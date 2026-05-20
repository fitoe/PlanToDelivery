import json
from pathlib import Path

import pytest

from plantodelivery.kanban_runtime import (
    KanbanContractError,
    create_task_envelope,
    decide_gate_status,
    load_provider_registry,
    validate_result_manifest,
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
