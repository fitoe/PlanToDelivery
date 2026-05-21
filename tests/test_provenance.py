import json
from pathlib import Path

from plantodelivery.kanban_runtime import (
    KanbanOrchestrator,
    KanbanStateStore,
    calculate_file_sha256,
    create_task_envelope,
)


def test_record_task_writes_active_slice_digest_with_envelope_hash(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    store = KanbanStateStore(project_root / "project-state" / "kanban")
    task_id = "p2d-provenance-task"
    output_root = store.tasks_root / task_id
    envelope = create_task_envelope(
        task_id=task_id,
        capability="technical_blueprint",
        project_root=project_root,
        active_slice={"goal": "trace task envelope into digest"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=output_root,
        expected_outputs=["result-manifest.json"],
        verification_expectations=["digest references envelope hash"],
        allowed_side_effects=["write output_root only"],
    )

    task_path = store.record_task(envelope)
    digest_path = output_root / "active-slice-digest.json"
    digest = json.loads(digest_path.read_text(encoding="utf-8"))

    assert digest["provenance"]["task_envelope_path"] == str(task_path)
    assert digest["provenance"]["task_envelope_sha256"] == calculate_file_sha256(task_path)


def test_record_result_adds_manifest_provenance_and_artifact_hashes(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    store = KanbanStateStore(project_root / "project-state" / "kanban")
    task_id = "p2d-provenance-result"
    output_root = store.tasks_root / task_id
    envelope = create_task_envelope(
        task_id=task_id,
        capability="visual_implementation",
        project_root=project_root,
        active_slice={"goal": "trace produced artifacts"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=output_root,
        expected_outputs=["result-manifest.json", "artifact.txt"],
        verification_expectations=["result references artifact hash"],
        allowed_side_effects=["write output_root only"],
    )
    task_path = store.record_task(envelope)
    digest_path = output_root / "active-slice-digest.json"
    artifact_path = output_root / "artifact.txt"
    artifact_path.write_text("provider output\n", encoding="utf-8")

    result_path = store.record_result({
        "schema": "kanban-capability-result/v1",
        "task_id": task_id,
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": [],
        "produced_artifacts": [str(artifact_path)],
        "evidence": [],
        "blockers": [],
        "debts": [],
        "review_required": False,
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    })

    result = json.loads(result_path.read_text(encoding="utf-8"))
    provenance = result["provenance"]
    assert provenance["task_envelope_path"] == str(task_path)
    assert provenance["task_envelope_sha256"] == calculate_file_sha256(task_path)
    assert provenance["active_slice_digest_path"] == str(digest_path)
    assert provenance["active_slice_digest_sha256"] == calculate_file_sha256(digest_path)
    assert provenance["produced_artifact_hashes"] == [
        {"path": str(artifact_path), "sha256": calculate_file_sha256(artifact_path)}
    ]


def test_strict_provenance_audit_detects_tampered_digest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
    providers_root = tmp_path / "providers"
    provider_manifest = providers_root / "design-to-code" / "provider-manifest.json"
    provider_manifest.parent.mkdir(parents=True, exist_ok=True)
    provider_manifest.write_text(json.dumps({
        "schema": "provider-manifest/v1",
        "provider": "design-to-code",
        "capabilities": [{"name": "visual_implementation"}],
    }), encoding="utf-8")
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root)
    orchestrator.dispatch_task(
        task_id="p2d-audit-provenance",
        capability="visual_implementation",
        active_slice={"goal": "audit provenance"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        expected_outputs=["result-manifest.json"],
        verification_expectations=["strict provenance audit"],
        allowed_side_effects=["write output_root only"],
    )
    orchestrator.store.claim_task("p2d-audit-provenance", ttl_seconds=30)
    result_path = orchestrator.ingest_result({
        "schema": "kanban-capability-result/v1",
        "task_id": "p2d-audit-provenance",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": [],
        "produced_artifacts": [],
        "evidence": [],
        "blockers": [],
        "debts": [],
        "review_required": False,
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }).result_path

    digest_path = tmp_path / "project-state" / "kanban" / "tasks" / "p2d-audit-provenance" / "active-slice-digest.json"
    digest = json.loads(digest_path.read_text(encoding="utf-8"))
    digest["active_slice"]["goal"] = "tampered"
    digest_path.write_text(json.dumps(digest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = orchestrator.store.audit_enforcement(strict_digest=True, strict_provenance=True)

    assert report["ok"] is False
    assert any(violation["code"] == "mismatched_result_digest_hash" for violation in report["violations"])
    assert json.loads(result_path.read_text(encoding="utf-8"))["provenance"]["active_slice_digest_sha256"]
