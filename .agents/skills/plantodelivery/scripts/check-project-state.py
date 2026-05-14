#!/usr/bin/env python3
"""Validate portable project-state execution progress and artifact manifest."""
from __future__ import annotations
import json, sys
from pathlib import Path

TASK_DONE = {"completed", "skipped"}
TASK_REF_DONE = {"completed", "skipped"}  # waived is represented by gate/verification/commit statuses, not task_status
RESOLVED_BLOCKER = {"resolved", "waived"}
PASSED_GATE = {"passed", "waived"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot parse {path}: {exc}")


def try_schema(data, schema_path: Path, label: str, errors: list[str], warnings: list[str]):
    if not schema_path.exists():
        errors.append(f"missing schema: {schema_path}")
        return
    try:
        import jsonschema  # type: ignore
    except Exception:
        warnings.append("jsonschema not installed; using structural validation only")
        return
    schema = load_json(schema_path)
    try:
        jsonschema.validate(data, schema)
    except Exception as exc:
        errors.append(f"{label} schema validation failed: {exc}")


def main() -> int:
    root = Path.cwd()
    ps = root / "project-state"
    progress_path = ps / "execution-progress.json"
    progress_schema = ps / "execution-progress.schema.json"
    manifest_path = ps / "artifact-manifest.json"
    manifest_schema = ps / "artifact-manifest.schema.json"

    errors: list[str] = []
    warnings: list[str] = []
    for p in [progress_path, progress_schema, manifest_path, manifest_schema]:
        if not p.exists():
            errors.append(f"missing required file: {p}")
    if errors:
        for e in errors: print(e)
        return 1

    progress = load_json(progress_path)
    manifest = load_json(manifest_path)
    try_schema(progress, progress_schema, "execution-progress", errors, warnings)
    try_schema(manifest, manifest_schema, "artifact-manifest", errors, warnings)

    if progress.get("schema_version") != "1.0.0":
        errors.append("execution-progress schema_version must be 1.0.0")
    if manifest.get("schema_version") != "1.0.0":
        errors.append("artifact-manifest schema_version must be 1.0.0")

    tasks = {t.get("id"): t for t in progress.get("tasks", []) if t.get("id")}
    gates = {g.get("id"): g for g in progress.get("gates", []) if g.get("id")}
    blockers = {b.get("id"): b for b in progress.get("blockers", []) if b.get("id")}
    artifacts = {a.get("id"): a for a in manifest.get("artifacts", []) if a.get("id")}

    def require_task(ref, where):
        if ref is not None and ref not in tasks:
            errors.append(f"{where} references missing task: {ref}")
    def require_gate(ref, where):
        if ref not in gates:
            errors.append(f"{where} references missing gate: {ref}")
    def require_blocker(ref, where):
        if ref not in blockers:
            errors.append(f"{where} references missing blocker: {ref}")
    def require_artifact(ref, where):
        if ref not in artifacts:
            errors.append(f"{where} references missing artifact: {ref}")

    current = progress.get("current", {})
    require_task(current.get("task_id"), "current.task_id")
    require_task(current.get("next_task_id"), "current.next_task_id")

    for tid, t in tasks.items():
        for dep in t.get("depends_on", []): require_task(dep, f"task {tid}.depends_on")
        for bid in t.get("blocked_by", []): require_blocker(bid, f"task {tid}.blocked_by")
        for gid in t.get("required_gates", []): require_gate(gid, f"task {tid}.required_gates")
        for aid in t.get("artifact_refs", []): require_artifact(aid, f"task {tid}.artifact_refs")
        for aid in t.get("routing", {}).get("input_artifact_refs", []): require_artifact(aid, f"task {tid}.routing.input_artifact_refs")
        if t.get("task_status") == "blocked" and not t.get("blocked_by"):
            errors.append(f"blocked task {tid} has no blocked_by refs")
        if t.get("task_status") == "completed" and t.get("verification_status") in {"failed", "running"}:
            errors.append(f"completed task {tid} has inconsistent verification_status={t.get('verification_status')}")
        if t.get("task_status") == "completed":
            for f in t.get("expected_files", []):
                if not (root / f).exists():
                    errors.append(f"completed task {tid} expected file missing: {f}")

    for gid, g in gates.items():
        for aid in g.get("required_artifact_refs", []): require_artifact(aid, f"gate {gid}.required_artifact_refs")
        for bid in g.get("blocked_by", []): require_blocker(bid, f"gate {gid}.blocked_by")
        if g.get("status") == "passed":
            for aid in g.get("required_artifact_refs", []):
                a = artifacts.get(aid)
                if a and a.get("status") in {"missing", "stale", "rejected"}:
                    errors.append(f"passed gate {gid} requires non-ready artifact {aid} status={a.get('status')}")

    for bid, b in blockers.items():
        for tid in b.get("unblocks_task_ids", []): require_task(tid, f"blocker {bid}.unblocks_task_ids")

    for cp in progress.get("checkpoints", []):
        cid = cp.get("id", "<unknown>")
        for tid in cp.get("task_refs", []): require_task(tid, f"checkpoint {cid}.task_refs")
        for aid in cp.get("artifact_refs", []): require_artifact(aid, f"checkpoint {cid}.artifact_refs")

    for aid, a in artifacts.items():
        status = a.get("status")
        path = a.get("path")
        if path and status not in {"draft", "missing"} and not (root / path).exists():
            warnings.append(f"artifact {aid} path does not exist yet: {path}")
        for ref in a.get("source_refs", []): require_artifact(ref, f"artifact {aid}.source_refs")
        for ref in a.get("evidence_refs", []): require_artifact(ref, f"artifact {aid}.evidence_refs")

    if current.get("task_id") in tasks:
        ct = tasks[current["task_id"]]
        if ct.get("task_status") not in {"in_progress", "ready", "pending"} and not current.get("next_task_id"):
            unresolved = [b for b in blockers.values() if b.get("status") not in RESOLVED_BLOCKER]
            if not unresolved:
                warnings.append("current task is not continueable and no next_task_id/unresolved blocker is present")

    for w in warnings: print(f"WARNING: {w}")
    for e in errors: print(f"ERROR: {e}")
    if errors:
        print(f"project-state validation failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"project-state validation passed: {len(tasks)} task(s), {len(gates)} gate(s), {len(blockers)} blocker(s), {len(artifacts)} artifact(s), {len(warnings)} warning(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
