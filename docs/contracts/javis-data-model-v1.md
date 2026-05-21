# Javis Data Model v1

## 1. Principle

Kanban DB is canonical. File paths referenced by the DB are artifacts, not state truth.

All models SHOULD include `created_at` and `updated_at` unless they are append-only events.

## 2. Project

Represents a complete delivery effort.

Fields:

```text
project_id
name
goal_summary
status
current_phase
root_path
tech_stack_summary
approved_blueprint_artifact_id
approved_decision_list_artifact_id
default_dev_server_id
created_at
updated_at
```

## 3. Slice

Represents the user-visible delivery card: page, page-state group, feature, flow, module, or acceptance unit.

Fields:

```text
slice_id
project_id
title
type: page | feature | flow | module | acceptance
goal_summary
route_or_entry
kanban_status
priority
owner_provider
depends_on_slice_ids
approved_design_ref_ids
approved_asset_ref_ids
approved_tech_spec_artifact_id
acceptance_criteria_artifact_id
status_summary
blocker_summary
next_action
created_at
updated_at
```

## 4. KanbanDependency

Represents the dependency, review, blocker, or acceptance evidence that Hermes Kanban uses to constrain project/slice progression. This is not a separate execution state machine; downstream work is unlocked only through canonical Kanban state plus recorded evidence.

Fields:

```text
kanban_dependency_id
project_id
slice_id nullable
dependency_type
status
required_artifact_ids
required_decision_ids
waiver_id nullable
approved_by
approved_at
blocked_reason
created_at
updated_at
```

Kanban dependency status values:

```text
missing
drafting
ready_for_review
approved
blocked
waived
failed
```

Only `approved` and explicit `waived` evidence can unlock downstream Kanban cards.

## 5. CapabilityTask

Represents actual provider/subagent/command work.

Fields:

```text
task_id
project_id
slice_id
capability
provider_id
engine_status
input_artifact_refs
output_artifact_refs
task_envelope_artifact_id
result_manifest_artifact_id
allowed_files
forbidden_files
locked_resource_ids
verification_level
attempt_count
max_attempts
review_required
blockers
debts
started_at
completed_at
created_at
updated_at
```

Engine status values:

```text
backlog
ready
dispatched
running
review
blocked
retrying
partial
completed
failed
cancelled
waived
```

## 6. Provider

Declares a capability source.

Fields:

```text
provider_id
name
manifest_path
capabilities
execution_mode: manual | subagent | command | builtin
priority
enabled
constraints
created_at
updated_at
```

## 7. Artifact

Indexes a file, image, manifest, report, screenshot, log, or generated asset.

Fields:

```text
artifact_id
project_id
slice_id nullable
task_id nullable
type
path
version
status
summary
mime_type
dimensions nullable
hash nullable
created_by
approved_by
approved_at
created_at
updated_at
```

Artifact status values:

```text
draft
generated
ready_for_review
approved
rejected
superseded
archived
```

## 8. Decision

Represents a user/architecture/product decision.

Fields:

```text
decision_id
project_id
slice_id nullable
title
description
options
recommended_option
selected_option
status: pending | approved | rejected | superseded
impact_scope
blocks_gate_ids
created_at
decided_at
```

## 9. Waiver

Explicitly waives a required Kanban dependency while preserving risk.

Fields:

```text
waiver_id
project_id
slice_id nullable
gate_id
reason
risk
approved_by
approved_at
compensation_required
compensation_task_id nullable
expires_at nullable
```

## 10. ChangeRequest

Represents new or changed requirements during execution.

Fields:

```text
change_request_id
project_id
slice_id nullable
title
description
reason
impact_scope
affected_slice_ids
affected_artifact_ids
affected_gate_ids
recommendation
status: proposed | analyzing | approved | rejected | applied | deferred
requires_user_decision
created_at
resolved_at
```

## 11. DevServer

Tracks reusable project dev server processes.

Fields:

```text
dev_server_id
project_id
command
cwd
port
url
process_session_id
pid
status: unknown | starting | healthy | unhealthy | stopped
started_at
last_health_check_at
last_used_at
restart_count
notes
```

## 12. ResourceLock

Prevents unsafe parallel shared-resource modification.

Fields:

```text
lock_id
project_id
resource_type
resource_key
held_by_task_id
held_by_provider_id
reason
status: requested | granted | released | denied | expired
created_at
granted_at
released_at
```

Resource types:

```text
route
global_style
theme_tokens
shared_component
api_client
state_store
build_config
dev_server
dependency
```

## 13. Event

Append-only state transition record.

Fields:

```text
event_id
project_id
slice_id nullable
task_id nullable
event_type
payload
created_by
created_at
```

Events MUST be append-only.

## 14. Snapshot models

### ProjectControlSnapshot

```text
project_id
goal_summary
current_phase
active_slices
pending_decisions
blocked_slices
running_tasks
review_items
approved_artifacts
dev_server_status
resource_locks
recent_events_summary
next_recommended_actions
```

### SliceControlSnapshot

```text
slice_id
title
goal_summary
kanban_status
required_kanban_dependencies
approved_design_refs
approved_asset_refs
approved_tech_spec
pending_decisions
active_tasks
blockers
verification_status
next_action
```

### TaskExecutionContext

```text
task_id
capability
project_root
slice_id
objective
allowed_files
forbidden_files
locked_resources
required_artifact_refs
artifact_summaries
dev_server_url
verification_level
acceptance_criteria
return_manifest_schema
```
