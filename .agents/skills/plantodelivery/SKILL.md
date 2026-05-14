---
name: PlanToDelivery
description: Use when orchestrating a project from idea or plan through staged delivery, checkpoints, skill routing, gates, progress reporting, and handoff.
---

# Plan To Delivery

## Purpose

Orchestrate delivery without duplicating specialist skills. Own stage state, gates, routing, progress reporting, verification discipline, and handoff claims.

## Core Responsibilities

- maintain current stage, milestone, blockers, and next action
- route work to the right skill or workflow
- enforce hard gates before stage transitions
- keep progress visible and truthful
- commit/push meaningful verified checkpoints when appropriate
- report debt, waivers, and incomplete verification explicitly

## Stage Machine

Default stages:
1. intake / context recovery
2. decision closure
3. UI definition / design handoff if UI-bearing
4. milestone plan
5. execution
6. verification / hardening
7. release / final handoff

Do not skip gates because implementation “looks done”.

## Low-Token Routing Protocol

When the user invokes "贾维斯", "贾维斯继续", "低 token 模式", or asks to continue a project, default to low-token orchestration:

1. Keep `PlanToDelivery` as the only persistent owner until a gate requires a specialist.
2. Restore durable state first; prefer project-root `project-state/execution-progress.json` and `project-state/artifact-manifest.json` when present. Fall back to `.hermes/project-state/current-state.md`, `.hermes/project-state/active-slice.json`, or legacy `docs/orchestrator/*` only when project-state is absent.
3. Route by current stage and active slice, not by habit. Specialist skills are stage tools, not persistent context.
4. Load at most one specialist skill by default:
   - `idea-to-design` only for product/visual exploration, visual source approval, Visual Freeze, Post-Visual Extraction, or missing/stale design handoff.
   - `IdeaToTech` only for API/state/dependency/mock-to-real/platform/security/performance decisions, feature recipes, or verification strategy that must be fixed before coding.
   - `design-to-code` only after approved design/handoff for implementation, Visual IR, section anchors, screenshots, parity repair, and UI handoff evidence.
5. Do not co-load `idea-to-design`, `IdeaToTech`, and `design-to-code` unless a gate explicitly needs cross-skill conflict resolution. If more than one is needed, load sequentially and pass artifact paths, not full conversation history.
6. Make specialist outputs durable artifacts. The orchestrator consumes `project-state/artifact-manifest.json`, current-state updates, changed-file lists, verification summaries, and blocker/debt ledgers instead of long prose.
7. Keep each execution loop scoped to one feature slice, page, route, or section. Split broad requests into visible checkpoints.
8. Large logs, diffs, screenshots, browser snapshots, and file reads should be saved or summarized; avoid pasting full raw output into the main conversation when a path plus concise summary is enough.
9. For GPT Image 2/mockup UI work, default to `standard-fidelity`: keep high-fidelity expectations, but scope each loop to the active page/section and use Visual IR/source/screenshot paths instead of long visual prose.
10. Do not downgrade high-fidelity UI to a fast/loose mode just to save tokens. Escalate to `strict-fidelity` only for core screens, full-page regeneration, complex assets, final parity acceptance, or repeated parity failure.
11. Load references/templates only when the current gate needs them. Read `templates/index.md` before opening templates, and open only the exact template needed.

## Skill Routing

- Use `idea-to-design` for product/visual exploration, design approval, Visual Freeze, Post-Visual Extraction, and Level 3 handoff.
- Use `design-to-code` after approved design handoff for implementation, Visual IR, `data-section`, screenshot parity, and visual repair. For GPT Image 2/mockup UI, route with `standard-fidelity` by default; use `strict-fidelity` only when exact final parity, full-page regeneration, complex assets, or repeated repair failure requires heavier references.
- Use `IdeaToTech` or project planning workflows for technical/API/state/dependency decisions when needed.
- Use framework skills only for concrete implementation details.

### UI Handoff Boundary

Once the visual source is user-approved and has Visual Freeze + Post-Visual Extraction + implementation-ready handoff, route routine UI implementation to `design-to-code`. Return to `idea-to-design` only for stale/missing/conflicting design source, product changes, missing handoff, or requested redesign.

For flat PNG/GPT Image 2 sources, prefer Visual IR + section parity evidence over prose-only briefs.

## Gate Checks

Before major transitions, record:
- required artifacts
- pass/fail/n/a for each
- allowed vs blocked
- owner of next step
- verification evidence or explicit waiver

Hard-block on:
- destructive changes without scope confirmation
- secrets/token persistence
- unknown auth/permission requirements for real API work
- claiming completion without verification or waiver
- design parity claims without design source and visual evidence


## Progress-Driven Execution

Use project-root `project-state/` as the portable execution state layer for any project with a formal implementation plan. This state is a project asset, not Hermes-private runtime state.

Required files when an implementation plan exists:
- `project-state/execution-progress.json` — source of truth for current stage/task, task states, gates, blockers, verification, checkpoints, events, and selection policy
- `project-state/execution-progress.schema.json` — schema for the progress file
- `project-state/artifact-manifest.json` — registry of design, technical, implementation, gate, evidence, and report artifacts
- `project-state/artifact-manifest.schema.json` — schema for the artifact registry
- `scripts/check-project-state.py` — validator, unless an explicit waiver is recorded

