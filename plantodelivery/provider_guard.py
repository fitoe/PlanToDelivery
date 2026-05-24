from __future__ import annotations

import json
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

from .kanban_runtime import TASK_SCHEMA, KanbanContractError, validate_active_slice_digest


@dataclass(frozen=True)
class ProviderExecutionContext:
    task_id: str
    capability: str
    project_root: Path
    output_root: Path
    task_envelope_path: Path
    active_slice_digest_path: Path
    execution_permit_path: Path | None
    result_manifest_path: Path
    envelope: dict[str, Any]
    digest: dict[str, Any]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise KanbanContractError(f"required provider context file is missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KanbanContractError(f"invalid JSON in provider context file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise KanbanContractError(f"provider context file must contain a JSON object: {path}")
    return data


def _require_string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise KanbanContractError(f"{field} must be a non-empty string")
    return value


def _validate_task_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    for field in ["schema", "task_id", "capability", "project_root", "active_slice", "output_root"]:
        if field not in envelope:
            raise KanbanContractError(f"missing required fields: {field}")
    if envelope["schema"] != TASK_SCHEMA:
        raise KanbanContractError(f"unsupported task schema: {envelope['schema']}")
    _require_string(envelope, "task_id")
    _require_string(envelope, "capability")
    _require_string(envelope, "project_root")
    _require_string(envelope, "output_root")
    if not isinstance(envelope["active_slice"], dict) or not envelope["active_slice"]:
        raise KanbanContractError("active_slice must be a non-empty object")
    return envelope


def validate_provider_execution_context(
    *,
    task_envelope_path: str | Path,
    active_slice_digest_path: str | Path,
    expected_capability: str | None = None,
    hermes_backend: Any | None = None,
    require_running: bool = True,
    execution_permit_path: str | Path | None = None,
) -> ProviderExecutionContext:
    """Validate the bounded P2D provider execution context before provider work starts."""

    task_path = Path(task_envelope_path)
    digest_path = Path(active_slice_digest_path)
    envelope = _validate_task_envelope(_load_json(task_path))
    digest = validate_active_slice_digest(_load_json(digest_path))

    task_id = envelope["task_id"]
    capability = envelope["capability"]
    if expected_capability is not None and capability != expected_capability:
        raise KanbanContractError(f"expected capability {expected_capability!r}, got {capability!r}")
    if digest["task_id"] != task_id or digest["capability"] != capability:
        raise KanbanContractError("active-slice digest does not match task envelope")

    output_root = Path(envelope["output_root"])
    permit_path = Path(execution_permit_path) if execution_permit_path is not None else None
    if permit_path is not None:
        permit = _load_json(permit_path)
        schema = permit.get("schema")
        if schema is not None and schema != "p2d-execution-permit/v1":
            raise KanbanContractError(f"unsupported execution permit schema: {schema}")
        for field, expected in [("task_id", task_id), ("capability", capability)]:
            if field in permit and permit[field] != expected:
                raise KanbanContractError(f"execution permit {field} does not match task envelope")
    result_manifest_path = Path(digest.get("handoff", {}).get("result_manifest_path") or output_root / "result-manifest.json")
    if result_manifest_path != output_root / "result-manifest.json":
        raise KanbanContractError("digest result_manifest_path must point to output_root/result-manifest.json")

    if require_running:
        if hermes_backend is None:
            raise KanbanContractError("Hermes Kanban backend is required when require_running=True")
        card = hermes_backend.show_card(task_id)
        status = card.get("task", {}).get("status")
        if status != "running":
            raise KanbanContractError(f"provider task {task_id} must be running before execution; current status is {status!r}")

    return ProviderExecutionContext(
        task_id=task_id,
        capability=capability,
        project_root=Path(envelope["project_root"]),
        output_root=output_root,
        task_envelope_path=task_path,
        active_slice_digest_path=digest_path,
        execution_permit_path=permit_path,
        result_manifest_path=result_manifest_path,
        envelope=envelope,
        digest=digest,
    )


def _relative_posix_path(path: str | Path, project_root: Path) -> str:
    raw = Path(path)
    if raw.is_absolute():
        try:
            raw = raw.resolve().relative_to(project_root.resolve())
        except ValueError as exc:
            raise KanbanContractError(f"changed file is outside project_root: {path}") from exc
    parts = raw.parts
    if any(part in {"", ".", ".."} for part in parts):
        raise KanbanContractError(f"changed file must be a normalized relative path: {path}")
    return raw.as_posix()


def _side_effect_allows_path(rule: str, changed_file: str, *, output_root_rel: str) -> bool:
    normalized_rule = " ".join(rule.strip().split())
    if normalized_rule == "write output_root only":
        return changed_file == output_root_rel or changed_file.startswith(f"{output_root_rel}/")
    if not normalized_rule.startswith("write "):
        return False
    pattern = normalized_rule[len("write ") :].strip()
    if pattern == "output_root/**":
        pattern = f"{output_root_rel}/**"
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return changed_file == prefix or changed_file.startswith(f"{prefix}/")
    return fnmatchcase(changed_file, pattern)


def assert_provider_write_allowed(
    ctx: ProviderExecutionContext,
    changed_files: list[str | Path],
    *,
    review_required: bool | None = None,
) -> None:
    """Reject provider side effects that are outside the task's declared write scope."""

    if not changed_files:
        raise KanbanContractError("prewrite guard requires at least one changed file")
    side_effects = ctx.envelope.get("allowed_side_effects")
    if not isinstance(side_effects, list) or not all(isinstance(item, str) and item.strip() for item in side_effects):
        raise KanbanContractError("task envelope must declare allowed_side_effects before provider writes")
    output_root_rel = _relative_posix_path(ctx.output_root, ctx.project_root)
    for changed in changed_files:
        changed_rel = _relative_posix_path(changed, ctx.project_root)
        if not any(_side_effect_allows_path(rule, changed_rel, output_root_rel=output_root_rel) for rule in side_effects):
            raise KanbanContractError(f"changed file is not permitted by allowed_side_effects: {changed_rel}")

    if review_required is True:
        review_policy = ctx.envelope.get("review_policy")
        if review_policy is not None and not isinstance(review_policy, dict):
            raise KanbanContractError("review_policy must be an object when review is required")
