# Javis Provider Runtime v1

## 1. Purpose

Provider Runtime dispatches bounded capability work to manual, subagent, command, or builtin providers and ingests results into canonical Hermes Kanban state plus P2D evidence overlays.

PlanToDelivery matches by capability, not by provider identity.

## 2. Provider types

```text
manual
subagent
command
builtin
```

- `manual`: create task envelope for human/main-agent execution.
- `subagent`: dispatch bounded TaskExecutionContext to a worker agent.
- `command`: run declared command for deterministic work such as crop, screenshot, build, or test.
- `builtin`: internal PlanToDelivery runtime such as Kanban evidence projection, artifact indexing, snapshot generation.

## 3. Provider registry

Provider registry records:

```text
provider_id
manifest_path
capabilities
execution_mode
priority
enabled
constraints
```

Selection factors:

- capability match;
- enabled status;
- priority;
- resource locks;
- historical failures;
- task type;
- user/project preferences.

## 4. Task envelope

Dispatch creates a `kanban-capability-task/v1` artifact.

Minimum fields:

```json
{
  "schema": "kanban-capability-task/v1",
  "task_id": "",
  "capability": "",
  "project_root": "",
  "slice_id": "",
  "objective": "",
  "input_artifact_refs": [],
  "artifact_summaries": [],
  "allowed_files": [],
  "forbidden_files": [],
  "locked_resources": [],
  "dev_server_url": "",
  "verification_level": "dev_loop",
  "acceptance_criteria": [],
  "return_manifest_schema": "kanban-capability-result/v1"
}
```

Task envelope describes need and boundaries, not provider internals.

## 5. Task ready conditions

A task can become `ready` only when:

- upstream Hermes Kanban dependencies/reviews are approved or waived;
- required artifact refs exist;
- provider is available;
- allowed and forbidden files are explicit;
- resource locks are available;
- dev server state satisfies the task;
- verification level is defined;
- retry limit is not exceeded.

## 6. Dispatch lifecycle

```text
backlog -> ready -> dispatched -> running -> review -> completed
```

Exception paths:

```text
running -> blocked
running -> failed
failed -> retrying -> running
running -> partial -> review/completed/backlog
review -> completed
review -> retrying
blocked -> ready/cancelled
```

## 7. Result manifest

Providers return `kanban-capability-result/v1`.

Minimum fields:

```json
{
  "schema": "kanban-capability-result/v1",
  "task_id": "",
  "capability": "",
  "provider": "",
  "result": "completed",
  "changed_files": [],
  "produced_artifacts": [],
  "evidence": [],
  "blockers": [],
  "debts": [],
  "review_required": false,
  "suggested_kanban_updates": [],
  "next_recommended_task": null
}
```

Allowed `result` values:

```text
completed
partial
blocked
failed
```

## 8. Result ingest

Ingest MUST:

1. Validate schema.
2. Validate task id and capability.
3. Record produced artifact refs.
4. Record changed files and evidence.
5. Update task engine status.
6. Apply or queue suggested Kanban lifecycle/evidence updates.
7. Create review, blocker, debt, or next-task records as needed.
8. Append events.
9. Update board projections.

Providers MUST NOT bypass Hermes Kanban claim/review/block/complete transitions.

## 9. Review handling

If `review_required=true`, task status becomes `review`, not `blocked`.

Review outcomes:

```text
approve -> completed
request_changes -> retrying/backlog
reject -> failed/cancelled
split_followup -> create new task
```

## 10. Blocked handling

Blocked is valid only for missing prerequisite, external dependency, contradiction, unsafe/destructive action, auth/permission issue, secret need, or impossible input.

Blocking scope should be local to the affected Slice unless a project-level blocker exists.

## 11. Retry handling

Before retry, record:

- failure type;
- evidence;
- changed retry strategy;
- provider selection decision;
- whether task should be split;
- whether the affected Kanban card/dependency should roll back.

No infinite retries.

## 12. Subagent boundary

Subagents receive TaskExecutionContext only. They MUST NOT receive full chat history by default.

Subagents MUST NOT:

- change forbidden files;
- modify shared resources without locks;
- start duplicate dev servers;
- skip gates;
- treat mock/local fallback as real completion unless accepted;
- lower high-fidelity targets;
- delete or overwrite approved artifacts;
- silently change approved blueprint decisions.

## 13. Controlled parallelism

Allowed parallel work:

- different slices;
- non-overlapping files;
- no shared resource conflicts;
- no dependency on the same pending Kanban dependency/review;
- read-only shared artifacts.

Disallowed parallel work:

- same page/area;
- same route config;
- same shared component;
- same global style/token file;
- same API client/state store;
- same dev server config;
- same dependency/build config.

## 14. Dev server policy

Providers MUST query project dev server state before starting a process.

Healthy server: reuse.
Unknown server: health check.
Unhealthy/stopped server: restart/start only through DevServer Manager and append event.
