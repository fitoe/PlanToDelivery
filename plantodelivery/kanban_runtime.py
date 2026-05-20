from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TASK_SCHEMA = "kanban-capability-task/v1"
RESULT_SCHEMA = "kanban-capability-result/v1"
PROVIDER_SCHEMA = "provider-manifest/v1"
PROVIDER_REGISTRY_SCHEMA = "provider-registry/v1"
VALID_RESULTS = {"completed", "partial", "blocked", "failed"}
STATE_SCHEMA = "plantodelivery-kanban-state/v1"
DISPLAY_GATE_STATUSES = {
    "backlog": "待办",
    "ready": "待派发",
    "dispatched": "已派发",
    "running": "进行中",
    "review": "待审查",
    "blocked": "已阻塞",
    "partial": "部分完成",
    "completed": "已完成",
    "failed": "失败",
    "cancelled": "已取消",
}


class KanbanContractError(ValueError):
    """Raised when a Kanban provider contract artifact is invalid."""


@dataclass(frozen=True)
class ProviderCapability:
    provider: str
    capability: str
    manifest_path: Path
    task_schema: str = TASK_SCHEMA
    result_schema: str = RESULT_SCHEMA
    priority: int | None = None


@dataclass(frozen=True)
class DispatchRecord:
    provider: str
    capability: str
    envelope: dict[str, Any]
    task_path: Path
    output_root: Path


@dataclass(frozen=True)
class IngestRecord:
    task_id: str
    capability: str
    provider: str
    gate_status: str
    result_path: Path


@dataclass(frozen=True)
class ReviewRecord:
    task_id: str
    gate_status: str
    evidence: list[str]


@dataclass(frozen=True)
class BoardEvent:
    task_id: str
    gate_status: str
    display_status: str
    action: str


class InMemoryKanbanBoardAdapter:
    """Test/dry-run board adapter mirroring task state as visible Kanban cards."""

    def __init__(self) -> None:
        self.cards: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def upsert_card(self, task: dict[str, Any], *, action: str = "upsert") -> None:
        task_id = task["task_id"]
        gate_status = task.get("gate_status", "dispatched")
        card = dict(self.cards.get(task_id, {}))
        card.update(task)
        card["display_status"] = display_gate_status(gate_status)
        self.cards[task_id] = card
        self.events.append(
            {
                "task_id": task_id,
                "gate_status": gate_status,
                "display_status": card["display_status"],
                "action": action,
            }
        )


