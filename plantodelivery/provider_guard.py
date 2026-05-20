from __future__ import annotations

import json
from dataclasses import dataclass
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
        result_manifest_path=result_manifest_path,
        envelope=envelope,
        digest=digest,
    )
