#!/usr/bin/env python3
"""Validate portable project-state execution progress and artifact manifest."""
from __future__ import annotations
import json, sys
from pathlib import Path

TASK_DONE = {"completed", "skipped"}
RESOLVED_BLOCKER = {"resolved", "waived"}
PASSED_CONSTRAINT = {"passed", "waived"}
CONTINUEABLE = {"in_progress", "ready", "pending", "needs_rework"}
ELIGIBLE = {"ready", "pending", "needs_rework"}
BLOCKING_CONFIRMATION = {"required", "requested", "changes_requested"}
EXECUTION_STAGES = {"execution", "debugging", "verification", "handoff", "done"}
UI_FIDELITY = {"visual_shell", "high_fidelity", "strict_parity"}
VISUAL_ARTIFACT_KINDS = {"visual_source", "visual_source_contract", "implementation_blueprint", "page_matrix", "component_blueprint", "visual_ir", "parity_report", "screenshot_evidence"}
READY_ARTIFACT_STATUS = {"ready", "approved", "consumed"}


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
    constraints = {c.get("id"): c for c in progress.get("kanban_constraints", []) if c.get("id")}
    blockers = {b.get("id"): b for b in progress.get("blockers", []) if b.get("id")}
    artifacts = {a.get("id"): a for a in manifest.get("artifacts", []) if a.get("id")}

    def require_task(ref, where):
        if ref is not None and ref not in tasks:
            errors.append(f"{where} references missing task: {ref}")
    def require_constraint(ref, where):
        if ref not in constraints:
            errors.append(f"{where} references missing Kanban constraint: {ref}")
    def require_blocker(ref, where):
        if ref not in blockers:
            errors.append(f"{where} references missing blocker: {ref}")
    def require_artifact(ref, where):
        if ref not in artifacts:
            errors.append(f"{where} references missing artifact: {ref}")

    current = progress.get("current", {})
    current_stage = current.get("stage")
    current_task_id = current.get("task_id")
    next_task_id = current.get("next_task_id")
    require_task(current_task_id, "current.task_id")
    require_task(next_task_id, "current.next_task_id")

    for tid, t in tasks.items():
        for dep in t.get("depends_on", []): require_task(dep, f"task {tid}.depends_on")
        for bid in t.get("blocked_by", []): require_blocker(bid, f"task {tid}.blocked_by")
        for gid in t.get("required_kanban_dependencies", []): require_constraint(gid, f"task {tid}.required_kanban_dependencies")
        for aid in t.get("artifact_refs", []): require_artifact(aid, f"task {tid}.artifact_refs")
        for aid in t.get("routing", {}).get("input_artifact_refs", []): require_artifact(aid, f"task {tid}.routing.input_artifact_refs")

        status = t.get("task_status")
        if status == "blocked" and not t.get("blocked_by"):
            errors.append(f"blocked task {tid} has no blocked_by refs")
        if status == "completed" and t.get("verification_status") in {"failed", "running", "not_started"}:
            errors.append(f"completed task {tid} has inconsistent verification_status={t.get('verification_status')}")
        if status == "completed" and t.get("user_confirmation_status") in BLOCKING_CONFIRMATION:
            errors.append(f"completed task {tid} still has blocking user_confirmation_status={t.get('user_confirmation_status')}")
        if status == "skipped" and not (t.get("waiver") or t.get("skip_reason") or any("waiver" in str(n).lower() for n in t.get("notes", []))):
            errors.append(f"skipped task {tid} requires waiver/skip_reason evidence")
        if status == "completed":
            for f in t.get("expected_files", []):
                if not (root / f).exists():
                    errors.append(f"completed task {tid} expected file missing: {f}")

        # Task-local Kanban dependency readiness for active/executable tasks.
        if status in {"in_progress", "completed"}:
            for gid in t.get("required_kanban_dependencies", []):
                c = constraints.get(gid)
                if c and c.get("status") not in PASSED_CONSTRAINT:
                    errors.append(f"task {tid} is {status} but required Kanban dependency {gid} status={c.get('status')}")
            for bid in t.get("blocked_by", []):
                b = blockers.get(bid)
                if b and b.get("status") not in RESOLVED_BLOCKER:
                    errors.append(f"task {tid} is {status} but blocker {bid} status={b.get('status')}")

        # UI final/completion guard: visual fidelity completion needs visual evidence.
        if status == "completed" and t.get("fidelity_target") in UI_FIDELITY:
            refs = list(t.get("artifact_refs", [])) + list(t.get("routing", {}).get("input_artifact_refs", []))
            visual_refs = [aid for aid in refs if artifacts.get(aid, {}).get("kind") in VISUAL_ARTIFACT_KINDS]
            if not visual_refs:
                errors.append(f"completed UI task {tid} fidelity_target={t.get('fidelity_target')} has no visual/parity artifact refs")

    for gid, c in constraints.items():
        for aid in c.get("required_artifact_refs", []): require_artifact(aid, f"Kanban constraint {gid}.required_artifact_refs")
        for bid in c.get("blocked_by", []): require_blocker(bid, f"Kanban constraint {gid}.blocked_by")
        if c.get("status") == "passed":
            if c.get("blocked_by"):
                unresolved = [bid for bid in c.get("blocked_by", []) if blockers.get(bid, {}).get("status") not in RESOLVED_BLOCKER]
                if unresolved:
                    errors.append(f"passed Kanban constraint {gid} still has unresolved blockers: {', '.join(unresolved)}")
            for aid in c.get("required_artifact_refs", []):
                a = artifacts.get(aid)
                if a and a.get("status") not in READY_ARTIFACT_STATUS:
                    errors.append(f"passed Kanban constraint {gid} requires non-ready artifact {aid} status={a.get('status')}")

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

    unresolved_blockers = [b for b in blockers.values() if b.get("status") not in RESOLVED_BLOCKER]

    if current_task_id in tasks:
        ct = tasks[current_task_id]
        if ct.get("task_status") not in CONTINUEABLE and not next_task_id:
            if not unresolved_blockers:
                warnings.append("current task is not continueable and no next_task_id/unresolved blocker is present")
        if ct.get("user_confirmation_status") in BLOCKING_CONFIRMATION:
            warnings.append(f"current task {current_task_id} is waiting on user confirmation; next action should resolve confirmation")

    # Execution-stage Kanban constraint guard. This catches the common accidental skip from intake/planning to execution.
    if current_stage in EXECUTION_STAGES:
        execution_constraints = [g for g in constraints.values() if current_stage in g.get("required_for_stages", []) or g.get("id") in {"execution-entry", "constraint-execution-entry"}]
        if not execution_constraints:
            errors.append(f"current.stage={current_stage} requires an execution-entry Kanban constraint in project-state.kanban_constraints")
        elif not any(c.get("status") in PASSED_CONSTRAINT for c in execution_constraints):
            statuses = ", ".join(f"{c.get('id')}={c.get('status')}" for c in execution_constraints)
            errors.append(f"current.stage={current_stage} has no passed/waived execution-entry Kanban constraint ({statuses})")

        if current_task_id:
            ct = tasks.get(current_task_id, {})
            if current_task_id and not ct.get("required_kanban_dependencies") and not execution_constraints:
                errors.append(f"execution current task {current_task_id} has no required_kanban_dependencies and no execution Kanban constraint exists")

    # Eligible next task sanity check.
    if next_task_id in tasks:
        nt = tasks[next_task_id]
        if nt.get("task_status") not in ELIGIBLE and nt.get("task_status") != "in_progress":
            warnings.append(f"next_task_id {next_task_id} status={nt.get('task_status')} is not normally eligible")
        for gid in nt.get("required_kanban_dependencies", []):
            c = constraints.get(gid)
            if c and c.get("status") not in PASSED_CONSTRAINT:
                warnings.append(f"next_task_id {next_task_id} waits for Kanban dependency {gid} status={c.get('status')}")
        for bid in nt.get("blocked_by", []):
            b = blockers.get(bid)
            if b and b.get("status") not in RESOLVED_BLOCKER:
                warnings.append(f"next_task_id {next_task_id} blocked by {bid} status={b.get('status')}")
        if nt.get("user_confirmation_status") in BLOCKING_CONFIRMATION:
            warnings.append(f"next_task_id {next_task_id} waits for user confirmation status={nt.get('user_confirmation_status')}")

    for w in warnings: print(f"WARNING: {w}")
    for e in errors: print(f"ERROR: {e}")
    if errors:
        print(f"project-state validation failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"project-state validation passed: {len(tasks)} task(s), {len(constraints)} Kanban constraint(s), {len(blockers)} blocker(s), {len(artifacts)} artifact(s), {len(warnings)} warning(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
