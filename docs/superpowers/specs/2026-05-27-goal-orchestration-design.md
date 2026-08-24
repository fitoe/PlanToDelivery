# Goal Orchestration Design

## Context

PlanToDelivery is the delivery orchestrator for complex Codex work. The goal branch adds a formal way to create and run Codex goals for long, high-risk projects without putting the entire workflow into one long prompt.

The current UI delivery chain is especially strict:

1. PlanToDelivery classifies the project and owns stage/gate state.
2. idea-to-design creates or consolidates product/design artifacts.
3. GPT Image 2 or an equivalent visual source produces page-level mockups when UI fidelity matters.
4. The user approves the visual source.
5. idea-to-design records Visual Freeze and runs Post-Visual Extraction.
6. IdeaToTech locks functional, state, API, mock, dependency, and verification decisions when needed.
7. design-to-code implements from approved visual sources, Visual IR, and implementation blueprints.
8. Playwright screenshot and section-diff evidence closes visual parity gates.

Goal prompts are useful for starting or resuming this chain, but they are not a reliable place to store all process detail. The durable source of truth must be project artifacts and explicit gates.

## Decision

Use **Goal + Project State + Gate Artifacts**.

The Codex goal is a compact execution contract:

- final objective
- workspace and scope
- delivery mode
- hard gates that cannot be bypassed
- skill routing boundaries
- state recovery paths
- completion and waiver rules

Detailed flow state lives under `project-state/`. Legacy `docs/orchestrator/` files may be read as fallback for old PlanToDelivery projects, but `.hermes/` is not a default path.

## Guided Goal Start

PlanToDelivery should support a simple user entrypoint:

```text
P2D，开始这个项目
```

or:

```text
P2D，开始这个项目，目标是 <goal>
```

This entrypoint starts a guided flow instead of requiring the user to understand goal contracts, project-state, Visual IR, or specialist routing.

The guided flow:

1. Ask for the project goal if it is missing.
2. Inspect the project and existing durable state.
3. Classify project profile and delivery mode.
4. Brainstorm only the decisions that affect flow choice or first slice.
5. Present 2-3 flow options with a recommendation.
6. Ask the user to approve or choose the flow.
7. Generate goal contract, goal prompt, flow profile, and initial project-state.
8. Start the first active slice without another broad planning loop.

For UI projects that need high fidelity, the guided flow must automatically include the design-source path:

```text
idea-to-design -> GPT Image 2 or equivalent visual source -> user approval -> Visual Freeze -> Post-Visual Extraction -> IdeaToTech if needed -> design-to-code -> Playwright screenshot/section diff
```

The user should only be interrupted for direction-level choices, approval gates, destructive actions, secrets/auth facts, or waiver decisions.

## Path Protocol

Default portable state paths:

- `project-state/current-state.md`
- `project-state/active-slice.json`
- `project-state/artifact-manifest.json`
- `project-state/gates.json`
- `project-state/decision-log.md`
- `project-state/verification-ledger.md`

Specialist artifact paths:

- `project-state/design/visual-source-contract.json`
- `project-state/design/implementation-blueprint.json`
- `project-state/design/page-matrix.json`
- `project-state/design/component-blueprint.json`
- `project-state/design/debt-ledger.json`
- `project-state/design/visual-ir/<page-id>.json`
- `project-state/tech/technical-decisions.json`
- `project-state/tech/feature-recipes.json`
- `project-state/tech/verification-matrix.json`
- `project-state/evidence/screenshots/`
- `project-state/evidence/parity-reports/`

## Goal Contract

A generated goal must say:

- PlanToDelivery owns orchestration, stage transitions, gates, and handoff claims.
- Specialist skills are loaded only for the active gate or slice.
- UI implementation cannot enter design-to-code without an approved or explicitly waived visual source.
- For GPT Image 2/mockup UI work, approved visual sources are binding unless the user explicitly selects directional-only implementation.
- Visual Freeze and Post-Visual Extraction must be complete before implementation claims visual fidelity.
- design-to-code must consume implementation blueprint, Visual IR, page matrix, and visual source refs before coding or repair when they exist.
- Visual parity claims require screenshot-to-source or section-level evidence unless explicitly waived.
- Completion requires verification evidence or a recorded waiver.

## Flow Profiles

PlanToDelivery should choose the lightest flow that controls the main risk:

| Project profile | Flow |
|---|---|
| Tiny local fix | PlanToDelivery only |
| Backend or functional feature | PlanToDelivery -> IdeaToTech -> execution -> verification |
| UI with approved design source | PlanToDelivery -> design-to-code -> verification |
| UI/product direction unclear | PlanToDelivery -> idea-to-design -> IdeaToTech if needed -> design-to-code -> verification |
| Long-running complex product | PlanToDelivery + project-state + milestone gates + specialist routing |

## Gate Model

Every gate records:

- status: `open`, `passed`, `blocked`, `waived`, or `not_applicable`
- required inputs
- produced artifacts
- evidence
- next owner
- blockers and debt

UI visual gates:

1. Product/design direction closed or explicitly provisional.
2. Page-level visual source generated or supplied.
3. User approval recorded.
4. Visual Freeze recorded.
5. Post-Visual Extraction complete.
6. Visual IR and implementation blueprint ready.
7. design-to-code implementation produces section anchors.
8. Screenshot/section-diff evidence records PASS/WARN/FAIL.

## Templates To Add

- `templates/goal-contract-template.md`
- `templates/goal-prompt-template.md`
- `templates/flow-profile-template.json`
- `references/goal-orchestration.md`
- `references/guided-goal-start.md`

## Updates To Existing Files

- Update `.agents/skills/plantodelivery/SKILL.md` to use `project-state/` as the default state path.
- Keep `docs/orchestrator/` as legacy fallback.
- Remove `.hermes/` from default path examples.
- Update `templates/active-slice-template.json` and `templates/index.md` so generated state points at `project-state/`.
- Add goal orchestration to progressive loading.
- Add Guided Goal Start as the simplest user entrypoint.

## Acceptance Criteria

- No default PlanToDelivery path references `.hermes/`.
- SKILL.md explains that goal prompts are compact contracts, not full workflow storage.
- A new reference describes Goal + Project State + Gate Artifacts as the recommended pattern.
- A new reference describes the one-line Guided Goal Start workflow.
- Templates exist for goal contract, goal prompt, and flow profile.
- Existing project-state checker remains compatible.
