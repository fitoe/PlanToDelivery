import json
from pathlib import Path

import pytest

from plantodelivery.kanban_runtime import (
    ACTIVE_SLICE_DIGEST_SCHEMA,
    KanbanContractError,
    KanbanOrchestrator,
    HermesKanbanBackend,
    DispatchRecord,
    IngestRecord,
    KanbanStateStore,
    P2DMeta,
    ReviewRecord,
    append_p2d_meta_marker,
    bootstrap_provider_registry_from_manifests,
    build_active_slice_digest,
    create_task_envelope,
    decide_kanban_run_policy,
    decide_kanban_status,
    display_kanban_status,
    display_kanban_status_group,
    display_kanban_status_group_label,
    display_kanban_status_groups,
    extract_p2d_meta_marker,
    load_provider_registry,
    load_provider_registry_config,
    p2d_meta_to_task_envelope,
    render_provider_handoff_prompt,
    validate_active_slice_digest,
    validate_p2d_meta,
    validate_result_manifest,
    write_fixture_provider_result,
    write_provider_registry_config,
)


def test_display_kanban_status_uses_human_workflow_labels() -> None:
    assert display_kanban_status("backlog") == "待梳理"
    assert display_kanban_status("ready") == "待开工"
    assert display_kanban_status("dispatched") == "已分配"
    assert display_kanban_status("running") == "执行中"
    assert display_kanban_status("review") == "待确认"
    assert display_kanban_status("blocked") == "卡住了"
    assert display_kanban_status("partial") == "部分完成"
    assert display_kanban_status("completed") == "已完成"
    assert display_kanban_status("failed") == "未通过"
    assert display_kanban_status("cancelled") == "已取消"
    assert display_kanban_status("custom-status") == "custom-status"


def test_display_kanban_groups_fit_six_columns_by_collapsing_low_signal_statuses() -> None:
    groups = display_kanban_status_groups()

    assert len(groups) == 6
    assert [group["id"] for group in groups] == ["inbox", "todo", "active", "review", "blocked", "done"]
    assert [group["label"] for group in groups] == ["待梳理", "待开工", "进行中", "待确认", "卡住了", "已完成"]
    assert groups[0]["statuses"] == ["backlog"]
    assert groups[1]["statuses"] == ["ready"]
    assert groups[2]["statuses"] == ["dispatched", "running"]
    assert groups[3]["statuses"] == ["review"]
    assert groups[4]["statuses"] == ["blocked", "failed"]
    assert groups[5]["statuses"] == ["partial", "completed", "cancelled"]


@pytest.mark.parametrize(
    ("status", "group_id", "group_label"),
    [
        ("backlog", "inbox", "待梳理"),
        ("ready", "todo", "待开工"),
        ("dispatched", "active", "进行中"),
        ("running", "active", "进行中"),
        ("review", "review", "待确认"),
        ("blocked", "blocked", "卡住了"),
        ("failed", "blocked", "卡住了"),
        ("partial", "done", "已完成"),
        ("completed", "done", "已完成"),
        ("cancelled", "done", "已完成"),
    ],
)
def test_display_kanban_status_group_maps_machine_states_without_changing_contract(status: str, group_id: str, group_label: str) -> None:
    assert display_kanban_status_group(status) == group_id
    assert display_kanban_status_group_label(status) == group_label


def test_display_kanban_status_group_falls_back_for_unknown_status() -> None:
    assert display_kanban_status_group("custom-status") == "custom-status"
    assert display_kanban_status_group_label("custom-status") == "custom-status"


