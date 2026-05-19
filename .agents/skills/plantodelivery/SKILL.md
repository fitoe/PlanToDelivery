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

Do not skip gates because implementation “looks done”. However, best practice is not “more steps”; it is the smallest process that removes the largest delivery risk and produces verifiable progress.

## Delivery Mode Calibration

Before starting or resuming a project, classify the lightest delivery mode that still controls the main risk:

| Mode | Use when | Default workflow |
|---|---|---|
| **Lightweight** | Small fix, single bug, copy/style tweak, clearly bounded task | confirm target → implement → narrow verification → report |
| **Standard** | New page/module/H5/website slice with moderate ambiguity | 30-60 min calibration → decisionable artifact → key direction approval → sliced execution → evidence checkpoint |
| **Strict** | New product/system, many pages/stakeholders, high ambiguity, costly rework, complex data/auth/compliance | discovery → scope/design/tech freeze → milestone plan → execution gates → hardening/release |

Rules:
- Default to the lightest mode that controls the actual risk; do not use Strict only because a project is new.
- Escalate one level only when ambiguity, integration, data/auth, compliance, brand/visual, or rework cost is high.
- Downgrade when the task is local and reversible; do not force full project gates for small fixes.
- State the chosen mode, why, and the first deliverable slice before deep planning.

## Speed and Output Discipline

- First loop for a new project must produce a **decisionable artifact** within 30-60 minutes: project type/risk/mode, first slice, assumptions, blockers, and at least one concrete artifact path or preview plan.
- Prefer artifacts over prose: route/page inventory, IA, state matrix, visual board, screenshot, diff, demo, build result, or concise decision log.
- Do not run two consecutive planning loops with only narrative analysis and no new decision, artifact, screenshot, code, test, or documented gate result.
- Use explicit low-risk assumptions instead of blocking on every unknown; reserve hard blockers for destructive actions, secrets, irreversible choices, auth/permission, or direction-level ambiguity.
- Each execution/repair loop should target the largest **1-3** product-breaking gaps, then checkpoint remaining debt instead of polishing everything equally.

## Parallel Progress Rule

When workstreams do not depend on each other, run them in parallel or delegate them separately:
- product/IA clarification can run beside tech environment/API discovery;
- visual direction exploration can run beside route/data/state inventory;
- implementation can run beside mock data/assets preparation;
- screenshot evidence can run beside Top-gap/debt summarization.

Main session owns mode, gates, and acceptance; subagents may own bounded pages/components/research tasks. Do not serialize independent work just because the written workflow is ordered.

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

When the user asks to整理/生成/更新产品设计文档 after design approval, route to `idea-to-design` to consolidate the approved design into `Design-Spec.md` or an equivalent product/design document, recording source paths, approval notes, and implementation-critical design decisions. This is a documentation capability, not a default hard gate; it should not block existing implementation flow unless the project state or user explicitly requires it.

For flat PNG/GPT Image 2 sources, prefer Visual IR + section parity evidence over prose-only briefs.

## Gate Checks

Gates are decision points, not ritual confirmations. Every gate must answer:
1. Can we safely move to the next stage now?
2. What evidence or artifact supports that decision?
3. If blocked, what are the smallest 1-3 missing conditions?
4. Which unknowns can be carried as explicit assumptions/debt?
5. Who owns the next action?

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
| Treating best practice as maximum process | Choose the lightest delivery mode that controls risk |
| Producing two planning rounds with no artifact | Create a decisionable artifact or move into a bounded execution slice |
| Polishing many minor issues equally | Fix the Top 1-3 product-breaking gaps and record the rest as debt |
| Serializing independent workstreams | Parallelize/delegate independent discovery, design, implementation, and evidence tasks |
