# Orchestration Core

Use this file when deciding routing, artifact validity, Kanban constraint state, review/block handling, or cross-provider handoff. It is the compact entry for orchestration rules. Load detailed references only when this file is not enough.

## Owner Model

- `PlanToDelivery` owns Hermes Kanban orchestration: board/card state, lifecycle constraints, durable overlays, routing, provider dispatch, result ingestion, and handoff.
- `idea-to-design` is the recommended owner for product design, route/page planning, design brief, visual directions, page images, and design documentation.
- `design-to-code` is the recommended owner for converting approved persisted design sources into high-fidelity implementation.
- Recommended owner does not mean exclusive source. Equivalent artifacts are valid if they satisfy the same Kanban evidence requirements.

## Artifact Contract

Orchestration depends on durable artifacts and Hermes Kanban state, not on a specific skill implementation.

Valid equivalents include:

- `Design-Spec.md` or equivalent product/design document
- `state.json` or equivalent resumable design state
- approved design assets or equivalent persisted visual source
- approved section breakdown or equivalent implementation-ready page segmentation
- `Pre-Implementation Brief` or equivalent code-facing design brief
- `kanban-capability-result/v1` result manifest for provider completion/review/block outcomes

Artifacts must be repository-persisted. Chat-only output, temp files, unrecorded tool output, and project-local JSON status do not authorize execution.

## Kanban Constraint Rule

Hermes Kanban is the only execution constraint for V2 orchestration.

Each active card is interpreted through the Kanban lifecycle:

- `todo` / `ready`: not yet claimed or ready to claim when dependencies are satisfied
- `running`: claimed work may execute within the task envelope and active-slice digest
- `review`: provider output exists and requires evidence-based approval before downstream unlock
- `blocked`: missing input, contradictory requirement, unsafe/destructive action, auth/permission, secret, or external dependency
- `done`: accepted result manifest and evidence have been recorded; downstream dependencies may unlock

Do not use a separate Gate status to authorize work. Former gate language maps to Kanban dependencies, review, block reasons, acceptance evidence, and done transitions.

A task may advance only when the Hermes Kanban transition is valid. JSON/local overlays, SQLite exports, project-state files, and chat summaries are evidence/export/debug layers only.

Kanban decisions should name:

- board/card id and lifecycle state
- owner capability/provider
- required artifacts/evidence
- result manifest or blocker/review evidence paths
- decision/outcome
- next Kanban-allowed action

## Startup Rule

At session start, decide before doing work:

- current Hermes Kanban board/card/DAG state
- current owner capability/provider
- current Kanban constraint state
- next Kanban-allowed action
- durable evidence used

Prefer loading `quick-start.md`, Hermes Kanban state, project-state overlays, and latest result/review/block evidence before detailed references.

## Blocking Scenarios

- No Hermes Kanban board/card for real V2 execution: block real execution; create/repair the board/card metadata instead of running from chat.
- Card is not `running`: do not execute provider work; claim or transition through Hermes Kanban first.
- Idea-only request to start coding: create product/planning/design cards and dependencies before implementation cards.
- UI coding with no approved persisted design source: block implementation card and route to design or collect equivalent approved source.
- UI coding with design source but no section breakdown or brief: create/repair the missing implementation-ready artifact/card dependency.
- Approved image exists only in chat or temp folder: block implementation until it is persisted and referenced by the card/manifest.
- User asks to skip a constraint: allow only by recording explicit approval/risk as Kanban evidence and moving through the appropriate Kanban transition.
- Existing equivalent artifact exists: accept it if evidence satisfies the card; do not force a specific skill rerun.

## Context Budget

Use this order to save tokens:

1. Hermes Kanban board/card state
2. active task envelope and active-slice digest
3. latest result manifest, review evidence, blocker note, and project-state overlay
4. compact orchestration core
5. capability/stage-specific reference
6. exact template being written
7. historical docs only when there is a contradiction or missing decision

Do not read all references, all templates, or all historical artifacts by default.

## Speed Rules

- Do not re-ask confirmed first-order decisions.
- Do not re-run design or planning when equivalent approved artifacts exist.
- Do not expand a milestone beyond the closed scope.
- Use detailed references only when Kanban state, ownership, dependency, review, block, or artifact evidence is ambiguous.
- Prefer patching missing evidence/card metadata over rewriting complete documents.
