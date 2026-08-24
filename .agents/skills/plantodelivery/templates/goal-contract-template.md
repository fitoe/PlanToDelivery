# Goal Contract

## Objective

<Describe the final outcome.>

## Workspace

- Root: `<absolute-or-project-root-path>`
- In scope:
- Out of scope:

## Delivery Mode

- Mode: `lightweight | standard | strict`
- Reason:
- First deliverable slice:

## Recovery

Read these first:

1. `project-state/current-state.md`
2. `project-state/active-slice.json`
3. `project-state/artifact-manifest.json`
4. `project-state/gates.json`
5. `project-state/verification-ledger.md`

Use `docs/orchestrator/*` only as legacy fallback when portable state is absent.

## Hard Gates

- Do not advance stages without gate evidence or a recorded waiver.
- Do not claim completion without verification evidence or a recorded waiver.
- Do not persist secrets, tokens, passwords, or private connection strings.

## UI Visual Gates

- Do not enter design-to-code for high-fidelity UI without an approved or waived visual source.
- Treat approved UI mockups as binding unless the user explicitly chooses directional-only implementation.
- Require Visual Freeze and Post-Visual Extraction before visual fidelity implementation.
- Require screenshot-to-source or section-level evidence before claiming parity.

## Skill Routing

- PlanToDelivery owns orchestration, gates, state, verification, and handoff.
- idea-to-design owns product/visual exploration, visual source approval, Visual Freeze, and Post-Visual Extraction.
- IdeaToTech owns API, state, dependency, mock-to-real, platform, and verification decisions.
- design-to-code owns implementation and parity repair after approved handoff.

## Completion Criteria

- Required artifacts exist and are current.
- Current gate status is `passed` or explicitly `waived`.
- Verification evidence is recorded.
- Remaining blockers, debt, and accepted deviations are listed.
