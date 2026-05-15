---
name: PlanToDelivery
description: Use when orchestrating a project from idea or plan through staged delivery, checkpoints, skill routing, gates, progress reporting, and handoff.
---

# Plan To Delivery

## Purpose

PlanToDelivery is the persistent orchestrator for project delivery. It owns stage state, gates, task selection, progress reporting, checkpoint discipline, and final handoff claims. It routes specialist work, but it does not silently replace specialist workflows or skip their gates.

## Non-Skippable Operating Rules

These rules are mandatory even in low-token mode:

1. **Session start gate first.** Before acting on a project request, determine: project root, current stage, current task/slice, owner skill, latest relevant gate, blockers, and next allowed action.
2. **Unknown means inspect/repair.** If any startup value is unknown, stale, contradictory, or missing, the next allowed action is to inspect or repair durable state, not to implement.
3. **No silent stage skipping.** A stage may be skipped only when durable repository state proves its required outputs already exist, are still valid, and any required gate is `passed` or `waived` with evidence.
4. **Low-token is not low-rigor.** Reduce reading volume, not process steps. Never skip gate checks, state validation, approval checks, or required verification because of token budget.
5. **Completion requires evidence.** Do not claim a task, milestone, UI parity, release, or handoff is complete without fresh evidence or an explicit recorded waiver.
6. **Project-state is authoritative when present.** Prefer project-root `project-state/` over `.hermes/project-state/` and legacy `docs/orchestrator/`. If multiple state systems exist and conflict, repair or reconcile state before continuing.

## Canonical Stage Machine

Use these stage names consistently:

1. `intake`
2. `discovery`
3. `product-definition`
4. `ui-definition` when UI-bearing
5. `system-definition`
6. `decision-closure`
7. `roadmap`
8. `milestone-spec`
9. `milestone-plan`
10. `execution`
11. `debugging` when needed
12. `verification`
13. `handoff`
14. `done`

Major transitions require a gate record. Do not skip gates because implementation “looks done”.

## Startup Protocol

For every resumed project, new project, or `贾维斯继续` request:

1. Verify repository identity: root path, git status, and whether the user-named project matches the root.
2. Load the smallest authoritative state:
   - first: `project-state/execution-progress.json` and `project-state/artifact-manifest.json`;
   - fallback only if absent: `.hermes/project-state/current-state.md`, `.hermes/project-state/active-slice.json`, `.hermes/project-state/artifact-index.json`;
   - legacy fallback only if both above are absent: `docs/orchestrator/*`.
3. If an implementation plan exists, ensure `project-state/` exists, schemas are present, and `scripts/check-project-state.py` can validate it, unless a waiver is recorded.
4. Establish and, when useful, report:

```md
Session Start
- Stage:
- Current task/slice:
- Owner skill:
- Latest gate:
- Blocked reason:
- Next allowed action:
- Must update:
```

If the next allowed action is not known, inspect/repair state. If a requested action conflicts with a blocking gate, report the gate instead of proceeding.

## Progress-Driven Execution Contract

Use project-root `project-state/` as the portable execution state layer whenever a formal implementation plan exists.

Required files:

- `project-state/execution-progress.json`
- `project-state/execution-progress.schema.json`
- `project-state/artifact-manifest.json`
- `project-state/artifact-manifest.schema.json`
- `scripts/check-project-state.py`, unless explicitly waived

`execution-progress.json` tracks:

- `source_plan`: implementation plan path and status
- `current`: stage, milestone/phase, task id, next task id, next action
- `selection_policy`: default `dependency_priority_order`
- `tasks`: separated `task_status`, `verification_status`, `commit_status`, `user_confirmation_status`, dependency/gate/blocker refs, routing, artifact refs
- `gates`: transition/handoff gates with required artifacts and checks
- `blockers`: lifecycle blockers with owner, severity, resolution requirement, affected tasks
- `checkpoints`: meaningful commits/releases/handoffs with evidence
- `events`: audit trail for key progress changes

Default task statuses: `pending`, `ready`, `in_progress`, `blocked`, `needs_rework`, `completed`, `skipped`, `failed`.
Default verification statuses: `not_required`, `not_started`, `running`, `passed`, `failed`, `waived`.
Default commit statuses: `not_required`, `not_committed`, `committed`, `pushed`, `waived`.
Default user confirmation statuses: `not_required`, `required`, `requested`, `approved`, `changes_requested`, `waived`.

## Task Selection Policy

When choosing the next task:

1. Continue `current.task_id` only if its `task_status` is `in_progress`, `ready`, or `pending`, and its blockers/gates do not block continuation.
2. Otherwise choose tasks whose `task_status` is `ready`, `pending`, or `needs_rework`.
3. Dependencies must be `completed`, `skipped`, or explicitly waived through gate/waiver evidence.
4. Referenced blockers must be `resolved` or `waived`.
5. Required gates must be `passed` or `waived`.
6. User confirmation must not be `required`, `requested`, or `changes_requested` unless the next action is to request/resolve that confirmation.
7. Sort eligible tasks by `priority`, then `order`.
8. If no task is eligible and unresolved blockers exist, report blockers instead of retrying blindly.

Never mark a task `skipped`, `completed`, or gate `passed` just to make a later task eligible. Record an explicit waiver/deviation when bypassing expected work.

## Gate Checks

Before major transitions, record a gate decision with:

- stage transition or task/handoff being evaluated
- required artifacts and whether each is `pass`, `fail`, or `n/a`
- required approvals and confirmations
- blockers and waivers
- allowed vs blocked decision
- owner of the next step
- evidence paths, commands, screenshots, commits, or explicit waiver

Hard-block on:

