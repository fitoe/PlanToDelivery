# Quick Start

Use this file at the start of every `PlanToDelivery` session.

Goal: restore Kanban control with the smallest possible context before doing work.

## Startup Checklist

1. Identify the Hermes Kanban board and current card/DAG state.
2. Read durable project state if it exists.
3. Identify the current owner capability/provider.
4. Check the latest result manifest, approval evidence, blockers, and card comments.
5. State the next Kanban-allowed action before implementation.

## Minimal Load Order

Load only what is needed:

1. `quick-start.md`
2. Hermes Kanban board/card state for the project
3. `project-state/kanban/**` or `.hermes/project-state/**`, if present
4. latest result manifest, approval evidence, or blocker note, if present
5. `references/orchestration-core.md`, only when routing, artifact validity, review, or blocker handling must be decided
6. one capability/stage-specific reference, only after the active card is known
7. one template, only when creating or updating that exact artifact

Do not load all references or all templates during startup.

## Required Startup Output

Before doing substantive work, report:

- `kanban`: board/card status and whether backend execution is active
- `owner`: `PlanToDelivery`, `idea-to-design`, `design-to-code`, or another capability-bounded provider
- `constraint`: `ready`, `running`, `review`, `blocked`, `done`, `n/a`, or `unknown`
- `next`: next Kanban-allowed action
- `evidence`: durable files, result manifests, card comments, or missing evidence used to decide

If the Kanban constraint is `review`, `blocked`, or `unknown`, do not advance to implementation. Repair the missing artifact/metadata when possible, or ask only for the first-order decision that blocks progress.

## Fast Path

When Kanban state is clear and required evidence exists:

- do not re-open old completed planning unless new contradictions appear
- do not ask the user to reconfirm previously approved first-order decisions
- move directly to the next Kanban-allowed action

When state is missing:

- create or repair only the smallest required artifact/card metadata
- prefer a session brief over reloading long historical documents
- preserve existing decisions unless evidence shows they are obsolete
