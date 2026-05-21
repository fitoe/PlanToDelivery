# Javis B Implementation Roadmap

**Direction:** B — Kanban DB backed AI Delivery OS
**Canonical project:** `/mnt/c/Users/imjzq/Projects/PlanToDelivery`

## 1. Principles

- Target B, implement by vertical slices.
- DB is canonical state; JSON is export/test helper only.
- Strong gates before strong automation.
- Start single-project before multi-project scheduling.
- Start manual/subagent provider runtime before full daemonization.
- Preserve existing `kanban-*` contracts for compatibility while extending semantics.

## 2. Phase 0 — Specification landing

Goal: persist approved requirements, architecture, contracts, and roadmap.

Files:

```text
docs/requirements/javis-ai-delivery-os-requirements.md
docs/architecture/javis-ai-delivery-os-architecture.md
docs/contracts/javis-data-model-v1.md
docs/contracts/javis-kanban-constraint-model-v1.md
docs/contracts/javis-artifact-model-v1.md
docs/contracts/javis-provider-runtime-v1.md
docs/plans/javis-b-implementation-roadmap.md
```

Acceptance:

- B is recorded as official implementation direction.
- Existing `kanban-*` contracts remain compatible.
- DB canonical state, gates, artifact index, provider runtime, and snapshots are documented.

## 3. Phase 1 — Kanban DB canonical state

Implement DB-backed state for:

```text
Project / Slice / KanbanDependency / CapabilityTask / Artifact / Decision / Waiver / ChangeRequest / Event
```

Minimum API:

```text
create_project
create_slice
set_kanban_status
create_artifact_ref
approve_artifact
create_task
update_task_status
record_event
load_project_snapshot
load_slice_snapshot
```

Tests:

- project and slices recover from DB;
- Kanban dependency/review completion unlocks downstream only when allowed;
- artifact refs are indexed in DB;
- event log is append-only;
- snapshots avoid full artifact bodies.

## 4. Phase 2 — Dual status and board projections

Implement:

- user-facing Kanban status enum;
- internal engine status enum;
- Slice Status Board projection;
- Provider Task Board projection;
- Review / Decision Board projection.

Tests:

- missing design => 待设计;
- missing asset => 待素材规划;
- missing tech spec => 待技术说明;
- blocker priority => 已阻塞;
- review_required => 待审查;
- all required Kanban dependencies/reviews completed => 已完成.

## 5. Phase 3 — Kanban Constraint Controller

Implement project and slice Kanban dependency/review unlock logic.

API:

```text
can_unlock_gate
approve_gate
waive_gate
required_missing_items
derive_next_gate
```

Tests:

- no design crop blocks implementation_ready;
- no tech spec blocks implementation_ready;
- blocking decision blocks implementation_ready;
- waiver unlocks with risk record;
- review-required is review, not blocked;
- partial result does not auto-complete.

## 6. Phase 4 — Artifact Index + Versioning

Implement artifact refs, versions, approved refs, summaries, hashes, dimensions, and linked slice/task records.

API:

```text
create_artifact_ref
supersede_artifact
approve_artifact
get_approved_artifact
list_artifacts_for_slice
```

Tests:

- v2 supersedes v1;
- only approved artifacts unlock gates;
- summaries appear in snapshots;
- missing file does not count as approved;
- full artifact body is not loaded by default.

## 7. Phase 5 — Blueprint / Decision workflow

Implement the flow from brainstorming to blueprint to decision clearance.

API:

```text
record_brainstorming
create_requirements_draft
approve_delivery_blueprint
extract_decisions
approve_decision
generate_initial_slices
```

Acceptance:

- brainstorming produces requirements draft;
- blueprint approval creates initial slices;
- blocking decisions enter board and block execution until cleared.

## 8. Phase 6 — Design Board / Asset Board pipeline

Implement design and asset artifact registration.

API:

```text
register_design_board
register_page_crop
approve_design_reference
register_asset_requirement
register_asset_board
register_asset_crop
approve_asset_plan
```

Tests:

- missing page crop => 待设计;
- missing required key state => 待设计;
- needed asset missing => 待素材规划;
- design board cannot be used as asset crop;
- asset crop records dimensions and source.

## 9. Phase 7 — Provider Runtime

Implement dispatch, ingest, review, retry, and blocker semantics.

API:

```text
dispatch_task
ingest_result
request_review
approve_review
request_changes
diagnose_failure
retry_task
```

Tests:

- capability routes to provider;
- task envelope includes artifact summaries;
- result manifest updates task/Kanban/artifact/event state;
- review_required enters review;
- blocker only blocks affected slice unless project-level.

## 10. Phase 8 — Dev Server Manager + Resource Locks

API:

```text
get_or_start_dev_server
health_check_dev_server
request_resource_lock
release_resource_lock
list_active_locks
```

Tests:

- healthy dev server is reused;
- unhealthy server can be restarted with event;
- duplicate locks are denied;
- shared resources require locks;
- workers cannot restart server concurrently.

## 11. Phase 9 — Verification Runtime

API:

```text
record_verification_evidence
require_verification_level
create_visual_deviation_report
approve_slice_verification
create_acceptance_report
```

Tests:

- dev_loop does not require full build;
- slice_gate requires page evidence;
- final_gate requires complete evidence;
- no fresh evidence blocks completed;
- remote delivery can produce screenshot comparison artifact.

## 12. Phase 10 — Reporting + Resume

API:

```text
load_project_control_snapshot
load_slice_control_snapshot
build_task_execution_context
generate_progress_report
```

Tests:

- snapshots contain active tasks, blockers, decisions, dev server, locks, and next actions;
- snapshots do not grow linearly with artifact history;
- progress reports are generated from DB/events;
- orchestration can resume after context loss.

## 13. First vertical E2E slice

Start with a single project and single Slice:

```text
create project
create home slice
register requirements draft
register delivery blueprint
register design crop
register tech spec
unlock implementation_ready
dispatch visual_implementation task
ingest result manifest
enter review
approve review
register verification evidence
complete slice
generate Slice Board
generate ProjectControlSnapshot
```

This proves DB state, Kanban constraint enforcement, artifact refs, task/result lifecycle, board projection, and snapshot recovery.

## 14. Checkpoint rhythm

Suggested commits:

```text
docs: specify javis ai delivery os
feat: add kanban db project and slice state
feat: add Kanban constraint controller
feat: add artifact index
feat: add board projections
feat: add provider task lifecycle
feat: add dev server manager
feat: add verification evidence runtime
feat: add project resume snapshots
```

Each checkpoint should include tests, documentation, state verification, and no unrelated staged files.
