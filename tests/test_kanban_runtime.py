import json
from pathlib import Path

import pytest

from plantodelivery.kanban_runtime import (
    InMemoryKanbanBoardAdapter,
    KanbanContractError,
    KanbanOrchestrator,
    KanbanStateStore,
    create_task_envelope,
    decide_gate_status,
    display_gate_status,
    load_provider_registry,
    load_provider_registry_config,
    validate_result_manifest,
    write_fixture_provider_result,
    write_provider_registry_config,
)


def write_manifest(path: Path, provider: str, capabilities: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema": "provider-manifest/v1",
                "provider": provider,
                "version": "0.1.0",
                "capabilities": [
                    {
                        "name": name,
                        "task_schema": "kanban-capability-task/v1",
                        "result_schema": "kanban-capability-result/v1",
                    }
                    for name in capabilities
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_registry_loads_replaceable_providers_by_capability(tmp_path: Path) -> None:
    write_manifest(tmp_path / "providers" / "idea-to-design" / "provider-manifest.json", "idea-to-design", ["product_visual_design", "visual_source_creation"])
    write_manifest(tmp_path / "providers" / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])

    registry = load_provider_registry(tmp_path / "providers")

    assert registry["product_visual_design"].provider == "idea-to-design"
    assert registry["visual_source_creation"].provider == "idea-to-design"
    assert registry["visual_implementation"].provider == "design-to-code"
    assert registry["visual_implementation"].manifest_path.name == "provider-manifest.json"


def test_registry_rejects_duplicate_capability_without_priority(tmp_path: Path) -> None:
    write_manifest(tmp_path / "a" / "provider-manifest.json", "provider-a", ["visual_implementation"])
    write_manifest(tmp_path / "b" / "provider-manifest.json", "provider-b", ["visual_implementation"])

    with pytest.raises(KanbanContractError, match="duplicate capability"):
        load_provider_registry(tmp_path)


def test_provider_registry_config_records_real_provider_paths(tmp_path: Path) -> None:
    providers = {
        "idea-to-design": tmp_path / "IdeaToDesign" / "contracts" / "provider-manifest.json",
        "idea-to-tech": tmp_path / "IdeaToTech" / "contracts" / "provider-manifest.json",
        "design-to-code": tmp_path / "DesignToCode" / "contracts" / "provider-manifest.json",
    }
    for provider, manifest_path in providers.items():
        write_manifest(manifest_path, provider, [f"{provider}-capability"])

    config_path = write_provider_registry_config(
        tmp_path / "project-state" / "kanban" / "provider-registry.json",
        providers=providers,
    )

    config = load_provider_registry_config(config_path)
    assert config["schema"] == "provider-registry/v1"
    assert set(config["providers"]) == {"idea-to-design", "idea-to-tech", "design-to-code"}
    assert config["providers"]["design-to-code"]["manifest_path"] == str(providers["design-to-code"])

    registry = load_provider_registry(config_path)
    assert registry["design-to-code-capability"].provider == "design-to-code"
    assert registry["design-to-code-capability"].manifest_path == providers["design-to-code"]


def test_task_envelope_is_capability_first_and_bounded(tmp_path: Path) -> None:
    envelope = create_task_envelope(
        task_id="task-001",
        capability="technical_blueprint",
        project_root=tmp_path,
        active_slice={"page": "/mall", "goal": "define API/state seams"},
        input_artifact_refs=["project-state/design/mall-handoff.json"],
        output_root=tmp_path / "project-state" / "kanban" / "task-001",
        expected_outputs=["technical-decisions.json", "verification-matrix.json"],
        verification_expectations=["schema-valid result manifest"],
        allowed_side_effects=["write output_root only"],
    )

    assert envelope["schema"] == "kanban-capability-task/v1"
    assert envelope["capability"] == "technical_blueprint"
    assert "provider" not in envelope
    assert envelope["active_slice"]["page"] == "/mall"
    assert envelope["input_artifact_refs"] == ["project-state/design/mall-handoff.json"]
    assert envelope["allowed_side_effects"] == ["write output_root only"]
    assert envelope["review_policy"]["route_review_required_to"] == "review"
    assert envelope["blocking_policy"]["blocked_only_for_missing_or_unsafe_input"] is True


def test_result_manifest_validation_and_gate_decision_review(tmp_path: Path) -> None:
    manifest = {
        "schema": "kanban-capability-result/v1",
        "task_id": "task-001",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": ["src/pages/mall.vue"],
        "produced_artifacts": ["project-state/implementation/mall-parity.md"],
        "evidence": ["project-state/implementation/screenshots/mall-mobile.png"],
        "blockers": [],
        "debts": ["minor icon mismatch"],
        "review_required": True,
        "suggested_gate_updates": [],
        "next_recommended_task": None,
    }

    validated = validate_result_manifest(manifest, expected_task_id="task-001", expected_capability="visual_implementation")

    assert validated["provider"] == "design-to-code"
    assert decide_gate_status(validated) == "review"


def test_gate_decision_keeps_real_blockers_separate_from_review() -> None:
    assert decide_gate_status({"result": "blocked", "review_required": True, "blockers": ["missing auth token"]}) == "blocked"
    assert decide_gate_status({"result": "partial", "review_required": False, "blockers": []}) == "partial"
    assert decide_gate_status({"result": "completed", "review_required": False, "blockers": []}) == "completed"
    assert decide_gate_status({"result": "failed", "review_required": False, "blockers": []}) == "failed"


def test_result_manifest_rejects_missing_required_fields() -> None:
    with pytest.raises(KanbanContractError, match="missing required fields"):
        validate_result_manifest({"schema": "kanban-capability-result/v1", "task_id": "task-001"})


def test_result_manifest_rejects_task_or_capability_mismatch() -> None:
    manifest = {
        "schema": "kanban-capability-result/v1",
        "task_id": "other",
        "capability": "technical_blueprint",
        "provider": "IdeaToTech",
        "result": "completed",
        "changed_files": [],
        "produced_artifacts": [],
        "evidence": [],
        "blockers": [],
        "debts": [],
        "review_required": False,
        "suggested_gate_updates": [],
        "next_recommended_task": None,
    }

    with pytest.raises(KanbanContractError, match="task_id mismatch"):
        validate_result_manifest(manifest, expected_task_id="task-001", expected_capability="technical_blueprint")


def test_state_store_persists_task_result_and_gate_index(tmp_path: Path) -> None:
    store = KanbanStateStore(tmp_path / "project-state" / "kanban")
    envelope = create_task_envelope(
        task_id="task-001",
        capability="visual_implementation",
        project_root=tmp_path,
        active_slice={"page": "/mall", "goal": "implement approved design"},
        input_artifact_refs=["project-state/design/mall-handoff.json"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "task-001",
        expected_outputs=["result-manifest.json", "parity-report.md"],
        verification_expectations=["screenshot parity evidence"],
        allowed_side_effects=["write implementation files"],
    )

    task_path = store.record_task(envelope)

    assert task_path == tmp_path / "project-state" / "kanban" / "tasks" / "task-001" / "task-envelope.json"
    assert json.loads(task_path.read_text(encoding="utf-8"))["capability"] == "visual_implementation"
    assert store.load_task("task-001")["active_slice"]["page"] == "/mall"
    assert store.load_index()["tasks"]["task-001"]["gate_status"] == "dispatched"

    result_manifest = {
        "schema": "kanban-capability-result/v1",
        "task_id": "task-001",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": ["src/pages/mall.vue"],
        "produced_artifacts": ["project-state/kanban/tasks/task-001/parity-report.md"],
        "evidence": ["project-state/kanban/tasks/task-001/mobile.png"],
        "blockers": [],
        "debts": [],
        "review_required": True,
        "suggested_gate_updates": [],
        "next_recommended_task": None,
    }

    result_path = store.record_result(result_manifest)

    assert result_path == tmp_path / "project-state" / "kanban" / "tasks" / "task-001" / "result-manifest.json"
    index = store.load_index()
    assert index["schema"] == "plantodelivery-kanban-state/v1"
    assert index["tasks"]["task-001"]["result"] == "completed"
    assert index["tasks"]["task-001"]["gate_status"] == "review"
    assert index["gates"]["review"] == ["task-001"]
    assert store.load_result("task-001")["provider"] == "design-to-code"


def test_orchestrator_dispatch_ingest_and_review_approval_flow(tmp_path: Path) -> None:
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root)

    dispatch = orchestrator.dispatch_task(
        task_id="task-002",
        capability="visual_implementation",
        active_slice={"page": "/mall", "goal": "implement approved design"},
        input_artifact_refs=["project-state/design/mall-handoff.json"],
        expected_outputs=["result-manifest.json", "parity-report.md"],
        verification_expectations=["screenshot parity evidence"],
        allowed_side_effects=["write implementation files"],
    )

    assert dispatch.provider == "design-to-code"
    assert dispatch.envelope["capability"] == "visual_implementation"
    assert "provider" not in dispatch.envelope
    assert dispatch.task_path.exists()
    assert dispatch.output_root == tmp_path / "project-state" / "kanban" / "tasks" / "task-002"

    result_manifest = {
        "schema": "kanban-capability-result/v1",
        "task_id": "task-002",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": ["src/pages/mall.vue"],
        "produced_artifacts": ["project-state/kanban/tasks/task-002/parity-report.md"],
        "evidence": ["project-state/kanban/tasks/task-002/mobile.png"],
        "blockers": [],
        "debts": [],
        "review_required": True,
        "suggested_gate_updates": [],
        "next_recommended_task": None,
    }

    ingest = orchestrator.ingest_result(result_manifest)

    assert ingest.gate_status == "review"
    assert ingest.result_path.exists()
    assert orchestrator.store.load_index()["gates"]["review"] == ["task-002"]

    review = orchestrator.approve_review("task-002", evidence=["manual visual review approved"])

    assert review.gate_status == "completed"
    task = orchestrator.store.load_index()["tasks"]["task-002"]
    assert task["review"]["status"] == "approved"
    assert task["review"]["evidence"] == ["manual visual review approved"]
    assert orchestrator.store.load_index()["gates"]["completed"] == ["task-002"]


def test_board_adapter_records_chinese_display_status_for_task_flow(tmp_path: Path) -> None:
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])
    board = InMemoryKanbanBoardAdapter()
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root, board=board)

    assert display_gate_status("dispatched") == "已派发"

    orchestrator.dispatch_task(
        task_id="task-board",
        capability="visual_implementation",
        active_slice={"page": "/mall", "goal": "中文看板状态"},
        input_artifact_refs=[],
        expected_outputs=["result-manifest.json"],
        verification_expectations=[],
        allowed_side_effects=["write output_root only"],
    )
    assert board.cards["task-board"]["gate_status"] == "dispatched"
    assert board.cards["task-board"]["display_status"] == "已派发"
    assert board.events[-1]["display_status"] == "已派发"

    orchestrator.ingest_result(
        {
            "schema": "kanban-capability-result/v1",
            "task_id": "task-board",
            "capability": "visual_implementation",
            "provider": "design-to-code",
            "result": "completed",
            "changed_files": ["src/pages/mall.vue"],
            "produced_artifacts": ["project-state/kanban/tasks/task-board/parity-report.md"],
            "evidence": ["project-state/kanban/tasks/task-board/mobile.png"],
            "blockers": [],
            "debts": [],
            "review_required": True,
            "suggested_gate_updates": [],
            "next_recommended_task": None,
        }
    )
    assert board.cards["task-board"]["gate_status"] == "review"
    assert board.cards["task-board"]["display_status"] == "待审查"
    assert board.cards["task-board"]["result"] == "completed"

    orchestrator.approve_review("task-board", evidence=["人工审查通过"])
    assert board.cards["task-board"]["gate_status"] == "completed"
    assert board.cards["task-board"]["display_status"] == "已完成"
    assert board.cards["task-board"]["review"]["evidence"] == ["人工审查通过"]


