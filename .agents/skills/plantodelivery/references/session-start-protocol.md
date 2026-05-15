# Session Start Protocol

Use at the start of every `PlanToDelivery` session, including new projects, resumed projects, interrupted work, and `贾维斯继续` requests.

Main rule:
- do not act on the user's latest request until project root, current stage, current task/slice, owner skill, latest gate, blockers, and next allowed action are known.

Low-token mode may reduce how much history is read. It must not reduce the startup checks.

---

## Startup Order

1. Verify repository identity: root path, git status, and user-named project mapping.
2. Read authoritative durable state.
3. Detect stale, missing, or conflicting state systems.
4. Determine current stage.
5. Determine current task/slice and owner skill.
6. Determine latest relevant gate and blocking approvals.
7. Determine next allowed action.
8. Only then continue work.

If any value is unknown or contradictory, the next allowed action is `inspect_or_repair_state`.

---

## Durable State Priority

Read the smallest authoritative state first:

1. Preferred portable state:
   - `project-state/execution-progress.json`
   - `project-state/artifact-manifest.json`
   - `project-state/execution-progress.schema.json`
   - `project-state/artifact-manifest.schema.json`
   - `scripts/check-project-state.py`
2. Fallback only when `project-state/` is absent:
   - `.hermes/project-state/current-state.md`
   - `.hermes/project-state/active-slice.json`
   - `.hermes/project-state/artifact-index.json` or equivalent manifest
   - `.hermes/project-state/decision-log.md`
   - `.hermes/project-state/verification-ledger.md`
3. Legacy fallback only when the above are absent:
   - `docs/orchestrator/project-state.json`
   - `docs/orchestrator/session-brief.md`
   - `docs/orchestrator/current-state.md`
   - `docs/orchestrator/artifact-manifest.json`
   - `docs/orchestrator/approval-records.json`
   - latest file under `docs/orchestrator/gate-checks/`
   - active milestone task state

If more than one state system exists and they disagree about stage, current task, gate, blocker, approval, or next action, stop and repair/reconcile state before implementation.

Read only the smallest files needed to determine startup values. Do not load specialist artifacts until the owner skill is selected.

---

## Required Startup Output

At session start, establish:

```md
Session Start
- Project root:
- Stage:
- Current task/slice:
- Owner skill:
- Latest gate:
- Blocked reason:
- Next allowed action:
- Must update:
```

Keep it concise. Do not dump full process theory.

---

## New Project Behavior

For a new or unclear project:

- enter `intake`
- create or plan missing durable state
- clarify project goal and first-order decisions
- if UI/product design is needed, route to `idea-to-design`
- do not enter implementation until gates pass

Do not initialize new project state directly in `execution`.

---

## Resume Behavior

For resumed work:

- trust authoritative durable state over chat memory
- run the project-state validator when formal `project-state/` exists
- if state is stale or contradictory, repair state first
- if latest user request conflicts with current gate, output blocked gate check
- do not skip to implementation based on conversation pressure

---

## Missing State Behavior

If durable state is missing but repo has code or docs:

- inspect existing docs/code
- build or refresh durable current state
- build a gap analysis if the stage is unclear
- create `project-state/` if a formal implementation plan exists

If durable state is missing and repo is empty:

- start from `intake`
- record assumptions and first-order decisions

---

## Owner Skill Selection

Use:

- `PlanToDelivery` for orchestration, gates, roadmap, milestone planning, verification, handoff, progress state, and final gate decisions
- `idea-to-design` for product design docs, page planning, visual direction, design images, Visual Freeze, and Post-Visual Extraction
- `IdeaToTech` for API/state/dependency/mock-to-real/security/performance/verification decisions that must be fixed before implementation
- `design-to-code` for approved visual-source/blueprint-driven UI implementation and parity repair

Equivalent external artifacts may satisfy owner outputs only when manifests, approvals, and evidence paths are valid.

---

## Startup Gate

Before doing substantial work, answer the Required Startup Output. If any value is unknown, the next allowed action is to inspect or repair durable state.