- destructive changes without scope confirmation
- secrets/token persistence
- unknown auth/permission requirements for real API work
- requested user confirmation not yet approved or waived
- entering execution without milestone spec, milestone plan, test/verification plan, and execution entry gate
- claiming completion without verification or waiver
- UI implementation without approved visual source and valid UI handoff path
- design parity claims without design source and visual evidence

## UI and Specialist Routing

PlanToDelivery owns routing and gate decisions. Specialists own their domain outputs.

- Use `idea-to-design` for product/visual exploration, visual source approval, Visual Freeze, Post-Visual Extraction, and Level 3 handoff.
- Use `IdeaToTech` for API/state/dependency/mock-to-real/platform/security/performance decisions, feature recipes, or verification strategy that must be fixed before coding.
- Use `design-to-code` only after approved design/handoff for implementation, Visual IR, `data-section`, screenshots, section parity, and visual repair.
- Use framework/domain skills only for concrete implementation details required by the active task.

UI handoff boundary:

- After user-approved visual source + Visual Freeze + Post-Visual Extraction + implementation-ready handoff, routine UI implementation goes to `design-to-code`.
- Return to `idea-to-design` only for missing, stale, conflicting, or changed design source, missing post-visual extraction, product changes, or requested redesign.
- For flat PNG/GPT Image sources, prefer Visual IR + section parity evidence over prose-only briefs.
- A route smoke test or build pass is not final UI parity evidence.

## Low-Token Routing Protocol

When the user invokes `贾维斯`, `贾维斯继续`, `低 token 模式`, or asks to continue a project, default to low-token orchestration:

1. Keep `PlanToDelivery` as the persistent owner until a gate requires a specialist.
2. Restore authoritative durable state first; do not browse broad docs if `project-state/` is valid and sufficient.
3. Recover only active task/slice, blockers, required gates, referenced artifacts, and next allowed action.
4. Load at most one specialist skill by default, and only when the current gate/task explicitly requires it.
5. Pass specialists compact briefs with artifact refs and allowed files; require delta summaries, not narratives.
6. Verify specialist-proposed files/evidence before merging progress or manifest updates.
7. Save heavy outputs to `project-state/design/`, `project-state/tech/`, `project-state/implementation/`, `project-state/evidence/`, or another declared artifact path.
8. Keep each execution loop scoped to one slice: one feature, page, route, section, repair pass, or integration seam.

Default specialist invocation brief:

```json
{
  "active_task": "T-xxx",
  "scope": "route-or-section-or-feature",
  "required_skill": "design-to-code",
  "input_artifact_refs": ["artifact.id"],
  "allowed_files": ["path/or/glob"],
  "expected_outputs": ["artifact_kind_or_path"],
  "budgets": {
    "read_files_max": 8,
    "browser_snapshots_max": 2,
    "vision_outputs_inline": false,
    "repair_gaps_max": 3
  }
}
```

Default specialist delta response:

```json
{
  "result": "completed | partial | blocked",
  "changed_files": [],
  "produced_artifacts": [],
  "suggested_manifest_entries": [],
  "suggested_progress_updates": [],
  "suggested_blockers": [],
  "suggested_gate_updates": [],
  "evidence": [],
  "largest_remaining_gaps": [],
  "next_recommended_task": ""
}
```

The delta is a proposal. PlanToDelivery verifies and performs final gate checks.

## Progress Reporting Standard

For Weixin/project checkpoints, include:

- status label
- backend execution: yes/no
- completed in the last window
- current action
- next step
- next expected report

Batch updates; avoid noisy micro-messages. Routine user questions are inserted communication, not a reason to stop the workflow unless the user explicitly pauses or changes direction.

## Verification Discipline

During active implementation, avoid expensive broad checks after every edit unless needed. At checkpoints/gates, run the narrowest relevant verification first, then broader checks when release/merge readiness is claimed.

Report skipped checks as skipped, waived checks as waived, failed baseline checks as baseline/debt, and passed checks only when they actually ran or have explicit evidence.

## Progressive Loading

Load only when needed:

- `references/session-start-protocol.md` — startup details when state is missing, stale, or contradictory
- `references/workflow.md` — full stage workflow
- `references/stage-gates.md` — detailed gate matrix
- `references/skill-routing.md` — detailed routing by stage
- `references/cross-skill-contracts.md` — contracts with IdeaToDesign/DesignToCode/IdeaToTech
- `references/testing-strategy.md` — verification strategy
- `references/efficiency-rules.md` — low-token/low-cost execution rules
- `references/vue-progress-overlay.md` — progress overlay implementation
- `templates/index.md` — artifact templates
- `templates/execution-progress-template.json` — portable progress-driven state template
- `templates/artifact-manifest-template.json` — portable artifact registry template
- `templates/execution-progress.schema.json` — progress state schema
- `templates/artifact-manifest.schema.json` — artifact registry schema
- `scripts/check-project-state.py` — portable validator
- `references/main-skill-full-reference.md` — legacy/full detail only if compact guide is insufficient

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Treating low-token as permission to skip gates | Low-token reduces reading, not rigor |
| Starting from `current.task_id` without startup gate | First establish stage, owner, gate, blockers, and next allowed action |
| Letting `project-state/` and `.hermes/project-state/` conflict | Prefer `project-state/`; reconcile conflicts before work |
| Template initializes directly into execution | Start new/unclear projects in `intake` until gates prove otherwise |
| Treating smoke tests as visual parity | Require approved visual source plus screenshot/section evidence |
| Letting specialists pass orchestrator gates | Specialists propose deltas; PlanToDelivery verifies and records gates |
| Marking mock/demo as complete functionality | Mock can satisfy only visual/interaction shell unless demo-only scope is explicitly accepted |
| Stopping on routine user questions | Answer briefly, then continue unless the user pauses/stops |