def test_orchestrator_rejects_unknown_capability(tmp_path: Path) -> None:
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "idea-to-design" / "provider-manifest.json", "idea-to-design", ["product_visual_design"])
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root)

    with pytest.raises(KanbanContractError, match="no provider for capability"):
        orchestrator.dispatch_task(
            task_id="task-missing",
            capability="visual_implementation",
            active_slice={"page": "/mall"},
            input_artifact_refs=[],
            expected_outputs=[],
            verification_expectations=[],
            allowed_side_effects=[],
        )


def test_fixture_provider_e2e_flow_uses_registry_config(tmp_path: Path) -> None:
    manifest_path = tmp_path / "DesignToCode" / "contracts" / "provider-manifest.json"
    write_manifest(manifest_path, "design-to-code", ["visual_implementation"])
    registry_config = write_provider_registry_config(
        tmp_path / "project-state" / "kanban" / "provider-registry.json",
        providers={"design-to-code": manifest_path},
    )
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=registry_config)

    dispatch = orchestrator.dispatch_task(
        task_id="task-e2e",
        capability="visual_implementation",
        active_slice={"page": "/mall", "goal": "fixture e2e"},
        input_artifact_refs=["project-state/design/mall-handoff.json"],
        expected_outputs=["result-manifest.json"],
        verification_expectations=["fixture evidence exists"],
        allowed_side_effects=["write output_root only"],
    )
    result_path = write_fixture_provider_result(
        task_envelope_path=dispatch.task_path,
        provider="design-to-code",
        result="completed",
        review_required=True,
        changed_files=["src/pages/mall.vue"],
        produced_artifacts=["parity-report.md"],
        evidence=["mobile.png"],
    )

    ingest = orchestrator.ingest_result_path(result_path)
    assert ingest.gate_status == "review"
    assert orchestrator.store.load_index()["gates"]["review"] == ["task-e2e"]

    review = orchestrator.approve_review("task-e2e", evidence=["fixture review approved"])
    assert review.gate_status == "completed"
    assert orchestrator.store.load_index()["gates"]["completed"] == ["task-e2e"]
