from __future__ import annotations

import base64
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TASK_SCHEMA = "kanban-capability-task/v1"
RESULT_SCHEMA = "kanban-capability-result/v1"
ACTIVE_SLICE_DIGEST_SCHEMA = "active-slice-digest/v1"
PROVIDER_SCHEMA = "provider-manifest/v1"
PROVIDER_REGISTRY_SCHEMA = "provider-registry/v1"
P2D_META_SCHEMA = "p2d-meta/v1"
P2D_META_BEGIN = "<!-- P2D_META"
P2D_META_END = "P2D_META -->"
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
class P2DMeta:
    task_id: str
    capability: str
    active_slice: dict[str, Any]
    provider: str | None = None
    output_root: str | None = None
    input_artifact_refs: list[str] | None = None
    expected_outputs: list[str] | None = None
    verification_expectations: list[str] | None = None
    allowed_side_effects: list[str] | None = None
    gate_status: str | None = None
    depends_on: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema": P2D_META_SCHEMA,
            "task_id": self.task_id,
            "capability": self.capability,
            "active_slice": dict(self.active_slice),
        }
        optional = {
            "provider": self.provider,
            "output_root": self.output_root,
            "input_artifact_refs": self.input_artifact_refs,
            "expected_outputs": self.expected_outputs,
            "verification_expectations": self.verification_expectations,
            "allowed_side_effects": self.allowed_side_effects,
            "gate_status": self.gate_status,
            "depends_on": self.depends_on,
        }
        for key, value in optional.items():
            if value is not None:
                data[key] = value
        return validate_p2d_meta(data).to_dict_raw()

    def to_dict_raw(self) -> dict[str, Any]:
        return {
            "schema": P2D_META_SCHEMA,
            "task_id": self.task_id,
            "capability": self.capability,
            "active_slice": dict(self.active_slice),
            **({"provider": self.provider} if self.provider is not None else {}),
            **({"output_root": self.output_root} if self.output_root is not None else {}),
            **({"input_artifact_refs": list(self.input_artifact_refs)} if self.input_artifact_refs is not None else {}),
            **({"expected_outputs": list(self.expected_outputs)} if self.expected_outputs is not None else {}),
            **({"verification_expectations": list(self.verification_expectations)} if self.verification_expectations is not None else {}),
            **({"allowed_side_effects": list(self.allowed_side_effects)} if self.allowed_side_effects is not None else {}),
            **({"gate_status": self.gate_status} if self.gate_status is not None else {}),
            **({"depends_on": list(self.depends_on)} if self.depends_on is not None else {}),
        }


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
    digest_path: Path | None = None


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
    """JSON artifact overlay for PlanToDelivery provider contracts.

    Hermes Kanban boards own canonical execution state. This store only writes
    task/result evidence and display-friendly overlay exports for migration,
    debugging, and provider handoff tests.
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
        digest_path = task_dir / "active-slice-digest.json"
        digest = build_active_slice_digest(envelope, task_path=task_path)
        _write_json(digest_path, digest)

        index = self.load_index()
        index["tasks"][task_id] = {
            "task_id": task_id,
            "capability": envelope["capability"],
            "task_path": str(task_path),
            "digest_path": str(digest_path),
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
        raise KanbanContractError("find_next_ready_task requires the Hermes Kanban board backend")

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
                "suggested_gate_updates": list(validated.get("suggested_gate_updates") or []),
                "next_recommended_task": validated.get("next_recommended_task"),
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
        self._record_dependency_unlock_events(index, completed_task_id=task_id)
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
    def _record_dependency_unlock_events(index: dict[str, Any], *, completed_task_id: str) -> None:
        tasks = index.get("tasks", {})
        events = index.setdefault("events", [])
        for task_id, task in sorted(tasks.items()):
            if task.get("gate_status") != "ready":
                continue
            if completed_task_id not in (task.get("depends_on") or []):
                continue
            if not _dependencies_completed(task, tasks):
                continue
            if _has_dependency_unlock_event(events, task_id=task_id):
                continue
            display_status = display_gate_status("ready")
            task["display_status"] = display_status
            events.append(
                {
                    "task_id": task_id,
                    "gate_status": "ready",
                    "display_status": display_status,
                    "action": "dependency_unlocked",
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



class HermesKanbanBackend(KanbanStateStore):
    """Hermes Kanban CLI-backed execution store with JSON artifact overlay."""

    def __init__(
        self,
        *,
        project_root: str | Path,
        state_root: str | Path | None = None,
        board: str = "plantodelivery",
        hermes_home: str | Path | None = None,
        hermes_cmd: list[str] | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        super().__init__(state_root or self.project_root / "project-state" / "kanban")
        self.board = board
        self.hermes_home = Path(hermes_home) if hermes_home is not None else None
        self.hermes_cmd = list(hermes_cmd or ["hermes"])
        self._ensure_board()

    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        if self.hermes_home is not None:
            env["HERMES_HOME"] = str(self.hermes_home)
        return env

    def _run(self, *args: str, json_output: bool = False) -> Any:
        proc = subprocess.run(
            [*self.hermes_cmd, "kanban", *args],
            cwd=str(self.project_root),
            env=self._env(),
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise KanbanContractError(
                f"hermes kanban {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
            )
        if json_output:
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError as exc:
                raise KanbanContractError(f"invalid hermes kanban JSON output: {exc}: {proc.stdout}") from exc
        return proc.stdout

    def _ensure_board(self) -> None:
        self._run("init")
        boards = self._run("boards", "list", "--json", json_output=True)
        if not any(item.get("slug") == self.board for item in boards):
            self._run("boards", "create", self.board, "--default-workdir", str(self.project_root))

    def _card_body(self, envelope: dict[str, Any]) -> str:
        meta = P2DMeta(
            task_id=envelope["task_id"],
            capability=envelope["capability"],
            active_slice=envelope["active_slice"],
            provider=envelope.get("provider_hint"),
            output_root=envelope["output_root"],
            input_artifact_refs=envelope.get("input_artifact_refs") or [],
            expected_outputs=envelope.get("expected_outputs") or [],
            verification_expectations=envelope.get("verification_expectations") or [],
            allowed_side_effects=envelope.get("allowed_side_effects") or [],
            depends_on=envelope.get("depends_on") or None,
        )
        body = (
            f"P2D capability: {envelope['capability']}\n"
            f"Output root: {envelope['output_root']}\n"
        )
        return append_p2d_meta_marker(body, meta)

    def record_task(self, envelope: dict[str, Any]) -> Path:
        _require_fields(envelope, {"schema", "task_id", "capability", "output_root"})
        if envelope["schema"] != TASK_SCHEMA:
            raise KanbanContractError(f"unsupported task schema: {envelope['schema']}")
        task_path = super().record_task(envelope)
        digest_path = self.tasks_root / envelope["task_id"] / "active-slice-digest.json"
        card_envelope = dict(envelope)
        card_envelope["input_artifact_refs"] = [
            *list(envelope.get("input_artifact_refs") or []),
            str(digest_path),
        ]
        created = self._run(
            "--board", self.board,
            "create", envelope["task_id"],
            "--body", self._card_body(card_envelope),
            "--assignee", envelope.get("provider_hint") or envelope["capability"],
            "--workspace", f"dir:{self.project_root}",
            "--created-by", "plantodelivery",
            "--initial-status", "running",
            "--idempotency-key", f"p2d:{envelope['task_id']}",
            "--json",
            json_output=True,
        )
        hermes_task_id = created.get("id")
        if not isinstance(hermes_task_id, str) or not hermes_task_id:
            raise KanbanContractError("hermes kanban create returned no task id")
        _write_json(self.tasks_root / envelope["task_id"] / "hermes-card.json", {"id": hermes_task_id})
        for parent in envelope.get("depends_on") or []:
            self._run("--board", self.board, "link", self._hermes_task_id(parent), hermes_task_id)
        return task_path

    def _hermes_task_id(self, task_id: str) -> str:
        mapping_path = self.tasks_root / task_id / "hermes-card.json"
        if mapping_path.exists():
            mapped = _load_json(mapping_path).get("id")
            if isinstance(mapped, str) and mapped:
                return mapped
        if task_id.startswith("t_"):
            return task_id
        return task_id

    def show_card(self, task_id: str) -> dict[str, Any]:
        return self._run("--board", self.board, "show", self._hermes_task_id(task_id), "--json", json_output=True)

    def load_task(self, task_id: str) -> dict[str, Any]:
        local_path = self.tasks_root / task_id / "task-envelope.json"
        if local_path.exists():
            return _load_json(local_path)
        card = self.show_card(task_id)
        task = card.get("task") or {}
        meta = extract_p2d_meta_marker(
            body=task.get("body"),
            comments=[comment.get("body", "") for comment in card.get("comments", [])],
        )
        if meta is None:
            raise KanbanContractError(f"task has no P2D_META marker: {task_id}")
        envelope = p2d_meta_to_task_envelope(meta, project_root=self.project_root)
        if meta.provider:
            envelope["provider_hint"] = meta.provider
        return envelope

    def claim_task(self, task_id: str, *, ttl_seconds: int | None = None) -> dict[str, Any]:
        args = ["--board", self.board, "claim", self._hermes_task_id(task_id)]
        if ttl_seconds is not None:
            args.extend(["--ttl", str(ttl_seconds)])
        self._run(*args)
        return self.show_card(task_id)["task"]

    def _p2d_task_status(self, task_id: str) -> str:
        card = self.show_card(task_id)
        task = card.get("task") or {}
        status = task.get("status")
        if not isinstance(status, str) or not status:
            raise KanbanContractError(f"cannot read Hermes task status: {task_id}")
        return status

    def _require_running(self, task_id: str, *, action: str) -> None:
        status = self._p2d_task_status(task_id)
        if status != "running":
            raise KanbanContractError(f"task must be claimed/running before {action}: {task_id} (status={status})")

    def _comment(self, task_id: str, text: str, *, author: str = "plantodelivery") -> None:
        self._run("--board", self.board, "comment", self._hermes_task_id(task_id), text, "--author", author)

    def record_result(self, manifest: dict[str, Any]) -> Path:
        validated = validate_result_manifest(manifest)
        task_id = validated["task_id"]
        self._require_running(task_id, action="ingest_result")
        result_path = super().record_result(validated)
        gate_status = decide_gate_status(validated)
        if gate_status == "blocked":
            reason = "; ".join(validated.get("blockers") or []) or validated["result"]
            self._run("--board", self.board, "block", self._hermes_task_id(task_id), reason)
        elif gate_status == "review":
            summary = json.dumps(validated, ensure_ascii=False, separators=(",", ":"))
            self._comment(task_id, f"P2D RESULT READY FOR REVIEW\n{summary}")
            self._run("--board", self.board, "block", self._hermes_task_id(task_id), "P2D review gate pending approval")
            index = self.load_index()
            task_entry = index["tasks"].get(task_id)
            if task_entry is not None:
                task_entry["gate_status"] = "review"
                task_entry["display_status"] = display_gate_status("review")
                self._sync_card(index, task_id, action="review_gate")
                self._rebuild_gates(index)
                self._write_index(index)
        else:
            summary = json.dumps(validated, ensure_ascii=False, separators=(",", ":"))
            self._run(
                "--board", self.board,
                "complete", self._hermes_task_id(task_id),
                "--result", validated["result"],
                "--summary", summary,
            )
        return result_path

    def approve_review(self, task_id: str, evidence: list[str]) -> None:
        if not evidence:
            raise KanbanContractError("review evidence is required")
        index = self.load_index()
        task_entry = index.get("tasks", {}).get(task_id)
        if task_entry is None:
            raise KanbanContractError(f"unknown task: {task_id}")
        if task_entry.get("gate_status") != "review":
            raise KanbanContractError(f"task is not in review: {task_id}")
        result = self.load_result(task_id)
        self._comment(task_id, "P2D REVIEW APPROVED\n" + json.dumps({"evidence": list(evidence)}, ensure_ascii=False))
        summary = json.dumps({"result_manifest": result, "review_evidence": list(evidence)}, ensure_ascii=False, separators=(",", ":"))
        self._run(
            "--board", self.board,
            "complete", self._hermes_task_id(task_id),
            "--result", result["result"],
            "--summary", summary,
        )
        super().approve_review(task_id, evidence)

    def audit_enforcement(self, *, strict_digest: bool = False) -> dict[str, Any]:
        raw_cards = self._run("--board", self.board, "list", "--json", json_output=True)
        cards = raw_cards.get("tasks", raw_cards) if isinstance(raw_cards, dict) else raw_cards
        if not isinstance(cards, list):
            raise KanbanContractError("unexpected Hermes Kanban list JSON shape")
        violations: list[dict[str, Any]] = []
        for item in cards:
            task = item.get("task", item) if isinstance(item, dict) else {}
            if not isinstance(task, dict):
                continue
            hermes_id = str(task.get("id") or "")
            title = str(task.get("title") or hermes_id)
            body = str(task.get("body") or "")
            comments = [str(comment.get("body") or "") for comment in item.get("comments", [])] if isinstance(item, dict) else []
            if not comments and hermes_id:
                try:
                    detail = self.show_card(hermes_id)
                    comments = [str(comment.get("body") or "") for comment in detail.get("comments", [])]
                except KanbanContractError:
                    comments = []
            try:
                meta = extract_p2d_meta_marker(body=body, comments=comments)
            except KanbanContractError as exc:
                violations.append({"task_id": title, "hermes_task_id": hermes_id, "code": "invalid_p2d_meta", "message": str(exc)})
                continue
            if meta is None:
                violations.append({"task_id": title, "hermes_task_id": hermes_id, "code": "missing_p2d_meta", "message": "card has no P2D_META marker"})
                continue
            if strict_digest:
                digest_path = self.tasks_root / meta.task_id / "active-slice-digest.json"
                if not digest_path.exists():
                    violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "missing_active_slice_digest", "message": "task has no active-slice-digest.json"})
                else:
                    try:
                        digest = validate_active_slice_digest(_load_json(digest_path))
                        if digest["task_id"] != meta.task_id or digest["capability"] != meta.capability:
                            violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "mismatched_active_slice_digest", "message": "digest task_id/capability does not match P2D_META"})
                    except KanbanContractError as exc:
                        violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "invalid_active_slice_digest", "message": str(exc)})
            result_path = self.tasks_root / meta.task_id / "result-manifest.json"
            status = task.get("status")
            if status == "done" and not result_path.exists():
                violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "done_without_result_manifest", "message": "done card has no local result-manifest.json"})
                continue
            if result_path.exists():
                result = _load_json(result_path)
                gate_status = decide_gate_status(validate_result_manifest(result, expected_task_id=meta.task_id, expected_capability=meta.capability))
                has_approval = any("P2D REVIEW APPROVED" in comment for comment in comments)
                if gate_status == "review" and status == "done" and not has_approval:
                    violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "missing_review_approval", "message": "review-required task is done without P2D REVIEW APPROVED comment"})
                if gate_status != "review" and status == "blocked" and result.get("result") != "blocked":
                    violations.append({"task_id": meta.task_id, "hermes_task_id": hermes_id, "code": "unexpected_blocked_status", "message": "card is blocked but result is not blocked/review"})
        return {"schema": "p2d-enforcement-audit/v1", "ok": not violations, "board": self.board, "violations": violations}


class KanbanOrchestrator:
    """Minimal PlanToDelivery orchestration API over registry + state store."""

    def __init__(
        self,
        *,
        project_root: str | Path,
        providers_root: str | Path,
        state_root: str | Path | None = None,
        state_store: KanbanStateStore | None = None,
        state_backend: str = "hermes",
        board: str = "plantodelivery",
    ) -> None:
        self.project_root = Path(project_root)
        self.providers_root = Path(providers_root)
        resolved_state_root = state_root or self.project_root / "project-state" / "kanban"
        if state_store is not None:
            self.store = state_store
        elif state_backend == "json":
            raise KanbanContractError('state_backend="json" is test/export only; real PlanToDelivery execution requires state_backend="hermes"')
        elif state_backend == "hermes":
            self.store = HermesKanbanBackend(project_root=self.project_root, state_root=resolved_state_root, board=board)
        else:
            raise KanbanContractError(f"unsupported state_backend: {state_backend}")

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
        if isinstance(self.store, HermesKanbanBackend):
            envelope["provider_hint"] = provider.provider
        task_path = self.store.record_task(envelope)
        task_entry = self.store.load_index()["tasks"].get(task_id, {})
        digest_path_raw = task_entry.get("digest_path")
        digest_path = Path(digest_path_raw) if isinstance(digest_path_raw, str) and digest_path_raw else None
        return DispatchRecord(
            provider=provider.provider,
            capability=capability,
            envelope=envelope,
            task_path=task_path,
            output_root=output_root,
            digest_path=digest_path,
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
        raise KanbanContractError("dispatch_next_ready_task requires the Hermes Kanban board backend")


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


def validate_active_slice_digest(digest: dict[str, Any]) -> dict[str, Any]:
    raw = dict(digest)
    _require_fields(raw, {"schema", "task_id", "capability", "active_slice", "context_budget", "read_first", "handoff"})
    if raw["schema"] != ACTIVE_SLICE_DIGEST_SCHEMA:
        raise KanbanContractError(f"unsupported active-slice digest schema: {raw['schema']}")
    for field in ["task_id", "capability"]:
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise KanbanContractError(f"{field} must be a non-empty string")
    if not isinstance(raw["active_slice"], dict) or not raw["active_slice"]:
        raise KanbanContractError("active_slice must be a non-empty object")
    if not isinstance(raw["context_budget"], dict):
        raise KanbanContractError("context_budget must be an object")
    if not isinstance(raw["read_first"], list) or not all(isinstance(item, str) for item in raw["read_first"]):
        raise KanbanContractError("read_first must be a list of strings")
    if not isinstance(raw["handoff"], dict):
        raise KanbanContractError("handoff must be an object")
    for field in ["input_artifact_refs", "expected_outputs", "verification_expectations", "allowed_side_effects", "stop_rules"]:
        if field in raw and (not isinstance(raw[field], list) or not all(isinstance(item, str) for item in raw[field])):
            raise KanbanContractError(f"{field} must be a list of strings")
    return raw


def build_active_slice_digest(
    envelope: dict[str, Any],
    *,
    task_path: str | Path | None = None,
    max_chars: int = 6000,
    stop_rules: list[str] | None = None,
) -> dict[str, Any]:
    _require_fields(envelope, {"schema", "task_id", "capability", "active_slice", "output_root"})
    if envelope["schema"] != TASK_SCHEMA:
        raise KanbanContractError(f"unsupported task schema: {envelope['schema']}")
    output_root = Path(envelope["output_root"])
    digest = {
        "schema": ACTIVE_SLICE_DIGEST_SCHEMA,
        "task_id": envelope["task_id"],
        "capability": envelope["capability"],
        "active_slice": dict(envelope["active_slice"]),
        "context_budget": {
            "max_chars": max_chars,
            "policy": "artifact-paths-over-inline-history",
        },
        "read_first": [str(Path(task_path))] if task_path is not None else [],
        "input_artifact_refs": list(envelope.get("input_artifact_refs") or []),
        "expected_outputs": list(envelope.get("expected_outputs") or []),
        "verification_expectations": list(envelope.get("verification_expectations") or []),
        "allowed_side_effects": list(envelope.get("allowed_side_effects") or []),
        "stop_rules": list(stop_rules or []),
        "handoff": {
            "provider_prompt": "Use this digest and referenced artifacts only; do not rely on prior chat history.",
            "result_manifest_path": str(output_root / "result-manifest.json"),
        },
    }
    validated = validate_active_slice_digest(digest)
    if len(json.dumps(validated, ensure_ascii=False)) > max_chars:
        raise KanbanContractError(f"active-slice digest exceeds max_chars: {max_chars}")
    return validated


def render_provider_handoff_prompt(digest_path: str | Path, task_path: str | Path) -> str:
    return (
        "Use the active-slice digest and task envelope below. "
        "Do not rely on prior chat history. Read referenced artifacts as needed.\n"
        f"- Active slice digest: {digest_path}\n"
        f"- Task envelope: {task_path}\n"
        "Return a kanban-capability-result/v1 manifest with evidence paths."
    )


def validate_p2d_meta(data: P2DMeta | dict[str, Any]) -> P2DMeta:
    raw = data.to_dict_raw() if isinstance(data, P2DMeta) else dict(data)
    _require_fields(raw, {"schema", "task_id", "capability", "active_slice"})
    if raw["schema"] != P2D_META_SCHEMA:
        raise KanbanContractError(f"unsupported P2D_META schema: {raw['schema']}")
    for field in ["task_id", "capability"]:
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise KanbanContractError(f"{field} must be a non-empty string")
    if not isinstance(raw["active_slice"], dict) or not raw["active_slice"]:
        raise KanbanContractError("active_slice must be a non-empty object")
    for field in ["provider", "output_root", "gate_status"]:
        if field in raw and raw[field] is not None and not isinstance(raw[field], str):
            raise KanbanContractError(f"{field} must be a string")
    for field in ["input_artifact_refs", "expected_outputs", "verification_expectations", "allowed_side_effects", "depends_on"]:
        if field in raw and raw[field] is not None:
            if not isinstance(raw[field], list) or not all(isinstance(item, str) for item in raw[field]):
                raise KanbanContractError(f"{field} must be a list of strings")
    return P2DMeta(
        task_id=raw["task_id"],
        capability=raw["capability"],
        active_slice=raw["active_slice"],
        provider=raw.get("provider"),
        output_root=raw.get("output_root"),
        input_artifact_refs=list(raw["input_artifact_refs"]) if raw.get("input_artifact_refs") is not None else None,
        expected_outputs=list(raw["expected_outputs"]) if raw.get("expected_outputs") is not None else None,
        verification_expectations=list(raw["verification_expectations"]) if raw.get("verification_expectations") is not None else None,
        allowed_side_effects=list(raw["allowed_side_effects"]) if raw.get("allowed_side_effects") is not None else None,
        gate_status=raw.get("gate_status"),
        depends_on=list(raw["depends_on"]) if raw.get("depends_on") is not None else None,
    )


def append_p2d_meta_marker(text: str, meta: P2DMeta | dict[str, Any]) -> str:
    validated = validate_p2d_meta(meta).to_dict_raw()
    payload = json.dumps(validated, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii")
    marker = f"{P2D_META_BEGIN} {encoded} {P2D_META_END}"
    return f"{text.rstrip()}\n\n{marker}\n" if text.strip() else f"{marker}\n"


def _iter_p2d_meta_payloads(text: str) -> list[str]:
    payloads: list[str] = []
    start = 0
    while True:
        begin = text.find(P2D_META_BEGIN, start)
        if begin < 0:
            break
        payload_start = begin + len(P2D_META_BEGIN)
        end = text.find(P2D_META_END, payload_start)
        if end < 0:
            raise KanbanContractError("unterminated P2D_META marker")
        payload = text[payload_start:end].strip()
        if not payload:
            raise KanbanContractError("empty P2D_META marker")
        payloads.append(payload)
        start = end + len(P2D_META_END)
    return payloads


def _decode_p2d_meta_payload(payload: str) -> P2DMeta:
    try:
        decoded = base64.urlsafe_b64decode(payload.encode("ascii"))
        raw = json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise KanbanContractError(f"invalid P2D_META marker: {exc}") from exc
    if not isinstance(raw, dict):
        raise KanbanContractError("P2D_META marker must decode to an object")
    return validate_p2d_meta(raw)


def extract_p2d_meta_marker(*, body: str, comments: list[str] | None = None) -> P2DMeta | None:
    markers: list[P2DMeta] = []
    for payload in _iter_p2d_meta_payloads(body or ""):
        markers.append(_decode_p2d_meta_payload(payload))
    for comment in comments or []:
        for payload in _iter_p2d_meta_payloads(comment or ""):
            markers.append(_decode_p2d_meta_payload(payload))
    if not markers:
        return None
    first = markers[0]
    for marker in markers[1:]:
        if marker.to_dict_raw() != first.to_dict_raw():
            raise KanbanContractError("conflicting P2D_META markers")
    return first


def p2d_meta_to_task_envelope(
    meta: P2DMeta | dict[str, Any],
    *,
    project_root: str | Path,
    default_output_root: str | Path | None = None,
) -> dict[str, Any]:
    validated = validate_p2d_meta(meta)
    output_root = validated.output_root or default_output_root
    if output_root is None:
        output_root = Path(project_root) / "project-state" / "kanban" / "tasks" / validated.task_id
    envelope = create_task_envelope(
        task_id=validated.task_id,
        capability=validated.capability,
        project_root=project_root,
        active_slice=validated.active_slice,
        input_artifact_refs=validated.input_artifact_refs or [],
        output_root=output_root,
        expected_outputs=validated.expected_outputs or ["result-manifest.json"],
        verification_expectations=validated.verification_expectations or [],
        allowed_side_effects=validated.allowed_side_effects or ["write output_root only"],
    )
    if validated.provider is not None:
        envelope["provider_hint"] = validated.provider
    if validated.depends_on is not None:
        envelope["depends_on"] = list(validated.depends_on)
    return envelope


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


def _has_dependency_unlock_event(events: list[dict[str, Any]], *, task_id: str) -> bool:
    return any(
        event.get("task_id") == task_id and event.get("action") == "dependency_unlocked"
        for event in events
    )


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
