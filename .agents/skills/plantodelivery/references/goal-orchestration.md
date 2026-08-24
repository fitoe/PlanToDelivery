# Goal Orchestration

Use this reference when PlanToDelivery creates, resumes, or audits a Codex goal for a complex or high-fidelity project.

## Principle

A Codex goal is an execution contract, not a full workflow archive.

Put stable control rules in the goal. Put changing flow state, artifact paths, gates, approvals, evidence, and debt in `project-state/`.

The reliable pattern is:

```text
goal -> project-state -> active slice -> specialist artifact -> gate evidence -> next slice
```

## Goal Contract Contents

A goal should include:

- objective and scope
- workspace root
- delivery mode: lightweight, standard, or strict
- active stage or recovery path
- current state files to read first
- hard gates that cannot be bypassed
- skill routing boundaries
- completion criteria
- waiver rules

Do not put every stage instruction, full design brief, full technical plan, or full implementation plan inside the goal. Reference artifacts instead.

## Simple Start

For normal use, the user should be able to say:

```text
P2D，开始这个项目
```

PlanToDelivery should then run Guided Goal Start:

1. ask for the objective if missing;
2. inspect the project and existing state;
3. classify mode and flow;
4. ask for only the decisions that affect route choice;
5. generate goal/project-state artifacts after approval;
6. start the first active slice.

Load `references/guided-goal-start.md` when this entrypoint is used or when the user wants a simpler goal-generation flow.

## Default State Paths

Use these portable paths:

- `project-state/current-state.md`
- `project-state/active-slice.json`
- `project-state/artifact-manifest.json`
- `project-state/gates.json`
- `project-state/decision-log.md`
- `project-state/verification-ledger.md`

Use `docs/orchestrator/*` only as legacy fallback when portable state does not exist.

## Flow Profiles

Choose the lightest flow that controls the main risk:

| Project profile | Flow |
|---|---|
| Tiny local fix | PlanToDelivery only |
| Backend or functional feature | PlanToDelivery -> IdeaToTech -> execution -> verification |
| UI with approved design source | PlanToDelivery -> design-to-code -> verification |
| UI/product direction unclear | PlanToDelivery -> idea-to-design -> IdeaToTech if needed -> design-to-code -> verification |
| Long-running complex product | PlanToDelivery + project-state + milestone gates + specialist routing |

## High-Fidelity UI Gates

For GPT Image 2, mockup, Figma, or screenshot-driven UI implementation:

1. Product/page intent is clear enough to generate or select a visual source.
2. A page-level visual source exists, or the user explicitly waives it.
3. The user approves the visual source.
4. Visual Freeze is recorded.
5. Post-Visual Extraction creates or refreshes implementation artifacts.
6. Visual IR and implementation blueprint are ready for the active page or section.
7. design-to-code implements from structured artifacts and bound visual sources.
8. Playwright screenshots or section diffs record PASS/WARN/FAIL.

Do not let implementation proceed from prose-only briefs when a binding visual source is required.

## Specialist Boundaries

- PlanToDelivery owns orchestration, stage state, gate decisions, progress, verification discipline, and handoff claims.
- idea-to-design owns product/visual exploration, visual source generation or consolidation, Visual Freeze, Post-Visual Extraction, and Level 3 handoff readiness.
- IdeaToTech owns technical decisions for API, state, dependencies, mock-to-real, platform, performance, and verification strategy.
- design-to-code owns implementation and visual repair after the approved post-visual handoff is ready.

Load only the specialist needed for the active gate or slice. If multiple specialists are needed, route sequentially through artifacts.

## Gate Evidence

Every gate decision should record:

- status: `open`, `passed`, `blocked`, `waived`, or `not_applicable`
- required inputs
- produced artifacts
- evidence paths
- next owner
- blockers and debt

Completion claims require verification evidence or a recorded waiver.

## Common Failures

| Failure | Fix |
|---|---|
| Very long goal tries to store the whole project | Move details into `project-state/` and artifact manifests |
| D2C implements from prose | Require approved visual source, Visual IR, or a waiver |
| Visual source approved but not extracted | Route back to idea-to-design for Post-Visual Extraction |
| Build passes but visual parity is claimed | Require screenshot-to-source or section-diff evidence |
| Multiple specialists stay loaded forever | Return compact deltas and consume artifacts by path |