Rules:
1. Before entering execution, create or refresh project-state and run the validator.
2. Every task state change updates `execution-progress.json`; commits follow meaningful checkpoints, not every micro-state.
3. Milestone completion must be committed, and pushed when the project workflow expects remote build/deployment.
4. `PlanToDelivery` is the only authoritative writer for `execution-progress.json` and `artifact-manifest.json`.
5. Specialist skills create their own artifacts and return `suggested_manifest_entries`, `suggested_progress_updates`, blockers, gate recommendations, and evidence. Merge only after verifying files/evidence.
6. Do not store secrets, tokens, passwords, or private connection strings in project-state.

### Execution Progress Contract

`execution-progress.json` must track:
- `source_plan`: implementation plan path and status
- `current`: stage, milestone/phase, current task, next task, and next action
- `selection_policy`: default `dependency_priority_order`
- `tasks`: task-level progress with separated `task_status`, `verification_status`, `commit_status`, and `user_confirmation_status`
- `gates`: stage or handoff gates and required artifacts/checks
- `blockers`: top-level lifecycle blockers with owner, severity, resolution requirement, and unblocked task IDs
- `checkpoints`: meaningful commits/releases/handoffs with evidence
- `events`: audit trail for key progress changes

Default task statuses: `pending`, `ready`, `in_progress`, `blocked`, `completed`, `skipped`, `failed`.
Default verification statuses: `not_required`, `not_started`, `running`, `passed`, `failed`, `waived`.
Default commit statuses: `not_required`, `not_committed`, `committed`, `pushed`, `waived`.
Default user confirmation statuses: `not_required`, `required`, `requested`, `approved`, `changes_requested`, `waived`.

### Selection Policy

When choosing the next task:
1. Continue `current.task_id` if it is still `in_progress`.
2. Otherwise choose tasks whose status is `ready` or `pending`.
3. Dependencies must be `completed`, `skipped`, or `waived`.
4. Referenced blockers must be `resolved` or `waived`.
5. Required gates must be `passed` or `waived`.
6. Sort by `priority`, then `order`.
7. If no task is eligible and unresolved blockers exist, report blockers instead of retrying blindly.

### Artifact Manifest Contract

`artifact-manifest.json` registers artifacts by stable ID. Tasks, gates, checkpoints, and evidence reference artifacts by `artifact_refs` instead of relying on prose.

Common artifact kinds:
- design: `design_spec`, `visual_source`, `visual_source_contract`, `implementation_blueprint`, `page_matrix`, `component_blueprint`, `visual_ir`, `design_debt_ledger`
- technical: `technical_decisions`, `feature_recipes`, `verification_matrix`, `api_contracts`, `state_management_plan`, `mock_to_real_plan`
- implementation: `implementation_code`, `parity_report`, `screenshot_evidence`, `accepted_deviations`
- governance: `gate_report`, `validation_log`, `checkpoint_report`, `schema`, `note`

Artifact statuses: `draft`, `ready`, `approved`, `consumed`, `stale`, `superseded`, `rejected`, `missing`.

### Routing and Suggested Updates

Each execution task that needs a specialist should include `routing`:
- `required_skills`
- `input_artifact_refs`
- `expected_output_artifacts`
- `gate_owner`
- `handoff_to`

Load only the specialist named by the active task. Ask the specialist to return:

```json
{
  "suggested_manifest_entries": [],
  "suggested_progress_updates": [],
  "suggested_blockers": [],
  "suggested_gate_updates": [],
  "suggested_events": [],
  "evidence": []
}
```

Treat these as proposals. Verify referenced files, commands, screenshots, commits, and user confirmations before merging state. A specialist may not pass gates outside its ownership; `PlanToDelivery` performs final gate checks.

## Progress Reporting Standard

For Weixin/project checkpoints, include:
- status label
- backend execution: yes/no
- completed in the last window
- current action
- next step
- next expected report

Batch updates; avoid noisy micro-messages.

## Verification Discipline

During active implementation, avoid expensive broad checks after every edit unless needed. At checkpoints/gates, run the narrowest relevant verification first, then broader checks when release/merge readiness is claimed.

Report skipped checks as skipped, not passed.

## Progressive Loading

Load only when needed:
- `references/workflow.md` — full stage workflow
- `references/stage-gates.md` — detailed gate matrix
- `references/skill-routing.md` — routing details
- `references/cross-skill-contracts.md` — contracts with IdeaToDesign/DesignToCode/IdeaToTech
- `references/testing-strategy.md` — verification strategy
- `references/efficiency-rules.md` — low-token/low-cost execution rules
- `references/vue-progress-overlay.md` — progress overlay implementation
- `templates/index.md` — artifact templates
- `templates/active-slice-template.json` — low-token active slice/project-state seed
- `templates/execution-progress-template.json` — portable progress-driven execution state template
- `templates/artifact-manifest-template.json` — portable artifact registry template
- `templates/execution-progress.schema.json` — JSON Schema for progress state
- `templates/artifact-manifest.schema.json` — JSON Schema for artifact registry
- `scripts/check-project-state.py` — portable project-state validator
- `references/main-skill-full-reference.md` — full legacy detail if this compact guide is insufficient

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Loading every reference immediately | Load only the reference required for the current decision |
| Treating smoke tests as visual parity | Require design-source/section evidence for visual claims |
| Letting orchestration become implementation | Route to specialist skills and verify outputs |
| Stopping on routine user questions | Answer briefly, then continue unless user pauses/stops |
