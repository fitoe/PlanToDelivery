# Kanban Capability Envelope v1

This document defines the neutral contract between the kanban-aware orchestrator and decoupled provider skills.

## Purpose

PlanToDelivery/Javis dispatches work by capability. Providers implement capabilities and return manifests. Neither side imports the other side's internals.

## Task Envelope

Stage-admission Gates are Kanban-owned. If the task determines whether a downstream phase may start, create/require a Hermes Kanban review card and link downstream work to it; do not rely on local JSON, markdown manifests, or provider prose as the unlock authority.

```json
{
  "schema_version": "kanban-capability-task/v1",
  "task_id": "kb_123",
  "correlation_id": "project-stage-task",
  "capability": "visual_implementation",
  "objective": "Implement approved visual source",
  "inputs": {
    "project_path": "/absolute/path",
    "source_artifacts": [],
    "requirements": [],
    "constraints": [],
    "acceptance_criteria": []
  },
  "orchestration": {
    "origin": "kanban",
    "stage": "implementation",
    "priority": "normal",
    "review_policy": "required_before_children"
  }
}
```

### Required Fields

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | yes | Must be `kanban-capability-task/v1`. |
| `task_id` | yes | Kanban task identifier. |
| `correlation_id` | yes | Stable cross-provider trace ID. |
| `capability` | yes | Capability requested by orchestrator. |
| `objective` | yes | Human-readable outcome. |
| `inputs` | yes | Provider-specific input bundle. |
| `orchestration.origin` | yes | Usually `kanban`; metadata only for providers. |
| `orchestration.review_policy` | no | Hint for expected review behavior. |

## Result Manifest

```json
{
  "schema_version": "kanban-capability-result/v1",
  "task_id": "kb_123",
  "correlation_id": "project-stage-task",
  "capability": "visual_implementation",
  "status": "completed",
  "summary": "Implemented approved page and captured evidence.",
  "artifacts": [],
  "changed_files": [],
  "evidence": [],
  "review_required": false,
  "blocked": false,
  "blockers": [],
  "debt": [],
  "next_tasks": []
}
```

### Result Status Values

- `completed`: Provider produced the requested output and evidence for Javis to ingest.
- `partial`: Provider produced useful output but needs review or continuation.
- `failed`: Provider attempted and could not produce useful output.

Provider manifests are recommendations. `next_tasks`, `suggested_kanban_updates`, or similar fields must not mutate canonical state by themselves; Javis must convert accepted recommendations into Hermes Kanban cards, links, reviews, comments, and completion events before downstream work is unlocked.

### Review vs Blocker Rule

`review_required` and `blocked` are semantically different:

- `review_required=true` means the work is ready for the Hermes Kanban review/approval flow.
- `blocked=true` means the provider cannot proceed because required inputs, credentials, external systems, or non-contradictory prerequisites are missing.
- Normal approval, parity, design, or architecture review must not be reported as `blocked`.

## Provider Manifest Reference

Providers declare capabilities through `provider-manifest/v1`. The orchestrator consumes those manifests through a registry. Provider IDs are metadata, not hard-coded branch conditions.

## Validation Checklist

- Task schema version is exact.
- Capability is non-empty and matches provider manifest.
- `review_required` and `blocked` are not conflated.
- Artifacts and evidence use paths or URLs the orchestrator can surface.
- Next tasks use capability names, not implementation names.
