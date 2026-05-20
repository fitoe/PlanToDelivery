from __future__ import annotations

import json
import sqlite3
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
class KanbanEvent:
    task_id: str
    gate_status: str
    display_status: str
    action: str

class KanbanStateStore:
    """Canonical PlanToDelivery Kanban state source.

    The state index is the source of truth for tasks, gates, visible cards,
    and events. Task/result JSON files remain artifact evidence referenced by
    the canonical Kanban state.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.tasks_root = self.root / "tasks"
        self.index_path = self.root / "kanban-state.json"

    def load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"schema": STATE_SCHEMA, "tasks": {}, "gates": {}, "cards": {}, "events": []}
        index = _load_json(self.index_path)
        if index.get("schema") != STATE_SCHEMA:
            raise KanbanContractError(f"unsupported state schema: {index.get('schema')}")
        index.setdefault("tasks", {})
        index.setdefault("gates", {})
        index.setdefault("cards", {})
        index.setdefault("events", [])
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
            "display_status": display_gate_status("dispatched"),
        }
        self._sync_card(index, task_id, action="dispatch")
        self._rebuild_gates(index)
        self._write_index(index)
        return task_path

    def load_task(self, task_id: str) -> dict[str, Any]:
        return _load_json(self.tasks_root / task_id / "task-envelope.json")

    def find_next_ready_task(self) -> dict[str, Any] | None:
        tasks = self.load_index().get("tasks", {})
        for task_id, task in sorted(tasks.items()):
            if task.get("gate_status") == "ready" and _dependencies_completed(task, tasks):
                return dict(task)
        return None

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
                "display_status": display_gate_status(decide_gate_status(validated)),
            }
        )
        self._sync_card(index, task_id, action="ingest_result")
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
        task_entry["display_status"] = display_gate_status("completed")
        task_entry["review"] = {"status": "approved", "evidence": list(evidence)}
        self._sync_card(index, task_id, action="approve_review")
        self._rebuild_gates(index)
        self._write_index(index)

    def _write_index(self, index: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        _write_json(self.index_path, index)

    @staticmethod
    def _sync_card(index: dict[str, Any], task_id: str, *, action: str) -> None:
        task = index["tasks"][task_id]
        gate_status = task.get("gate_status", "dispatched")
        task["display_status"] = display_gate_status(gate_status)
        card = dict(index.setdefault("cards", {}).get(task_id, {}))
        card.update(task)
        card["display_status"] = task["display_status"]
        index["cards"][task_id] = card
        index.setdefault("events", []).append(
            {
                "task_id": task_id,
                "gate_status": gate_status,
                "display_status": task["display_status"],
                "action": action,
            }
        )

    @staticmethod
    def _rebuild_gates(index: dict[str, Any]) -> None:
        gates: dict[str, list[str]] = {}
        for task_id, task in sorted(index.get("tasks", {}).items()):
            gate_status = task.get("gate_status")
            if gate_status:
                gates.setdefault(gate_status, []).append(task_id)
        index["gates"] = gates


class KanbanSQLiteStateStore(KanbanStateStore):
    """SQLite-backed canonical PlanToDelivery Kanban state source.

    Task/result JSON files remain artifact evidence. SQLite is the source of
    truth for task, gate, card, review, and event recovery; JSON index export is
    available only as debug/evidence output.
    """

    def __init__(self, root: str | Path, db_path: str | Path | None = None) -> None:
        super().__init__(root)
        self.db_path = Path(db_path) if db_path is not None else self.root / "kanban-state.sqlite3"
        self.root.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists kanban_tasks (
                    task_id text primary key,
                    capability text not null,
                    provider text,
                    task_path text,
                    result_path text,
                    result text,
                    gate_status text not null,
                    display_status text not null,
                    task_json text,
                    result_json text,
                    review_json text
                );
                create table if not exists kanban_cards (
                    task_id text primary key,
                    gate_status text not null,
                    display_status text not null,
                    card_json text not null
                );
                create table if not exists kanban_events (
                    id integer primary key autoincrement,
                    task_id text not null,
                    gate_status text not null,
                    display_status text not null,
                    action text not null
                );
                create table if not exists kanban_artifacts (
                    id integer primary key autoincrement,
                    task_id text not null,
                    artifact_type text not null,
                    path text not null
                );
                create table if not exists kanban_reviews (
                    task_id text primary key,
                    status text not null,
                    evidence_json text not null
                );
                """
            )

    def load_index(self) -> dict[str, Any]:
        self._init_db()
        with self._connect() as conn:
            task_rows = conn.execute("select * from kanban_tasks order by task_id").fetchall()
            card_rows = conn.execute("select * from kanban_cards order by task_id").fetchall()
            event_rows = conn.execute("select task_id, gate_status, display_status, action from kanban_events order by id").fetchall()
        tasks = {row["task_id"]: json.loads(row["task_json"] or "{}") for row in task_rows}
        cards = {row["task_id"]: json.loads(row["card_json"]) for row in card_rows}
        index = {
            "schema": STATE_SCHEMA,
            "tasks": tasks,
            "gates": {},
            "cards": cards,
            "events": [dict(row) for row in event_rows],
        }
        self._rebuild_gates(index)
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

        task_entry = {
            "task_id": task_id,
            "capability": envelope["capability"],
            "task_path": str(task_path),
            "result_path": None,
            "result": None,
            "gate_status": "dispatched",
            "display_status": display_gate_status("dispatched"),
        }
        self._upsert_task(task_entry, envelope=envelope, result_manifest=None)
        self._sync_card_db(task_id, task_entry, action="dispatch")
        self._record_artifact(task_id, "task_envelope", task_path)
        return task_path

    def record_result(self, manifest: dict[str, Any]) -> Path:
        validated = validate_result_manifest(manifest)
        task_id = validated["task_id"]
        task_dir = self.tasks_root / task_id
        if not task_dir.exists():
            raise KanbanContractError(f"cannot record result for unknown task: {task_id}")
        result_path = task_dir / "result-manifest.json"
        _write_json(result_path, validated)

        index = self.load_index()
        existing = index["tasks"].get(
            task_id,
            {
                "task_id": task_id,
                "capability": validated["capability"],
                "task_path": str(task_dir / "task-envelope.json"),
            },
        )
        gate_status = decide_gate_status(validated)
        existing.update(
            {
                "capability": validated["capability"],
                "provider": validated["provider"],
                "result_path": str(result_path),
                "result": validated["result"],
                "gate_status": gate_status,
                "display_status": display_gate_status(gate_status),
                "suggested_gate_updates": list(validated.get("suggested_gate_updates") or []),
                "next_recommended_task": validated.get("next_recommended_task"),
            }
        )
        self._upsert_task(existing, envelope=None, result_manifest=validated)
        self._apply_provider_recommendations(validated)
        self._sync_card_db(task_id, existing, action="ingest_result")
        self._record_artifact(task_id, "result_manifest", result_path)
        return result_path

    def approve_review(self, task_id: str, evidence: list[str]) -> None:
        index = self.load_index()
        task_entry = index["tasks"].get(task_id)
        if task_entry is None:
            raise KanbanContractError(f"unknown task: {task_id}")
        if task_entry.get("gate_status") != "review":
            raise KanbanContractError(f"task is not in review: {task_id}")
        task_entry["gate_status"] = "completed"
        task_entry["display_status"] = display_gate_status("completed")
        task_entry["review"] = {"status": "approved", "evidence": list(evidence)}
        self._upsert_task(task_entry, envelope=None, result_manifest=None)
        with self._connect() as conn:
            conn.execute(
                "insert or replace into kanban_reviews(task_id, status, evidence_json) values (?, ?, ?)",
                (task_id, "approved", json.dumps(list(evidence), ensure_ascii=False)),
            )
        self._sync_card_db(task_id, task_entry, action="approve_review")

    def export_index(self) -> Path:
        self._write_index(self.load_index())
        return self.index_path

    def _upsert_task(self, task_entry: dict[str, Any], *, envelope: dict[str, Any] | None, result_manifest: dict[str, Any] | None) -> None:
        with self._connect() as conn:
            existing = conn.execute("select task_json, result_json from kanban_tasks where task_id = ?", (task_entry["task_id"],)).fetchone()
            result_json = json.dumps(result_manifest, ensure_ascii=False) if result_manifest is not None else (existing["result_json"] if existing else None)
            conn.execute(
                """
                insert or replace into kanban_tasks(
                    task_id, capability, provider, task_path, result_path, result,
                    gate_status, display_status, task_json, result_json, review_json
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_entry["task_id"],
                    task_entry["capability"],
                    task_entry.get("provider"),
                    task_entry.get("task_path"),
                    task_entry.get("result_path"),
                    task_entry.get("result"),
                    task_entry["gate_status"],
                    task_entry["display_status"],
                    json.dumps(task_entry, ensure_ascii=False),
                    result_json,
                    json.dumps(task_entry.get("review"), ensure_ascii=False) if task_entry.get("review") else None,
                ),
            )

    def _sync_card_db(self, task_id: str, task_entry: dict[str, Any], *, action: str) -> None:
        gate_status = task_entry.get("gate_status", "dispatched")
        task_entry["display_status"] = display_gate_status(gate_status)
        card = dict(self.load_index().get("cards", {}).get(task_id, {}))
        card.update(task_entry)
        card["display_status"] = task_entry["display_status"]
        with self._connect() as conn:
            conn.execute(
                "insert or replace into kanban_cards(task_id, gate_status, display_status, card_json) values (?, ?, ?, ?)",
                (task_id, gate_status, task_entry["display_status"], json.dumps(card, ensure_ascii=False)),
            )
            conn.execute(
                "insert into kanban_events(task_id, gate_status, display_status, action) values (?, ?, ?, ?)",
                (task_id, gate_status, task_entry["display_status"], action),
            )

    def _apply_provider_recommendations(self, manifest: dict[str, Any]) -> None:
        for update in manifest.get("suggested_gate_updates") or []:
            if not isinstance(update, dict):
                raise KanbanContractError("suggested_gate_updates entries must be objects")
            _require_fields(update, {"task_id", "gate_status"})
            gate_status = update["gate_status"]
            if not isinstance(gate_status, str) or not gate_status:
                raise KanbanContractError("suggested gate_status must be a non-empty string")
            task_id = update["task_id"]
            if not isinstance(task_id, str) or not task_id:
                raise KanbanContractError("suggested task_id must be a non-empty string")
            task_entry = self.load_index().get("tasks", {}).get(task_id, {"task_id": task_id})
            task_entry.update({k: v for k, v in update.items() if k not in {"reason"}})
            task_entry.setdefault("capability", update.get("capability") or "")
            task_entry["gate_status"] = gate_status
            task_entry["display_status"] = display_gate_status(gate_status)
            if "reason" in update:
                task_entry["gate_reason"] = update["reason"]
            self._upsert_task(task_entry, envelope=None, result_manifest=None)
            self._sync_card_db(task_id, task_entry, action="suggested_gate_update")

        next_task = manifest.get("next_recommended_task")
        if next_task is None:
            return
        if not isinstance(next_task, dict):
            raise KanbanContractError("next_recommended_task must be an object or null")
        _require_fields(next_task, {"task_id", "capability"})
        task_id = next_task["task_id"]
        if not isinstance(task_id, str) or not task_id:
            raise KanbanContractError("next_recommended_task.task_id must be a non-empty string")
        task_entry = self.load_index().get("tasks", {}).get(task_id, {"task_id": task_id})
        task_entry.update(next_task)
        task_entry.setdefault("depends_on", [manifest["task_id"]])
        task_entry.setdefault("gate_status", "ready")
        task_entry["display_status"] = display_gate_status(task_entry["gate_status"])
        self._upsert_task(task_entry, envelope=None, result_manifest=None)
        self._sync_card_db(task_id, task_entry, action="next_recommended_task")

    def _record_artifact(self, task_id: str, artifact_type: str, path: Path) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into kanban_artifacts(task_id, artifact_type, path) values (?, ?, ?)",
                (task_id, artifact_type, str(path)),
            )

class KanbanOrchestrator:
    """Minimal PlanToDelivery orchestration API over registry + state store."""

    def __init__(self, *, project_root: str | Path, providers_root: str | Path, state_root: str | Path | None = None, state_store: KanbanStateStore | None = None) -> None:
        self.project_root = Path(project_root)
        self.providers_root = Path(providers_root)
        self.store = state_store or KanbanStateStore(state_root or self.project_root / "project-state" / "kanban")

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
        return ReviewRecord(task_id=task_id, gate_status="completed", evidence=list(evidence))

    def dispatch_next_ready_task(self) -> DispatchRecord | None:
        task = self.store.find_next_ready_task()
        if task is None:
            return None
        required_fields = {
            "task_id",
            "capability",
            "active_slice",
            "input_artifact_refs",
            "expected_outputs",
            "verification_expectations",
            "allowed_side_effects",
        }
        _require_fields(task, required_fields)
        return self.dispatch_task(
            task_id=task["task_id"],
            capability=task["capability"],
            active_slice=task["active_slice"],
            input_artifact_refs=list(task["input_artifact_refs"]),
            expected_outputs=list(task["expected_outputs"]),
            verification_expectations=list(task["verification_expectations"]),
            allowed_side_effects=list(task["allowed_side_effects"]),
        )


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


def _dependencies_completed(task: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> bool:
    depends_on = task.get("depends_on") or []
    if not isinstance(depends_on, list):
        raise KanbanContractError("depends_on must be a list")
    for dependency_id in depends_on:
        if not isinstance(dependency_id, str) or not dependency_id:
            raise KanbanContractError("depends_on entries must be non-empty strings")
        dependency = tasks.get(dependency_id)
        if dependency is None or dependency.get("gate_status") != "completed":
            return False
    return True


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


def _normalize_provider_manifest(manifest_path: Path, target_path: Path) -> tuple[str, Path]:
    manifest = _load_json(manifest_path)
    if manifest.get("schema") == PROVIDER_SCHEMA and "provider" in manifest:
        provider = manifest["provider"]
        _write_json(target_path, manifest)
        return provider, target_path

    if manifest.get("schema_version") != PROVIDER_SCHEMA:
        raise KanbanContractError(f"unsupported provider schema in {manifest_path}: {manifest.get('schema') or manifest.get('schema_version')}")
    _require_fields(manifest, {"provider_id", "capabilities"})
    capabilities = manifest["capabilities"]
    if not isinstance(capabilities, list):
        raise KanbanContractError(f"capabilities must be a list in {manifest_path}")
    normalized = {
        "schema": PROVIDER_SCHEMA,
        "provider": manifest["provider_id"],
        "display_name": manifest.get("display_name", manifest["provider_id"]),
        "version": manifest.get("version", "0.1.0"),
        "capabilities": [
            {
                "name": capability,
                "task_schema": TASK_SCHEMA,
                "result_schema": RESULT_SCHEMA,
            }
            for capability in capabilities
        ],
        "source_manifest_path": str(manifest_path),
    }
    _write_json(target_path, normalized)
    return normalized["provider"], target_path


def bootstrap_provider_registry_from_manifests(
    path: str | Path,
    *,
    provider_manifests: dict[str, str | Path],
) -> Path:
    """Create a provider-registry/v1 config from real provider manifests.

    Real provider kernels currently expose compact manifests with
    schema_version/provider_id/capabilities. The runtime registry keeps a single
    contract shape (schema/provider/capability objects), so bootstrap writes
    normalized manifest snapshots next to the registry config and points the
    registry at those snapshots.
    """

    config_path = Path(path)
    normalized_root = config_path.parent / "provider-manifests"
    providers: dict[str, str | Path] = {}
    for provider_hint, source_path in sorted(provider_manifests.items()):
        source = Path(source_path)
        target = normalized_root / provider_hint / "provider-manifest.json"
        provider, normalized_path = _normalize_provider_manifest(source, target)
        providers[provider] = normalized_path
    return write_provider_registry_config(config_path, providers=providers)


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
