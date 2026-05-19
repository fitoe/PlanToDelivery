# Kanban Gate Policy v1

This policy defines how PlanToDelivery maps provider results into kanban task states.

## Canonical States

- `ready`: task can be assigned.
- `in_progress`: worker/provider is executing.
- `review`: output exists but requires review before downstream unlock.
- `blocked`: task cannot proceed due to missing prerequisite or external dependency.
- `done`: task is complete and can unlock children.

## Gate Types

### Pre-flight Gate

Before dispatch:
- task envelope validates;
- provider exists for capability;
- required inputs are present;
- project path/artifact paths are reachable if applicable.

Failure behavior:
- missing provider/input/artifact -> `blocked`;
- ambiguous provider tie -> `review`/escalation.

### Revision Gate

After provider returns `review_required=true`:
- move task to `review`;
- do not unlock child tasks yet;
- review may approve, request changes, or create follow-up tasks.

### Escalation Gate

Use when provider confidence is low, provider choice is ambiguous, or architectural/design decision requires human or stronger-model judgment.

Failure behavior:
- keep task in `review` until decision;
- do not mark as `blocked` unless required information is unavailable.

### Abort Gate

Use when continuing would be destructive, unsafe, or impossible.

Failure behavior:
- move to `blocked` with explicit blocker reason;
- preserve artifacts and partial evidence.

## Provider Result Mapping

| Result condition | Kanban transition | Child unlock |
|---|---|---:|
| `blocked=true` | `blocked` | no |
| `review_required=true` | `review` | no |
| `status=completed` and no review/block | `done` | yes |
| `status=partial` with useful artifacts | `review` | no |
| `status=failed` with retryable issue | `ready` or `blocked` after policy decision | no |

## Review Completion

When review approves:
- record approval evidence;
- transition `review` -> `done`;
- unlock dependent tasks whose prerequisites are now satisfied.

When review requests changes:
- create or update a revision task;
- keep original task in `review` or move to `ready` depending on implementation mechanics;
- do not mark as `blocked` unless work cannot proceed.

## Blocker Criteria

Use `blocked` only for:
- missing source artifact;
- missing credential/token/user-provided secret;
- unreachable required external system;
- contradictory requirements that cannot be resolved by provider;
- no registered provider for requested capability;
- destructive action requiring explicit user approval.

Do not use `blocked` for:
- normal design approval;
- code review;
- visual parity review;
- architecture review;
- low confidence that can be escalated.