def test_active_slice_digest_validator_and_builder_exclude_chat_history(tmp_path: Path) -> None:
    envelope = create_task_envelope(
        task_id="digest-001",
        capability="technical_blueprint",
        project_root=tmp_path,
        active_slice={"goal": "short-context handoff", "page": "/mall"},
        input_artifact_refs=["project-state/design/handoff.json"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "digest-001",
        expected_outputs=["result-manifest.json", "blueprint.md"],
        verification_expectations=["schema valid", "no chat history"],
        allowed_side_effects=["write output_root only"],
    )
    envelope["conversation"] = "should not be copied"
    envelope["chat_history"] = ["old turn"]
    envelope["messages"] = [{"role": "user", "content": "old context"}]

    digest = build_active_slice_digest(
        envelope,
        task_path=tmp_path / "project-state" / "kanban" / "tasks" / "digest-001" / "task-envelope.json",
        stop_rules=["block instead of guessing"],
    )

    assert digest["schema"] == ACTIVE_SLICE_DIGEST_SCHEMA
    assert digest["task_id"] == "digest-001"
    assert digest["capability"] == "technical_blueprint"
    assert digest["active_slice"]["page"] == "/mall"
    assert digest["input_artifact_refs"] == ["project-state/design/handoff.json"]
    assert digest["expected_outputs"] == ["result-manifest.json", "blueprint.md"]
    assert digest["stop_rules"] == ["block instead of guessing"]
    assert digest["context_budget"]["policy"] == "artifact-paths-over-inline-history"
    assert digest["read_first"] == [str(tmp_path / "project-state" / "kanban" / "tasks" / "digest-001" / "task-envelope.json")]
    assert digest["handoff"]["result_manifest_path"].endswith("result-manifest.json")
    serialized = json.dumps(digest, ensure_ascii=False)
    assert "should not be copied" not in serialized
    assert "chat_history" not in serialized
    assert "messages" not in serialized
    assert validate_active_slice_digest(digest) == digest


def test_active_slice_digest_rejects_invalid_schema_missing_fields_and_oversize(tmp_path: Path) -> None:
    valid = {
        "schema": ACTIVE_SLICE_DIGEST_SCHEMA,
        "task_id": "digest-002",
        "capability": "visual_implementation",
        "active_slice": {"goal": "implement"},
        "context_budget": {"max_chars": 6000, "policy": "artifact-paths-over-inline-history"},
        "read_first": [],
        "handoff": {"provider_prompt": "Use artifacts only", "result_manifest_path": "result-manifest.json"},
    }
    assert validate_active_slice_digest(valid)["task_id"] == "digest-002"

    with pytest.raises(KanbanContractError, match="missing required fields"):
        validate_active_slice_digest({"schema": ACTIVE_SLICE_DIGEST_SCHEMA, "task_id": "digest-002"})

    invalid = dict(valid)
    invalid["schema"] = "active-slice-digest/v0"
    with pytest.raises(KanbanContractError, match="unsupported active-slice digest schema"):
        validate_active_slice_digest(invalid)

    envelope = create_task_envelope(
        task_id="digest-oversize",
        capability="technical_blueprint",
        project_root=tmp_path,
        active_slice={"goal": "x" * 200},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=tmp_path / "tasks" / "digest-oversize",
        expected_outputs=[],
        verification_expectations=[],
        allowed_side_effects=[],
    )
    with pytest.raises(KanbanContractError, match="active-slice digest exceeds max_chars"):
        build_active_slice_digest(envelope, max_chars=80)


def test_render_provider_handoff_prompt_is_short_and_path_based(tmp_path: Path) -> None:
    digest_path = tmp_path / "tasks" / "digest-001" / "active-slice-digest.json"
    task_path = tmp_path / "tasks" / "digest-001" / "task-envelope.json"

    prompt = render_provider_handoff_prompt(digest_path, task_path)

    assert str(digest_path) in prompt
    assert str(task_path) in prompt
    assert "kanban-capability-result/v1" in prompt
    assert "Do not rely on prior chat history" in prompt
    assert len(prompt) < 1000


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



def test_hermes_kanban_backend_cli_create_read_claim_complete_block(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    project_root = tmp_path / "project"
    project_root.mkdir()
    backend = HermesKanbanBackend(
        project_root=project_root,
        board="p2d-smoke",
        hermes_home=hermes_home,
    )

    completed_meta = P2DMeta(
        task_id="p2d-complete",
        capability="technical_blueprint",
        active_slice={"goal": "prove complete path"},
        provider="idea-to-tech",
        output_root=str(project_root / "project-state" / "kanban" / "tasks" / "p2d-complete"),
    )
    task_path = backend.record_task(
        p2d_meta_to_task_envelope(completed_meta, project_root=project_root)
    )

    assert task_path == project_root / "project-state" / "kanban" / "tasks" / "p2d-complete" / "task-envelope.json"
    created = backend.load_task("p2d-complete")
    assert created["task_id"] == "p2d-complete"
    assert created["capability"] == "technical_blueprint"
    assert created["provider_hint"] == "idea-to-tech"

    claimed = backend.claim_task("p2d-complete", ttl_seconds=30)
    assert claimed["status"] == "running"

    result_path = backend.record_result({
        "schema": "kanban-capability-result/v1",
        "task_id": "p2d-complete",
        "capability": "technical_blueprint",
        "provider": "idea-to-tech",
        "result": "completed",
        "changed_files": [],
        "produced_artifacts": [],
        "evidence": [],
        "blockers": [],
        "debts": [],
        "review_required": False,
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    })
    assert result_path == project_root / "project-state" / "kanban" / "tasks" / "p2d-complete" / "result-manifest.json"
    assert backend.show_card("p2d-complete")["task"]["status"] == "done"

    blocked_meta = P2DMeta(
        task_id="p2d-blocked",
        capability="visual_implementation",
        active_slice={"goal": "prove block path"},
        provider="design-to-code",
        input_artifact_refs=["project-state/design/approved-design-source.json"],
    )
    backend.record_task(p2d_meta_to_task_envelope(blocked_meta, project_root=project_root))
    backend.claim_task("p2d-blocked", ttl_seconds=30)
    blocked_result = backend.record_result({
        "schema": "kanban-capability-result/v1",
        "task_id": "p2d-blocked",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "blocked",
        "changed_files": [],
        "produced_artifacts": [],
        "evidence": [],
        "blockers": ["missing approved source"],
        "debts": [],
        "review_required": False,
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    })
    assert blocked_result.exists()
    blocked_card = backend.show_card("p2d-blocked")
    assert blocked_card["task"]["status"] == "blocked"
    assert any("missing approved source" in c["body"] for c in blocked_card["comments"])


def test_orchestrator_uses_hermes_backend_for_state_backend_hermes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_manifest(tmp_path / "providers" / "idea-to-tech" / "provider-manifest.json", "idea-to-tech", ["technical_blueprint"])
    hermes_home = tmp_path / "hermes-home"
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    orchestrator = KanbanOrchestrator(
        project_root=tmp_path,
        providers_root=tmp_path / "providers",
        state_backend="hermes",
        board="p2d-orchestrator",
    )
    dispatch = orchestrator.dispatch_task(
        task_id="orch-001",
        capability="technical_blueprint",
        active_slice={"goal": "dispatch through Hermes"},
        input_artifact_refs=[],
        expected_outputs=["result-manifest.json"],
        verification_expectations=["card contains P2D_META"],
        allowed_side_effects=["write output_root only"],
    )

    assert dispatch.provider == "idea-to-tech"
    assert dispatch.task_path.exists()
    assert dispatch.digest_path is not None
    assert dispatch.digest_path.exists()
    assert dispatch.digest_path == tmp_path / "project-state" / "kanban" / "tasks" / "orch-001" / "active-slice-digest.json"
    digest = json.loads(dispatch.digest_path.read_text(encoding="utf-8"))
    assert digest["schema"] == ACTIVE_SLICE_DIGEST_SCHEMA
    assert digest["task_id"] == "orch-001"
    assert digest["read_first"] == [str(dispatch.task_path)]
    index_entry = orchestrator.store.load_index()["tasks"]["orch-001"]
    assert index_entry["digest_path"] == str(dispatch.digest_path)
    card = orchestrator.store.show_card("orch-001")
    assert card["task"]["status"] == "ready"
    meta = extract_p2d_meta_marker(body=card["task"]["body"], comments=[])
    assert meta is not None
    assert str(dispatch.digest_path) in (meta.input_artifact_refs or [])


def test_hermes_backend_enforces_claimed_before_result_and_review_before_done(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    project_root = tmp_path / "project"
    project_root.mkdir()
    backend = HermesKanbanBackend(project_root=project_root, board="p2d-enforce", hermes_home=hermes_home)
    meta = P2DMeta(
        task_id="p2d-review-kanban",
        capability="visual_implementation",
        active_slice={"goal": "prove enforcement"},
        provider="design-to-code",
        expected_outputs=["result-manifest.json", "parity-report.md"],
        verification_expectations=["visual evidence must exist"],
        allowed_side_effects=["write output_root only"],
        input_artifact_refs=["project-state/design/approved-design-source.json"],
    )
    backend.record_task(p2d_meta_to_task_envelope(meta, project_root=project_root))

    review_manifest = {
        "schema": "kanban-capability-result/v1",
        "task_id": "p2d-review-kanban",
        "capability": "visual_implementation",
        "provider": "design-to-code",
        "result": "completed",
        "changed_files": ["src/pages/mall.vue"],
        "produced_artifacts": ["project-state/kanban/tasks/p2d-review-kanban/parity-report.md"],
        "evidence": ["project-state/kanban/tasks/p2d-review-kanban/mobile.png"],
        "blockers": [],
        "debts": [],
        "review_required": True,
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }

    with pytest.raises(KanbanContractError, match="must be claimed/running before ingest_result"):
        backend.record_result(review_manifest)

    backend.claim_task("p2d-review-kanban", ttl_seconds=30)
    result_path = backend.record_result(review_manifest)

    assert result_path.exists()
    assert backend.show_card("p2d-review-kanban")["task"]["status"] == "blocked"
    assert backend.load_index()["tasks"]["p2d-review-kanban"]["kanban_status"] == "review"

    with pytest.raises(KanbanContractError, match="review evidence is required"):
        backend.approve_review("p2d-review-kanban", [])

    backend.approve_review("p2d-review-kanban", ["visual parity approved"] )
    card = backend.show_card("p2d-review-kanban")
    assert card["task"]["status"] == "done"
    assert any("P2D REVIEW APPROVED" in c["body"] for c in card["comments"])


def test_audit_enforcement_reports_missing_marker_and_done_without_result(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    project_root = tmp_path / "project"
    project_root.mkdir()
    backend = HermesKanbanBackend(project_root=project_root, board="p2d-audit", hermes_home=hermes_home)
    backend._run("--board", backend.board, "create", "plain task", "--body", "no marker", "--json", json_output=True)

    meta = P2DMeta(
        task_id="p2d-missing-result",
        capability="technical_blueprint",
        active_slice={"goal": "audit done without manifest"},
        provider="idea-to-tech",
    )
    backend.record_task(p2d_meta_to_task_envelope(meta, project_root=project_root))
    backend.claim_task("p2d-missing-result", ttl_seconds=30)
    backend._run("--board", backend.board, "complete", backend._hermes_task_id("p2d-missing-result"), "--result", "manual bypass")

    report = backend.audit_enforcement()

    codes = {violation["code"] for violation in report["violations"]}
    assert report["ok"] is False
    assert "missing_p2d_meta" in codes
    assert "done_without_result_manifest" in codes
    assert "missing_review_approval" not in codes


def test_strict_digest_audit_reports_missing_or_invalid_digest(tmp_path: Path) -> None:
    hermes_home = tmp_path / "hermes-home"
    project_root = tmp_path / "project"
    project_root.mkdir()
    backend = HermesKanbanBackend(project_root=project_root, board="p2d-strict-digest", hermes_home=hermes_home)

    envelope = create_task_envelope(
        task_id="p2d-missing-digest",
        capability="technical_blueprint",
        project_root=project_root,
        active_slice={"goal": "strict digest audit"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=project_root / "project-state" / "kanban" / "tasks" / "p2d-missing-digest",
        expected_outputs=["result-manifest.json"],
        verification_expectations=["digest exists"],
        allowed_side_effects=["write output_root only"],
    )
    backend.record_task(envelope)
    digest_path = project_root / "project-state" / "kanban" / "tasks" / "p2d-missing-digest" / "active-slice-digest.json"
    digest_path.unlink()

    report = backend.audit_enforcement(strict_digest=True)

    assert report["ok"] is False
    assert any(violation["code"] == "missing_active_slice_digest" for violation in report["violations"])

def test_p2d_meta_marker_round_trips_from_body_and_comments() -> None:
    meta = P2DMeta(
        task_id="task-001",
        capability="technical_blueprint",
        active_slice={"page": "/mall", "goal": "define seams"},
        provider="idea-to-tech",
        output_root="project-state/kanban/tasks/task-001",
        input_artifact_refs=["project-state/design/mall-handoff.json"],
        expected_outputs=["result-manifest.json"],
        verification_expectations=["schema-valid result manifest"],
        allowed_side_effects=["write output_root only"],
    )

    body = append_p2d_meta_marker("Implement the next bounded slice.", meta)
    extracted = extract_p2d_meta_marker(body=body, comments=[])

    assert extracted is not None
    assert extracted.task_id == "task-001"
    assert extracted.capability == "technical_blueprint"
    assert extracted.provider == "idea-to-tech"
    assert extracted.active_slice["page"] == "/mall"
    assert extracted.to_dict()["schema"] == "p2d-meta/v1"

    comment_marker = append_p2d_meta_marker("", meta)
    assert extract_p2d_meta_marker(body="plain user task", comments=["noise", comment_marker]) == extracted


def test_p2d_meta_marker_rejects_invalid_or_conflicting_markers() -> None:
    valid = append_p2d_meta_marker(
        "body",
        {
            "schema": "p2d-meta/v1",
            "task_id": "task-001",
            "capability": "visual_implementation",
            "active_slice": {"page": "/mall"},
            "output_root": "project-state/kanban/tasks/task-001",
        },
    )
    conflict = append_p2d_meta_marker(
        "comment",
        {
            "schema": "p2d-meta/v1",
            "task_id": "task-002",
            "capability": "visual_implementation",
            "active_slice": {"page": "/mall"},
            "output_root": "project-state/kanban/tasks/task-002",
        },
    )

    with pytest.raises(KanbanContractError, match="conflicting P2D_META markers"):
        extract_p2d_meta_marker(body=valid, comments=[conflict])

    with pytest.raises(KanbanContractError, match="missing required fields"):
        validate_p2d_meta({"schema": "p2d-meta/v1", "task_id": "missing-capability"})


def test_p2d_meta_marker_creates_task_envelope_without_extra_board_fields(tmp_path: Path) -> None:
    meta = P2DMeta(
        task_id="task-from-card",
        capability="product_visual_design",
        active_slice={"page": "/home"},
        provider="idea-to-design",
        output_root="project-state/kanban/tasks/task-from-card",
        depends_on=["idea-freeze"],
    )

    envelope = p2d_meta_to_task_envelope(meta, project_root=tmp_path)

    assert envelope["schema"] == "kanban-capability-task/v1"
    assert envelope["task_id"] == "task-from-card"
    assert envelope["capability"] == "product_visual_design"
    assert envelope["provider_hint"] == "idea-to-design"
    assert envelope["depends_on"] == ["idea-freeze"]
    assert "p2d_meta" not in envelope


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


def test_bootstrap_real_provider_manifests_into_json_artifact_store(tmp_path: Path) -> None:
    source_manifests = {
        "idea-to-design": Path("/mnt/c/Users/imjzq/Projects/IdeaToDesign/contracts/provider-manifest.json"),
        "idea-to-tech": Path("/mnt/c/Users/imjzq/Projects/IdeaToTech/contracts/provider-manifest.json"),
        "design-to-code": Path("/mnt/c/Users/imjzq/Projects/DesignToCode/contracts/provider-manifest.json"),
    }
    registry_config = bootstrap_provider_registry_from_manifests(
        tmp_path / "project-state" / "kanban" / "provider-registry.json",
        provider_manifests=source_manifests,
    )
    state_root = tmp_path / "project-state" / "kanban"
    backend = KanbanStateStore(state_root)
    orchestrator = KanbanOrchestrator(
        project_root=tmp_path,
        providers_root=registry_config,
        state_store=backend,
    )

    expectations = {
        "product_visual_design": "idea-to-design",
        "visual_source_creation": "idea-to-design",
        "technical_blueprint": "idea-to-tech",
        "implementation_planning": "idea-to-tech",
        "verification_strategy": "idea-to-tech",
        "visual_implementation": "design-to-code",
    }
    dispatches = {}
    for capability, provider in expectations.items():
        dispatches[capability] = orchestrator.dispatch_task(
            task_id=f"task-{capability.replace('_', '-')}",
            capability=capability,
            active_slice={"goal": f"dispatch {capability} from real provider manifest"},
            input_artifact_refs=["project-state/design/approved-design-source.json"] if capability == "visual_implementation" else [],
            expected_outputs=["result-manifest.json"],
            verification_expectations=["db-backed registry dispatch"],
            allowed_side_effects=["write output_root only"],
        )
        assert dispatches[capability].provider == provider

    registry = load_provider_registry(registry_config)
    assert {capability: registry[capability].provider for capability in expectations} == expectations
    index = KanbanStateStore(state_root).load_index()
    expected_task_ids = [f"task-{capability.replace('_', '-')}" for capability in expectations]
    assert sorted(index["columns"]["dispatched"]) == sorted(expected_task_ids)
    assert sorted(index["display_columns"]["active"]["tasks"]) == sorted(expected_task_ids)
    assert index["display_columns"]["active"]["label"] == "进行中"
    assert index["cards"]["task-visual-implementation"]["display_status"] == "已分配"
    assert index["cards"]["task-visual-implementation"]["display_group"] == "active"
    assert index["cards"]["task-visual-implementation"]["display_group_label"] == "进行中"

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
    assert envelope["kanban_contract"]["status_routing"]["review_required_to"] == "review"
    assert envelope["kanban_contract"]["status_routing"]["blocked_only_for_missing_or_unsafe_input"] is True


def test_result_manifest_validation_and_kanban_decision_review(tmp_path: Path) -> None:
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
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }

    validated = validate_result_manifest(manifest, expected_task_id="task-001", expected_capability="visual_implementation")

    assert validated["provider"] == "design-to-code"
    assert decide_kanban_status(validated) == "review"


def test_kanban_decision_keeps_real_blockers_separate_from_review() -> None:
    assert decide_kanban_status({"result": "blocked", "review_required": True, "blockers": ["missing auth token"]}) == "blocked"
    assert decide_kanban_status({"result": "partial", "review_required": False, "blockers": []}) == "partial"
    assert decide_kanban_status({"result": "completed", "review_required": False, "blockers": []}) == "completed"
    assert decide_kanban_status({"result": "failed", "review_required": False, "blockers": []}) == "failed"


def test_kanban_run_policy_auto_continues_until_hard_stop() -> None:
    completed = {
        "schema": "kanban-capability-result/v1",
        "task_id": "task-auto",
        "capability": "technical_blueprint",
        "provider": "idea-to-tech",
        "result": "completed",
        "changed_files": ["project-state/tech/blueprint.md"],
        "produced_artifacts": ["project-state/tech/blueprint.md"],
        "evidence": ["blueprint verified"],
        "blockers": [],
        "debts": [],
        "review_required": False,
        "suggested_kanban_updates": [],
        "next_recommended_task": {"task_id": "visual-pass", "capability": "product_visual_design"},
    }

    policy = decide_kanban_run_policy(completed)

    assert policy["decision"] == "continue"
    assert policy["auto_continue"] is True
    assert policy["requires_user_decision"] is False
    assert policy["safe_to_continue_other_cards"] is True
    assert policy["stop_reason"] is None
    assert policy["next_recommended_task"]["task_id"] == "visual-pass"


@pytest.mark.parametrize(
    ("manifest", "stop_reason"),
    [
        ({"result": "completed", "review_required": True, "blockers": []}, "human_review_required"),
        ({"result": "blocked", "review_required": False, "blockers": ["missing credential"]}, "blocked"),
        ({"result": "failed", "review_required": False, "blockers": []}, "failed"),
    ],
)
def test_kanban_run_policy_stops_only_for_review_blocked_or_failed(manifest: dict[str, object], stop_reason: str) -> None:
    policy = decide_kanban_run_policy(manifest)

    assert policy["decision"] == "stop"
    assert policy["auto_continue"] is False
    assert policy["requires_user_decision"] is (stop_reason == "human_review_required")
    assert policy["safe_to_continue_other_cards"] is (stop_reason != "failed")
    assert policy["stop_reason"] == stop_reason


def test_kanban_run_policy_marks_stop_rules_as_local_or_global() -> None:
    local = decide_kanban_run_policy(
        {"result": "blocked", "review_required": False, "blockers": ["waiting on one design asset"]},
        stop_rules=["hard_blocker"],
    )
    global_stop = decide_kanban_run_policy(
        {"result": "completed", "review_required": False, "blockers": []},
        stop_rules=["direction_decision", "destructive_action", "external_side_effect"],
    )

    assert local["decision"] == "stop"
    assert local["safe_to_continue_other_cards"] is True
    assert local["stop_rules"] == ["hard_blocker"]
    assert global_stop["decision"] == "stop"
    assert global_stop["requires_user_decision"] is True
    assert global_stop["safe_to_continue_other_cards"] is False
    assert global_stop["stop_reason"] == "global_stop_rule"
    assert global_stop["stop_rules"] == ["direction_decision", "destructive_action", "external_side_effect"]


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
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }

    with pytest.raises(KanbanContractError, match="task_id mismatch"):
        validate_result_manifest(manifest, expected_task_id="task-001", expected_capability="technical_blueprint")


def test_state_store_persists_task_result_and_kanban_index(tmp_path: Path) -> None:
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
    assert store.load_index()["tasks"]["task-001"]["kanban_status"] == "dispatched"

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
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }

    result_path = store.record_result(result_manifest)

    assert result_path == tmp_path / "project-state" / "kanban" / "tasks" / "task-001" / "result-manifest.json"
    index = store.load_index()
    assert index["schema"] == "plantodelivery-kanban-state/v1"
    assert index["tasks"]["task-001"]["result"] == "completed"
    assert index["tasks"]["task-001"]["kanban_status"] == "review"
    assert index["tasks"]["task-001"]["run_policy"]["decision"] == "stop"
    assert index["tasks"]["task-001"]["run_policy"]["stop_reason"] == "human_review_required"
    assert index["tasks"]["task-001"]["run_policy"]["safe_to_continue_other_cards"] is True
    assert index["columns"]["review"] == ["task-001"]
    assert index["display_columns"]["review"]["tasks"] == ["task-001"]
    assert index["tasks"]["task-001"]["display_group"] == "review"
    assert index["tasks"]["task-001"]["display_group_label"] == "待确认"
    assert store.load_result("task-001")["provider"] == "design-to-code"


def test_orchestrator_dispatch_ingest_and_review_approval_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
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
    assert dispatch.envelope["provider_hint"] == "design-to-code"
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
        "suggested_kanban_updates": [],
        "next_recommended_task": None,
    }

    assert isinstance(orchestrator.store, HermesKanbanBackend)
    orchestrator.store.claim_task("task-002", ttl_seconds=30)
    ingest = orchestrator.ingest_result(result_manifest)

    assert ingest.kanban_status == "review"
    assert ingest.result_path.exists()
    assert orchestrator.store.load_index()["columns"]["review"] == ["task-002"]

    review = orchestrator.approve_review("task-002", evidence=["manual visual review approved"])

    assert review.kanban_status == "completed"
    task = orchestrator.store.load_index()["tasks"]["task-002"]
    assert task["review"]["status"] == "approved"
    assert task["review"]["evidence"] == ["manual visual review approved"]
    assert orchestrator.store.load_index()["columns"]["completed"] == ["task-002"]


def test_state_store_is_canonical_kanban_state_with_chinese_display_status(tmp_path: Path) -> None:
    store = KanbanStateStore(tmp_path / "project-state" / "kanban")
    envelope = create_task_envelope(
        task_id="task-canonical",
        capability="visual_implementation",
        project_root=tmp_path,
        active_slice={"page": "/mall", "goal": "canonical kanban 状态"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "task-canonical",
        expected_outputs=["result-manifest.json"],
        verification_expectations=[],
        allowed_side_effects=["write output_root only"],
    )

    store.record_task(envelope)
    index = store.load_index()
    task = index["tasks"]["task-canonical"]
    assert task["kanban_status"] == "dispatched"
    assert task["display_status"] == "已分配"
    assert index["cards"]["task-canonical"]["display_status"] == "已分配"
    assert index["events"][-1] == {
        "task_id": "task-canonical",
        "kanban_status": "dispatched",
        "display_status": "已分配",
        "display_group": "active",
        "display_group_label": "进行中",
        "action": "dispatch",
    }

    store.record_result(
        {
            "schema": "kanban-capability-result/v1",
            "task_id": "task-canonical",
            "capability": "visual_implementation",
            "provider": "design-to-code",
            "result": "completed",
            "changed_files": ["src/pages/mall.vue"],
            "produced_artifacts": ["project-state/kanban/tasks/task-canonical/parity-report.md"],
            "evidence": ["project-state/kanban/tasks/task-canonical/mobile.png"],
            "blockers": [],
            "debts": [],
            "review_required": True,
            "suggested_kanban_updates": [],
            "next_recommended_task": None,
        }
    )
    index = KanbanStateStore(tmp_path / "project-state" / "kanban").load_index()
    assert index["tasks"]["task-canonical"]["kanban_status"] == "review"
    assert index["tasks"]["task-canonical"]["display_status"] == "待确认"
    assert index["cards"]["task-canonical"]["result"] == "completed"
    assert index["cards"]["task-canonical"]["display_status"] == "待确认"
    assert index["events"][-1]["action"] == "ingest_result"

    store.approve_review("task-canonical", ["人工审查通过"])
    index = store.load_index()
    assert index["tasks"]["task-canonical"]["kanban_status"] == "completed"
    assert index["tasks"]["task-canonical"]["display_status"] == "已完成"
    assert index["cards"]["task-canonical"]["review"]["evidence"] == ["人工审查通过"]
    assert index["events"][-1]["action"] == "approve_review"


def test_orchestrator_writes_canonical_kanban_state_without_board_adapter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root)

    orchestrator.dispatch_task(
        task_id="task-db-board",
        capability="visual_implementation",
        active_slice={"page": "/mall", "goal": "持久化中文看板状态"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        expected_outputs=["result-manifest.json"],
        verification_expectations=[],
        allowed_side_effects=["write output_root only"],
    )
    reloaded = KanbanStateStore(tmp_path / "project-state" / "kanban").load_index()
    assert reloaded["cards"]["task-db-board"]["kanban_status"] == "dispatched"
    assert reloaded["cards"]["task-db-board"]["display_status"] == "已分配"

    assert isinstance(orchestrator.store, HermesKanbanBackend)
    orchestrator.store.claim_task("task-db-board", ttl_seconds=30)
    orchestrator.ingest_result(
        {
            "schema": "kanban-capability-result/v1",
            "task_id": "task-db-board",
            "capability": "visual_implementation",
            "provider": "design-to-code",
            "result": "blocked",
            "changed_files": [],
            "produced_artifacts": [],
            "evidence": [],
            "blockers": ["等待设计冻结"],
            "debts": [],
            "review_required": False,
            "suggested_kanban_updates": [],
            "next_recommended_task": None,
        }
    )
    reloaded = KanbanStateStore(tmp_path / "project-state" / "kanban").load_index()
    assert reloaded["cards"]["task-db-board"]["kanban_status"] == "blocked"
    assert reloaded["cards"]["task-db-board"]["display_status"] == "卡住了"
    assert reloaded["events"][-1]["action"] == "ingest_result"



def test_self_managed_sqlite_backend_is_removed_from_orchestrator(tmp_path: Path) -> None:
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])

    with pytest.raises(KanbanContractError, match="unsupported state_backend: sqlite"):
        KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root, state_backend="sqlite")