class KanbanStateStore:
    """Persist the minimal Javis Kanban task/result/gate state on disk."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.tasks_root = self.root / "tasks"
        self.index_path = self.root / "kanban-state.json"

    def load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"schema": STATE_SCHEMA, "tasks": {}, "gates": {}}
        index = _load_json(self.index_path)
        if index.get("schema") != STATE_SCHEMA:
            raise KanbanContractError(f"unsupported state schema: {index.get('schema')}")
        index.setdefault("tasks", {})
        index.setdefault("gates", {})
        return index

    def record_task(self, envelope: dict[str, Any]) -> Path:
        _require_fields(envelope, {"schema", "task_id", "capability", "output_root"})
        if envelope["schema"] != TASK_SCHEMA:
            raise KanbanContractError(f"unsupported task schema: {envelope['schema']}")
        task_id = envelope["task_id"]
        task_dir = self.tasks_root / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        task_path = task_dir / "task-envelope.json"
        _write_json(task_path, envelope)

        index = self.load_index()
        index["tasks"][task_id] = {
            "task_id": task_id,
            "capability": envelope["capability"],
            "task_path": str(task_path),
            "result_path": None,
            "result": None,
            "gate_status": "dispatched",
        }
        self._rebuild_gates(index)
        self._write_index(index)
        return task_path

    def load_task(self, task_id: str) -> dict[str, Any]:
        return _load_json(self.tasks_root / task_id / "task-envelope.json")

    def record_result(self, manifest: dict[str, Any]) -> Path:
        validated = validate_result_manifest(manifest)
        task_id = validated["task_id"]
        task_dir = self.tasks_root / task_id
        if not task_dir.exists():
            raise KanbanContractError(f"cannot record result for unknown task: {task_id}")
        result_path = task_dir / "result-manifest.json"
        _write_json(result_path, validated)

        index = self.load_index()
        task_entry = index["tasks"].setdefault(
            task_id,
            {
                "task_id": task_id,
                "capability": validated["capability"],
                "task_path": str(task_dir / "task-envelope.json"),
            },
        )
        task_entry.update(
            {
                "capability": validated["capability"],
                "provider": validated["provider"],
                "result_path": str(result_path),
                "result": validated["result"],
                "gate_status": decide_gate_status(validated),
            }
        )
        self._rebuild_gates(index)
        self._write_index(index)
        return result_path

    def load_result(self, task_id: str) -> dict[str, Any]:
        return _load_json(self.tasks_root / task_id / "result-manifest.json")

    def approve_review(self, task_id: str, evidence: list[str]) -> None:
        index = self.load_index()
        task_entry = index["tasks"].get(task_id)
        if task_entry is None:
            raise KanbanContractError(f"unknown task: {task_id}")
        if task_entry.get("gate_status") != "review":
            raise KanbanContractError(f"task is not in review: {task_id}")
        task_entry["gate_status"] = "completed"
        task_entry["review"] = {"status": "approved", "evidence": list(evidence)}
        self._rebuild_gates(index)
        self._write_index(index)

    def _write_index(self, index: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        _write_json(self.index_path, index)

    @staticmethod
    def _rebuild_gates(index: dict[str, Any]) -> None:
        gates: dict[str, list[str]] = {}
        for task_id, task in sorted(index.get("tasks", {}).items()):
            gate_status = task.get("gate_status")
            if gate_status:
                gates.setdefault(gate_status, []).append(task_id)
        index["gates"] = gates


class KanbanOrchestrator:
    """Minimal PlanToDelivery orchestration API over registry + state store."""

    def __init__(self, *, project_root: str | Path, providers_root: str | Path, state_root: str | Path | None = None, board: InMemoryKanbanBoardAdapter | None = None) -> None:
        self.project_root = Path(project_root)
        self.providers_root = Path(providers_root)
        self.store = KanbanStateStore(state_root or self.project_root / "project-state" / "kanban")
        self.board = board

    def dispatch_task(
        self,
        *,
        task_id: str,
        capability: str,
        active_slice: dict[str, Any],
        input_artifact_refs: list[str],
        expected_outputs: list[str],
        verification_expectations: list[str],
        allowed_side_effects: list[str],
    ) -> DispatchRecord:
        registry = load_provider_registry(self.providers_root)
        provider = registry.get(capability)
        if provider is None:
            raise KanbanContractError(f"no provider for capability: {capability}")
        output_root = self.store.tasks_root / task_id
        envelope = create_task_envelope(
            task_id=task_id,
            capability=capability,
            project_root=self.project_root,
            active_slice=active_slice,
            input_artifact_refs=input_artifact_refs,
            output_root=output_root,
            expected_outputs=expected_outputs,
            verification_expectations=verification_expectations,
            allowed_side_effects=allowed_side_effects,
        )
        task_path = self.store.record_task(envelope)
        if self.board is not None:
            self.board.upsert_card(self.store.load_index()["tasks"][task_id], action="dispatch")
        return DispatchRecord(
            provider=provider.provider,
            capability=capability,
            envelope=envelope,
            task_path=task_path,
            output_root=output_root,
        )

    def ingest_result(self, manifest: dict[str, Any]) -> IngestRecord:
        task_id = manifest.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise KanbanContractError("task_id is required")
        task = self.store.load_task(task_id)
        validated = validate_result_manifest(
            manifest,
            expected_task_id=task_id,
            expected_capability=task["capability"],
        )
        result_path = self.store.record_result(validated)
        if self.board is not None:
            self.board.upsert_card(self.store.load_index()["tasks"][task_id], action="ingest_result")
        return IngestRecord(
            task_id=task_id,
            capability=validated["capability"],
            provider=validated["provider"],
            gate_status=decide_gate_status(validated),
            result_path=result_path,
        )

    def ingest_result_path(self, result_path: str | Path) -> IngestRecord:
        return self.ingest_result(_load_json(Path(result_path)))

    def approve_review(self, task_id: str, *, evidence: list[str]) -> ReviewRecord:
        self.store.approve_review(task_id, evidence)
        if self.board is not None:
            self.board.upsert_card(self.store.load_index()["tasks"][task_id], action="approve_review")
        return ReviewRecord(task_id=task_id, gate_status="completed", evidence=list(evidence))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KanbanContractError(f"invalid json: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise KanbanContractError(f"manifest must be an object: {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _require_fields(data: dict[str, Any], fields: set[str]) -> None:
    missing = sorted(field for field in fields if field not in data)
    if missing:
        raise KanbanContractError(f"missing required fields: {', '.join(missing)}")


def display_gate_status(gate_status: str) -> str:
    return DISPLAY_GATE_STATUSES.get(gate_status, gate_status)


def load_provider_registry_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    config = _load_json(config_path)
    _require_fields(config, {"schema", "providers"})
    if config["schema"] != PROVIDER_REGISTRY_SCHEMA:
        raise KanbanContractError(f"unsupported provider registry schema: {config['schema']}")
    if not isinstance(config["providers"], dict):
        raise KanbanContractError("providers must be an object")
    for provider, entry in config["providers"].items():
        if not isinstance(entry, dict):
            raise KanbanContractError(f"provider entry must be an object: {provider}")
        _require_fields(entry, {"manifest_path"})
    return config


def write_provider_registry_config(path: str | Path, *, providers: dict[str, str | Path]) -> Path:
    config_path = Path(path)
    config = {
        "schema": PROVIDER_REGISTRY_SCHEMA,
        "providers": {
            provider: {"manifest_path": str(Path(manifest_path))}
            for provider, manifest_path in sorted(providers.items())
        },
    }
    _write_json(config_path, config)
    return config_path


def _provider_manifest_paths(root: Path) -> list[Path]:
    if root.is_file():
        config = load_provider_registry_config(root)
        return [Path(entry["manifest_path"]) for entry in config["providers"].values()]
    return sorted(root.rglob("provider-manifest.json"))


def load_provider_registry(root: str | Path) -> dict[str, ProviderCapability]:
    """Load provider manifests and index them by replaceable capability.

    Duplicate capabilities are rejected unless one entry has a lower numeric
    priority than the other. This keeps routing capability-first while making
    provider replacement explicit instead of hidden in import order.
    """

    root = Path(root)
    registry: dict[str, ProviderCapability] = {}
    for manifest_path in _provider_manifest_paths(root):
        manifest = _load_json(manifest_path)
        _require_fields(manifest, {"schema", "provider", "capabilities"})
        if manifest["schema"] != PROVIDER_SCHEMA:
            raise KanbanContractError(f"unsupported provider schema in {manifest_path}: {manifest['schema']}")
        provider = manifest["provider"]
        capabilities = manifest["capabilities"]
        if not isinstance(capabilities, list):
            raise KanbanContractError(f"capabilities must be a list in {manifest_path}")
        for item in capabilities:
            if not isinstance(item, dict):
                raise KanbanContractError(f"capability entry must be an object in {manifest_path}")
            _require_fields(item, {"name"})
            capability = item["name"]
            entry = ProviderCapability(
                provider=provider,
                capability=capability,
                manifest_path=manifest_path,
                task_schema=item.get("task_schema", TASK_SCHEMA),
                result_schema=item.get("result_schema", RESULT_SCHEMA),
                priority=item.get("priority", manifest.get("priority")),
            )
            existing = registry.get(capability)
            if existing is None:
                registry[capability] = entry
                continue
            if existing.priority is None and entry.priority is None:
                raise KanbanContractError(
                    f"duplicate capability without priority: {capability} ({existing.provider}, {entry.provider})"
                )
            if entry.priority is None:
                continue
            if existing.priority is None or entry.priority < existing.priority:
                registry[capability] = entry
    return registry


def create_task_envelope(
    *,
    task_id: str,
    capability: str,
    project_root: str | Path,
    active_slice: dict[str, Any],
    input_artifact_refs: list[str],
    output_root: str | Path,
    expected_outputs: list[str],
    verification_expectations: list[str],
    allowed_side_effects: list[str],
    review_policy: dict[str, Any] | None = None,
    blocking_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not task_id:
        raise KanbanContractError("task_id is required")
    if not capability:
        raise KanbanContractError("capability is required")
    if not isinstance(active_slice, dict) or not active_slice:
        raise KanbanContractError("active_slice must be a non-empty object")
    return {
        "schema": TASK_SCHEMA,
        "task_id": task_id,
        "capability": capability,
        "project_root": str(Path(project_root)),
        "active_slice": active_slice,
        "input_artifact_refs": list(input_artifact_refs),
        "output_root": str(Path(output_root)),
        "expected_outputs": list(expected_outputs),
        "verification_expectations": list(verification_expectations),
        "allowed_side_effects": list(allowed_side_effects),
        "review_policy": {
            "route_review_required_to": "review",
            **(review_policy or {}),
        },
        "blocking_policy": {
            "blocked_only_for_missing_or_unsafe_input": True,
            **(blocking_policy or {}),
        },
    }


def write_fixture_provider_result(
    *,
    task_envelope_path: str | Path,
    provider: str,
    result: str = "completed",
    review_required: bool = True,
    changed_files: list[str] | None = None,
    produced_artifacts: list[str] | None = None,
    evidence: list[str] | None = None,
    blockers: list[str] | None = None,
    debts: list[str] | None = None,
    suggested_gate_updates: list[dict[str, Any]] | None = None,
    next_recommended_task: dict[str, Any] | None = None,
) -> Path:
    envelope = _load_json(Path(task_envelope_path))
    _require_fields(envelope, {"task_id", "capability", "output_root"})
    output_root = Path(envelope["output_root"])
    manifest = {
        "schema": RESULT_SCHEMA,
        "task_id": envelope["task_id"],
        "capability": envelope["capability"],
        "provider": provider,
        "result": result,
        "changed_files": list(changed_files or []),
        "produced_artifacts": list(produced_artifacts or []),
        "evidence": list(evidence or []),
        "blockers": list(blockers or []),
        "debts": list(debts or []),
        "review_required": review_required,
        "suggested_gate_updates": list(suggested_gate_updates or []),
        "next_recommended_task": next_recommended_task,
    }
    validate_result_manifest(
        manifest,
        expected_task_id=envelope["task_id"],
        expected_capability=envelope["capability"],
    )
    result_path = output_root / "result-manifest.json"
    _write_json(result_path, manifest)
    return result_path


def validate_result_manifest(
    manifest: dict[str, Any],
    *,
    expected_task_id: str | None = None,
    expected_capability: str | None = None,
) -> dict[str, Any]:
    required = {
        "schema",
        "task_id",
        "capability",
        "provider",
        "result",
        "changed_files",
        "produced_artifacts",
        "evidence",
        "blockers",
        "debts",
        "review_required",
        "suggested_gate_updates",
        "next_recommended_task",
    }
    _require_fields(manifest, required)
    if manifest["schema"] != RESULT_SCHEMA:
        raise KanbanContractError(f"unsupported result schema: {manifest['schema']}")
    if expected_task_id is not None and manifest["task_id"] != expected_task_id:
        raise KanbanContractError(f"task_id mismatch: expected {expected_task_id}, got {manifest['task_id']}")
    if expected_capability is not None and manifest["capability"] != expected_capability:
        raise KanbanContractError(
            f"capability mismatch: expected {expected_capability}, got {manifest['capability']}"
        )
    if manifest["result"] not in VALID_RESULTS:
        raise KanbanContractError(f"invalid result: {manifest['result']}")
    for list_field in ["changed_files", "produced_artifacts", "evidence", "blockers", "debts", "suggested_gate_updates"]:
        if not isinstance(manifest[list_field], list):
            raise KanbanContractError(f"{list_field} must be a list")
    if not isinstance(manifest["review_required"], bool):
        raise KanbanContractError("review_required must be a boolean")
    return manifest


def decide_gate_status(result_manifest: dict[str, Any]) -> str:
    """Convert a provider result recommendation into Javis gate state."""

    result = result_manifest.get("result")
    blockers = result_manifest.get("blockers") or []
    if result == "blocked":
        return "blocked"
    if blockers:
        return "blocked"
    if result_manifest.get("review_required"):
        return "review"
    if result in VALID_RESULTS:
        return result
    raise KanbanContractError(f"invalid result: {result}")
