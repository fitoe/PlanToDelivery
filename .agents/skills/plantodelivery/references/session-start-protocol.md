# Session Start Protocol

Use at the start of every `PlanToDelivery` session, including new projects, resumed projects, and interrupted work.

Main rule:
- do not act on the user's latest request until the Hermes Kanban board/card state, owner capability/provider, Kanban constraint state, and next Kanban-allowed action are known.

---

## Startup Order

1. Inspect repository state.
2. Inspect Hermes Kanban board/card/DAG state.
3. Read durable overlays/evidence if present.
4. Determine current owner capability/provider.
5. Determine current Kanban constraint state.
6. Determine next Kanban-allowed action.
7. Only then continue work.

---

## State And Evidence To Check

Canonical execution state:
- Hermes Kanban board and current card status
- card dependencies/links
- card comments or metadata containing `P2D_META`
- task envelope and active-slice digest paths referenced by the card
- latest result manifest, review evidence, blocker note, or approval evidence referenced by the card

Durable overlays/evidence, when present:
- `project-state/kanban/**`
- `.hermes/project-state/current-state.md`
- `.hermes/project-state/active-slice.json`
- `.hermes/project-state/artifact-index.json` or equivalent manifest
- `.hermes/project-state/decision-log.md`
- `.hermes/project-state/verification-ledger.md`

Legacy orchestrator state is fallback evidence only, not execution authority:
- `docs/orchestrator/project-state.json`
- `docs/orchestrator/session-brief.md`
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/artifact-manifest.json`
- `docs/orchestrator/approval-records.json`
- latest file under `docs/orchestrator/gate-checks/`
- active milestone task state

Read only the smallest files needed to determine Kanban state, owner, constraint, and next action. Do not load specialist artifacts until the owner capability/provider is selected.

If these files are missing in a new project:
- create or repair the Hermes Kanban board/card metadata first
- keep JSON/project-state as evidence/export only
- do not execute provider work from chat history or a local JSON status

---

## Required Startup Output

At session start, establish:
- current Hermes Kanban board/card/DAG state
- current milestone/slice, if any
- current owner capability/provider
- current Kanban constraint: `ready`, `running`, `review`, `blocked`, `done`, `n/a`, or `unknown`
- blocked/review reason, if any
- next Kanban-allowed action
- durable evidence file/card metadata that must be updated next

Keep this concise. Do not dump full process theory.

---

## New Project Behavior

For a new project:
- create or select the Hermes Kanban board
- create intake/discovery/planning cards and dependency links before implementation cards
- record first-order decisions as card evidence and durable overlays
- if UI/product design is needed, route through design capability cards before implementation capability cards
- do not enter implementation until the implementation card is unblocked/claimable through Hermes Kanban and required design/planning evidence is referenced

---

## Resume Behavior

For resumed work:
- trust Hermes Kanban lifecycle over chat memory and project-local JSON
- use durable overlays/evidence to explain or repair card state, not to bypass it
- if state is stale or contradictory, repair Kanban card metadata/evidence first
- if latest user request conflicts with current Kanban constraint, record/return the blocked or review state
- do not skip to implementation based on conversation pressure

---

## Missing State Behavior

If Hermes Kanban state is missing but repo has code or docs:
- inspect existing docs/code only enough to reconstruct current slice
- create/repair the board/cards, task envelopes, and active-slice digest
- build or update `current-state.md` / `gap-analysis.md` as evidence overlays if useful
- do not treat existing `project-state.json` as canonical execution state

If durable state is missing and repo is empty:
- start from discovery/intake cards
- record assumptions and first-order decisions as Kanban evidence

---

## Owner Capability Selection

Use:
- `PlanToDelivery` for Hermes Kanban orchestration, roadmap, milestone planning, verification, result ingestion, progress, and handoff
- `idea-to-design` for product design docs, page planning, visual direction, design images
- `design-to-code` for approved design image to code implementation

Equivalent external artifacts may satisfy owner outputs if manifests, approvals, and evidence paths are valid and referenced by the Kanban card.

---

## Startup Constraint

Before doing substantial work, answer:

```md
Session Start
- Kanban:
- Owner capability/provider:
- Constraint:
- Next Kanban-allowed action:
- Must update:
```

If any value is unknown, the next Kanban-allowed action is to inspect or repair Hermes Kanban state/evidence.
