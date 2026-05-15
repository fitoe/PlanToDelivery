# Quick Start

Use this file at the start of every `PlanToDelivery` session.

Goal: restore control with the smallest possible context before doing work.

## Startup Checklist

1. Determine current stage.
2. Read durable project state if it exists.
3. Identify the current owner skill.
4. Check the latest gate evidence.
5. State the next allowed action before implementation.

## Minimal Load Order

Load only what is needed:

1. `quick-start.md`
2. `docs/orchestrator/project-state.json`, if present
3. latest `docs/orchestrator/session-brief.md`, if present
4. latest gate check or approval record, if present
5. `references/orchestration-core.md`, only when routing, gates, or artifact validity must be decided
6. one stage-specific reference, only after the stage is known
7. one template, only when creating or updating that exact artifact

Do not load all references or all templates during startup.

## Required Startup Output

Before doing substantive work, report:

- `stage`: current stage or best inferred stage
- `owner`: `PlanToDelivery`, `idea-to-design`, `design-to-code`, or another stage-bounded skill
- `gate`: `pass`, `fail`, `n/a`, or `unknown`
- `next`: next allowed action
- `evidence`: durable files or missing files used to decide

If gate is `fail` or `unknown`, do not advance to execution. Repair the missing artifact or ask only for the first-order decision that blocks progress.

## Fast Path

When state is complete and gates pass:

- do not re-open old completed planning unless new contradictions appear
- do not ask the user to reconfirm previously approved first-order decisions
- move directly to the next stage action

When state is missing:

- create or repair only the smallest required artifact
- prefer a session brief over reloading long historical documents
- preserve existing decisions unless evidence shows they are obsolete
