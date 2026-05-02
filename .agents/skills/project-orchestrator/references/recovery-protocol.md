# Recovery Protocol

Use this file when resuming work in a new session or after interruption.

## Primary Resume Order

1. Read `docs/orchestrator/session-brief.md`
2. Read active milestone task state
3. Read `decision-log.md`
4. Read active milestone plan/spec only as needed
5. Cross-check current repo state
6. Resume the exact next recorded action

## Recovery Rules

- Durable docs beat memory.
- Git is cross-check, not sole truth.
- If durable docs are stale or contradictory, return to `intake`.
- Do not re-expand the whole project unless resume state is unreliable.

## Required Session-End State

Before stopping, ensure:

- current stage is recorded
- active milestone is recorded
- current task is recorded
- last verification state is recorded
- blockers are explicit
- persistent processes are recorded if any
- next exact action is recorded
