import json
import subprocess
import sys
from pathlib import Path

import pytest

from plantodelivery.kanban_runtime import (
    APPROVAL_PACKET_SCHEMA,
    PROVIDER_DOCTOR_SCHEMA,
    RESUME_SNAPSHOT_SCHEMA,
    KanbanContractError,
    KanbanStateStore,
    build_approval_packet,
    build_resume_snapshot,
    create_task_envelope,
    diagnose_provider_registry,
    load_project_alias_registry,
    resolve_project_alias,
    validate_approval_packet,
    write_project_alias_registry,
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


def make_review_task(tmp_path: Path) -> tuple[KanbanStateStore, Path, Path]:
    store = KanbanStateStore(tmp_path / "project-state" / "kanban")
    envelope = create_task_envelope(
        task_id="review-homepage",
        capability="visual_implementation",
        project_root=tmp_path,
        active_slice={"page": "/", "goal": "implement approved homepage"},
        input_artifact_refs=["project-state/design/approved-design/homepage-approved.png"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "review-homepage",
        expected_outputs=["result-manifest.json", "parity-report.md"],
        verification_expectations=["visual parity screenshot"],
        allowed_side_effects=["write src/pages/home.vue"],
    )
    task_path = store.record_task(envelope)
    result_path = store.record_result(
        {
            "schema": "kanban-capability-result/v1",
            "task_id": "review-homepage",
            "capability": "visual_implementation",
            "provider": "design-to-code",
            "result": "completed",
            "changed_files": ["src/pages/home.vue"],
            "produced_artifacts": ["project-state/kanban/tasks/review-homepage/parity-report.md"],
            "evidence": ["project-state/kanban/tasks/review-homepage/mobile.png"],
            "blockers": [],
            "debts": ["minor icon tune-up"],
            "review_required": True,
            "suggested_kanban_updates": [],
            "next_recommended_task": None,
        }
    )
    return store, task_path, result_path


def test_provider_doctor_reports_required_capabilities_and_duplicate_conflicts(tmp_path: Path) -> None:
    providers = tmp_path / "providers"
    write_manifest(providers / "idea-to-tech" / "provider-manifest.json", "idea-to-tech", ["technical_blueprint"])
    write_manifest(providers / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])

    report = diagnose_provider_registry(
        providers,
        required_capabilities=["technical_blueprint", "visual_implementation", "product_visual_design"],
    )

    assert report["schema"] == PROVIDER_DOCTOR_SCHEMA
    assert report["ok"] is False
    assert report["providers"] == ["design-to-code", "idea-to-tech"]
    assert report["capabilities"]["visual_implementation"]["provider"] == "design-to-code"
    assert report["missing_capabilities"] == ["product_visual_design"]
    assert any(item["code"] == "missing_required_capability" for item in report["violations"])

    write_manifest(providers / "alt-d2c" / "provider-manifest.json", "alt-d2c", ["visual_implementation"])
    duplicate = diagnose_provider_registry(providers, required_capabilities=["visual_implementation"])
    assert duplicate["ok"] is False
    assert any(item["code"] == "registry_error" and "duplicate capability" in item["message"] for item in duplicate["violations"])


def test_project_alias_registry_resolves_aliases_and_real_paths(tmp_path: Path) -> None:
    ruoshui = tmp_path / "ruoshui"
    ruoshui.mkdir()
    registry_path = write_project_alias_registry(
        tmp_path / "project-state" / "project-aliases.json",
        aliases={"若水": ruoshui, "ruoshui": ruoshui},
    )

    registry = load_project_alias_registry(registry_path)

    assert registry["schema"] == "p2d-project-aliases/v1"
    assert resolve_project_alias("若水", registry_paths=[registry_path]) == ruoshui.resolve()
    assert resolve_project_alias("ruoshui", registry_paths=[registry_path]) == ruoshui.resolve()
    assert resolve_project_alias(str(ruoshui), registry_paths=[registry_path]) == ruoshui.resolve()
    with pytest.raises(KanbanContractError, match="unknown project alias"):
        resolve_project_alias("missing-project", registry_paths=[registry_path])


def test_approval_packet_is_review_ready_and_schema_valid(tmp_path: Path) -> None:
    _, task_path, result_path = make_review_task(tmp_path)

    packet = build_approval_packet(
        task_envelope_path=task_path,
        result_manifest_path=result_path,
        review_prompt="请确认首页视觉是否通过",
    )

    assert packet["schema"] == APPROVAL_PACKET_SCHEMA
    assert packet["task_id"] == "review-homepage"
    assert packet["status"] == "review"
    assert packet["requires_user_decision"] is True
    assert packet["review_prompt"] == "请确认首页视觉是否通过"
    assert packet["changed_files"] == ["src/pages/home.vue"]
    assert packet["evidence"] == ["project-state/kanban/tasks/review-homepage/mobile.png"]
    assert packet["approval_options"] == ["approve", "request_changes", "block"]
    assert validate_approval_packet(packet) == packet


def test_approval_packet_rejects_non_review_results(tmp_path: Path) -> None:
    store, task_path, result_path = make_review_task(tmp_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["review_required"] = False
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    with pytest.raises(KanbanContractError, match="approval packet requires a review-required result"):
        build_approval_packet(task_envelope_path=task_path, result_manifest_path=result_path)


def test_resume_snapshot_summarizes_review_blocked_and_next_ready(tmp_path: Path) -> None:
    store, _, _ = make_review_task(tmp_path)
    ready_envelope = create_task_envelope(
        task_id="next-page-design",
        capability="product_visual_design",
        project_root=tmp_path,
        active_slice={"page": "/about", "goal": "design next page"},
        input_artifact_refs=[],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "next-page-design",
        expected_outputs=["visual-source.json"],
        verification_expectations=[],
        allowed_side_effects=["write design artifacts only"],
    )
    store.record_task(ready_envelope)
    index = store.load_index()
    index["tasks"]["next-page-design"]["kanban_status"] = "ready"
    store._sync_card(index, "next-page-design", action="manual_ready")
    store._rebuild_columns(index)
    store._write_index(index)

    snapshot = build_resume_snapshot(project_root=tmp_path, state_root=tmp_path / "project-state" / "kanban")

    assert snapshot["schema"] == RESUME_SNAPSHOT_SCHEMA
    assert snapshot["project_root"] == str(tmp_path)
    assert snapshot["counts_by_status"]["review"] == 1
    assert snapshot["counts_by_status"]["ready"] == 1
    assert snapshot["review_tasks"] == ["review-homepage"]
    assert snapshot["next_ready_tasks"] == ["next-page-design"]
    assert snapshot["resume_actions"][0]["action"] == "present_approval_packet"
    assert snapshot["resume_actions"][0]["task_id"] == "review-homepage"


def test_p2d_enforce_cli_writes_approval_packet_and_resume_snapshot(tmp_path: Path) -> None:
    _, task_path, result_path = make_review_task(tmp_path)
    script = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "plantodelivery" / "scripts" / "p2d_enforce.py"
    packet_path = tmp_path / "approval-packet.json"
    resume_path = tmp_path / "resume-snapshot.json"

    packet_proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(tmp_path),
            "approval-packet",
            "--task-envelope",
            str(task_path),
            "--result-manifest",
            str(result_path),
            "--output",
            str(packet_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert packet_proc.returncode == 0, packet_proc.stderr
    assert json.loads(packet_path.read_text(encoding="utf-8"))["schema"] == APPROVAL_PACKET_SCHEMA

    resume_proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(tmp_path),
            "resume",
            "--output",
            str(resume_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert resume_proc.returncode == 0, resume_proc.stderr
    assert json.loads(resume_path.read_text(encoding="utf-8"))["schema"] == RESUME_SNAPSHOT_SCHEMA
