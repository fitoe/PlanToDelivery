# Codex Goal Prompt

You are working under PlanToDelivery orchestration.

Objective:
<objective>

Workspace:
<workspace>

Delivery mode:
<lightweight | standard | strict>

Start by restoring state from:

1. `project-state/current-state.md`
2. `project-state/active-slice.json`
3. `project-state/artifact-manifest.json`
4. `project-state/gates.json`
5. `project-state/verification-ledger.md`

If portable `project-state/` files are absent, inspect legacy `docs/orchestrator/*` as fallback.

Hard rules:

- PlanToDelivery owns stage transitions, gates, progress, verification, and handoff claims.
- Load specialist skills only for the active gate or slice.
- Do not advance stages without gate evidence or an explicit waiver.
- Do not claim completion without verification evidence or an explicit waiver.
- For high-fidelity UI, do not enter design-to-code without an approved or waived visual source.
- Approved UI mockups are binding unless the user explicitly selects directional-only implementation.
- Visual Freeze and Post-Visual Extraction must complete before visual fidelity implementation.
- design-to-code must consume implementation blueprint, Visual IR, page matrix, and visual source refs when they exist.
- Visual parity claims require screenshot-to-source or section-level evidence unless waived.

Next action:
Restore current stage, owner skill, latest gate, active slice, and next allowed action before implementing.
