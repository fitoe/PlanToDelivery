# Session Start Protocol

Use at the start of every `PlanToDelivery` session, including new projects, resumed projects, and interrupted work.

Main rule:
- do not act on the user's latest request until current stage, owner skill, gate status, and next allowed action are known

---

## Startup Order

1. Inspect repository state
2. Read durable state if present
3. Determine current stage
4. Determine current owner skill
5. Determine latest gate status
6. Determine next allowed action
7. Only then continue work

---

## Files To Check

Prefer low-token project state first:
- `project-state/current-state.md`
- `project-state/active-slice.json`
- `project-state/artifact-manifest.json`
- `project-state/decision-log.md`
- `project-state/verification-ledger.md`

Use legacy orchestrator state as fallback when present:
- `docs/orchestrator/project-state.json`
- `docs/orchestrator/session-brief.md`
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/artifact-manifest.json`
- `docs/orchestrator/approval-records.json`
- latest file under `docs/orchestrator/gate-checks/`
- active milestone task state

Read only the smallest files needed to determine stage, owner, gate, and next action. Do not load specialist artifacts until the owner skill is selected.

If these files are missing in a new project:
- stay in `intake`
- create or plan the missing durable state before later stages

---

## Required Startup Output

At session start, establish:
- current stage
- current milestone, if any
- current owner skill
- latest gate decision
- blocked reason, if any
- next allowed action
- durable file that must be updated next

Keep this concise. Do not dump full process theory.

---

## New Project Behavior

For a new project:
- enter `intake`
- create initial durable state
- clarify project goal and first-order decisions
- if UI/product design is needed, route to `idea-to-design`
- do not enter implementation until gates pass

---

## Resume Behavior

For resumed work:
- trust durable state over chat memory
- if state is stale or contradictory, repair state first
- if latest user request conflicts with current gate, output blocked gate check
- do not skip to implementation based on conversation pressure

---

## Missing State Behavior

If durable state is missing but repo has code or docs:
- inspect existing docs/code
- build `current-state.md`
- build `gap-analysis.md`
- write initial `project-state.json` if artifact-driven workflow is in use

If durable state is missing and repo is empty:
- start from `discovery`
- record assumptions and first-order decisions

---

## Owner Skill Selection

Use:
- `PlanToDelivery` for orchestration, gates, roadmap, milestone planning, verification, handoff
- `idea-to-design` for product design docs, page planning, visual direction, design images
- `design-to-code` for approved design image to code implementation

Equivalent external artifacts may satisfy owner outputs if manifests, approvals, and evidence paths are valid.

---

## Startup Gate

Before doing substantial work, answer:

```md
Session Start
- Stage:
- Owner skill:
- Latest gate:
- Next allowed action:
- Must update:
```

If any value is unknown, the next allowed action is to inspect or repair durable state.
