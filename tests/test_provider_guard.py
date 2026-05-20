import json
from pathlib import Path

import pytest

from plantodelivery.kanban_runtime import HermesKanbanBackend, KanbanContractError, create_task_envelope
from plantodelivery.provider_guard import validate_provider_execution_context


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_provider_guard_validates_envelope_digest_and_capability(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    task_id = "p2d-provider-guard"
    output_root = project_root / "project-state" / "kanban" / "tasks" / task_id
    envelope = create_task_envelope(
        task_id=task_id,
        capability="technical_blueprint",
        project_root=project_root,
        active_slice={"goal": "guard provider context"},
        input_artifact_refs=[],
        output_root=output_root,
        expected_outputs=["result-manifest.json"],
        verification_expectations=["guard passes"],
        allowed_side_effects=["write output_root only"],
    )
    backend = HermesKanbanBackend(project_root=project_root, board="p2d-provider-guard", hermes_home=tmp_path / "hermes-home")
    backend.record_task(envelope)
    backend.claim_task(task_id, ttl_seconds=30)

    context = validate_provider_execution_context(
        task_envelope_path=output_root / "task-envelope.json",
        active_slice_digest_path=output_root / "active-slice-digest.json",
        expected_capability="technical_blueprint",
        hermes_backend=backend,
    )

    assert context.task_id == task_id
    assert context.capability == "technical_blueprint"
    assert context.output_root == output_root
    assert context.result_manifest_path == output_root / "result-manifest.json"

    with pytest.raises(KanbanContractError, match="expected capability"):
        validate_provider_execution_context(
            task_envelope_path=output_root / "task-envelope.json",
            active_slice_digest_path=output_root / "active-slice-digest.json",
            expected_capability="visual_implementation",
            hermes_backend=backend,
        )


def test_provider_guard_requires_running_card_and_matching_digest(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    task_id = "p2d-provider-not-running"
    output_root = project_root / "project-state" / "kanban" / "tasks" / task_id
    envelope = create_task_envelope(
        task_id=task_id,
        capability="visual_implementation",
        project_root=project_root,
        active_slice={"goal": "guard running state"},
        input_artifact_refs=[],
        output_root=output_root,
        expected_outputs=["result-manifest.json"],
        verification_expectations=["card running"],
        allowed_side_effects=["write output_root only"],
    )
    backend = HermesKanbanBackend(project_root=project_root, board="p2d-provider-guard-running", hermes_home=tmp_path / "hermes-home")
    backend.record_task(envelope)

    with pytest.raises(KanbanContractError, match="must be running"):
        validate_provider_execution_context(
            task_envelope_path=output_root / "task-envelope.json",
            active_slice_digest_path=output_root / "active-slice-digest.json",
            hermes_backend=backend,
        )

    digest_path = output_root / "active-slice-digest.json"
    digest = json.loads(digest_path.read_text(encoding="utf-8"))
    digest["task_id"] = "different-task"
    _write_json(digest_path, digest)
    backend.claim_task(task_id, ttl_seconds=30)

    with pytest.raises(KanbanContractError, match="does not match task envelope"):
        validate_provider_execution_context(
            task_envelope_path=output_root / "task-envelope.json",
            active_slice_digest_path=digest_path,
            hermes_backend=backend,
        )
