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
2. Restore durable state first; prefer `.hermes/project-state/current-state.md`, `.hermes/project-state/active-slice.json`, and an artifact/manifest index when present. If legacy `docs/orchestrator/*` state exists, use it as fallback.
3. Route by current stage and active slice, not by habit. Specialist skills are stage tools, not persistent context.
4. Load at most one specialist skill by default:
   - `idea-to-design` only for product/visual exploration, visual source approval, Visual Freeze, Post-Visual Extraction, or missing/stale design handoff.
   - `IdeaToTech` only for API/state/dependency/mock-to-real/platform/security/performance decisions, feature recipes, or verification strategy that must be fixed before coding.
   - `design-to-code` only after approved design/handoff for implementation, Visual IR, section anchors, screenshots, parity repair, and UI handoff evidence.
5. Do not co-load `idea-to-design`, `IdeaToTech`, and `design-to-code` unless a gate explicitly needs cross-skill conflict resolution. If more than one is needed, load sequentially and pass artifact paths, not full conversation history.
6. Make specialist outputs durable artifacts. The orchestrator consumes manifests, current-state updates, changed-file lists, verification summaries, and blocker/debt ledgers instead of long prose.
7. Keep each execution loop scoped to one feature slice, page, route, or section. Split broad requests into visible checkpoints.
8. Large logs, diffs, screenshots, browser snapshots, and file reads should be saved or summarized; avoid pasting full raw output into the main conversation when a path plus concise summary is enough.
9. Load references/templates only when the current gate needs them. Read `templates/index.md` before opening templates, and open only the exact template needed.

## Skill Routing

- Use `idea-to-design` for product/visual exploration, design approval, Visual Freeze, Post-Visual Extraction, and Level 3 handoff.
- Use `design-to-code` after approved design handoff for implementation, Visual IR, `data-section`, screenshot parity, and visual repair.
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
- `references/main-skill-full-reference.md` — full legacy detail if this compact guide is insufficient

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Loading every reference immediately | Load only the reference required for the current decision |
| Treating smoke tests as visual parity | Require design-source/section evidence for visual claims |
| Letting orchestration become implementation | Route to specialist skills and verify outputs |
| Stopping on routine user questions | Answer briefly, then continue unless user pauses/stops |