def test_orchestrator_rejects_json_backend_for_real_execution(tmp_path: Path) -> None:
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])

    with pytest.raises(KanbanContractError, match='state_backend="json" is test/export only'):
        KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root, state_backend="json")


def test_project_state_store_remains_json_artifact_overlay_not_sqlite(tmp_path: Path) -> None:
    store = KanbanStateStore(tmp_path / "project-state" / "kanban")
    envelope = create_task_envelope(
        task_id="task-json-overlay",
        capability="visual_implementation",
        project_root=tmp_path,
        active_slice={"page": "/mall", "goal": "artifact overlay only"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "task-json-overlay",
        expected_outputs=["result-manifest.json"],
        verification_expectations=["json artifacts only"],
        allowed_side_effects=["write output_root only"],
    )

    store.record_task(envelope)

    assert store.index_path == tmp_path / "project-state" / "kanban" / "kanban-state.json"
    assert not (tmp_path / "project-state" / "kanban" / "kanban-state.sqlite3").exists()
    assert not hasattr(store, "db_path")


def test_provider_recommendations_are_json_overlay_only_until_hermes_board_backend(tmp_path: Path) -> None:
    store = KanbanStateStore(tmp_path / "project-state" / "kanban")
    envelope = create_task_envelope(
        task_id="task-json-dag-source",
        capability="technical_blueprint",
        project_root=tmp_path,
        active_slice={"feature": "provider driven task DAG"},
        input_artifact_refs=["project-state/design/approved-design-source.json"],
        output_root=tmp_path / "project-state" / "kanban" / "tasks" / "task-json-dag-source",
        expected_outputs=["result-manifest.json"],
        verification_expectations=["recommendations remain artifact metadata"],
        allowed_side_effects=["write output_root only"],
    )
    store.record_task(envelope)

    store.record_result(
        {
            "schema": "kanban-capability-result/v1",
            "task_id": "task-json-dag-source",
            "capability": "technical_blueprint",
            "provider": "idea-to-tech",
            "result": "completed",
            "changed_files": [],
            "produced_artifacts": ["project-state/tech/blueprint.md"],
            "evidence": ["blueprint contract checked"],
            "blockers": [],
            "debts": [],
            "review_required": False,
            "suggested_kanban_updates": [
                {"task_id": "visual-pass", "kanban_status": "ready", "reason": "blueprint complete"},
            ],
            "next_recommended_task": {
                "task_id": "visual-pass",
                "capability": "visual_implementation",
                "active_slice": {"page": "/mall"},
                "depends_on": ["task-json-dag-source"],
            },
        }
    )

    index = KanbanStateStore(tmp_path / "project-state" / "kanban").load_index()
    source = index["tasks"]["task-json-dag-source"]
    assert source["suggested_kanban_updates"] == [
        {"task_id": "visual-pass", "kanban_status": "ready", "reason": "blueprint complete"},
    ]
    assert source["next_recommended_task"]["task_id"] == "visual-pass"
    assert "visual-pass" not in index["tasks"]


def test_dispatch_next_ready_task_requires_hermes_board_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
    providers_root = tmp_path / "providers"
    write_manifest(providers_root / "design-to-code" / "provider-manifest.json", "design-to-code", ["visual_implementation"])
    orchestrator = KanbanOrchestrator(project_root=tmp_path, providers_root=providers_root)

    with pytest.raises(KanbanContractError, match="Hermes Kanban board backend"):
        orchestrator.dispatch_next_ready_task()

def test_orchestrator_rejects_unknown_capability(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
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


def test_fixture_provider_e2e_flow_uses_registry_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
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

    assert isinstance(orchestrator.store, HermesKanbanBackend)
    orchestrator.store.claim_task("task-e2e", ttl_seconds=30)
    ingest = orchestrator.ingest_result_path(result_path)
    assert ingest.kanban_status == "review"
    assert orchestrator.store.load_index()["columns"]["review"] == ["task-e2e"]

    review = orchestrator.approve_review("task-e2e", evidence=["fixture review approved"])
    assert review.kanban_status == "completed"
    assert orchestrator.store.load_index()["columns"]["completed"] == ["task-e2e"]
