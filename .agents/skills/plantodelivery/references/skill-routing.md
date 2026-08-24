# Skill Routing

This file defines which skills the orchestrator should activate, when they should be used, and how to keep routing controlled.

Use it after stage is known.

For stage transition, gate, and cross-skill handoff decisions, prefer `references/orchestration-core.md` first. Load detailed references only when the compact core is not enough.

Before loading templates, read `templates/index.md` and open only the exact template needed.

## Routing Principles

- Route by stage, not by habit.
- Use the smallest necessary skill set for the current task.
- Treat specialist skills as stage tools, not persistent context.
- Keep `PlanToDelivery` as the persistent owner; load at most one specialist by default.
- Prefer artifact paths, manifests, and concise state summaries over full chat-history handoffs.
- Prefer existing core skills over introducing new ones.
- Additional skills must be explicitly justified and stage-bounded.
- Do not load all possible skills into every session.
- Do not duplicate a skill's full workflow inside orchestrator logic. Route to it.

## Core Skill Tiers

### Tier 1: Always-On Process Layer

These define project discipline and should be active from the start.

- `superpowers:using-superpowers`
- `karpathy-guidelines`

## Tier 2: Core Planning Layer

Use when project definition or milestone definition is being created or repaired.

- `superpowers:brainstorming`
- `superpowers:writing-plans`

## Tier 3: Core Execution Layer

Use when milestone work is ready to implement.

- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:test-driven-development`

## Tier 4: Core Quality Layer

Use during implementation, repair, and closure.

- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`
- `superpowers:systematic-debugging`
- `superpowers:finishing-a-development-branch`

## Tier 5: Optional Extension Layer

Use only when relevant.

- `context7`
- `find-skills`
- `caveman`

## Tier 6: Specialized Project Delivery Layer

Use only through explicit stage gates. These are on-demand stage tools, not always-on context:

- `idea-to-design`
- `IdeaToTech`
- `design-to-code`

## Stage-to-Skill Routing

## 1. Intake

### Default Skills
- `superpowers:using-superpowers`
- `karpathy-guidelines`

### Optional Skills
- `context7` when codebase depends on changing third-party APIs or libraries
- registered domain skills only if current-state assessment clearly needs them

### Do Not Use By Default
- `superpowers:writing-plans`
- `superpowers:subagent-driven-development`

## 2. Discovery

### Default Skills
- `superpowers:brainstorming`

### Supporting Skills
- `superpowers:using-superpowers`
- `karpathy-guidelines`

## 3. Full Definition

### Default Skills
- `superpowers:brainstorming`

### Supporting Skills
- `karpathy-guidelines`

### Optional Skills
- `context7` when architecture or library detail depends on current docs
- UI or stack-specific registered skills if they help define implementation-shaping details

## 4. UI Definition

### Default Skills
- `superpowers:brainstorming`
- `idea-to-design` when product design, page planning, design documentation, visual direction, or staged design images are needed

### Optional Registered Skills
Use when enabled and appropriate:
- frontend/design-related skills
- component-system skills
- framework-specific UI skills
- `imagegen` for style frames or effect previews

Examples:
- `build-web-apps:frontend-app-builder`
- `build-web-apps:react-best-practices`
- `build-web-apps:shadcn`
- `magicpath`

### Browser Validation Note
Playwright may validate UI structure, state, or flow when text-only reasoning is not enough.

### Visual Generation Note
If the milestone needs route planning, page planning, style direction, or design images, route to `idea-to-design`.
`PlanToDelivery` should verify persisted outputs and approval state, not reproduce the full design workflow inside this routing file.

## 5. Decision Closure

### Default Skills
- `superpowers:brainstorming`

### Supporting Skills
- `karpathy-guidelines`
- `context7` when documentation is needed to compare stack or platform choices

## 6. Roadmap

### Default Skills
- `superpowers:brainstorming`

## 7. Milestone Spec

### Default Skills
- `superpowers:brainstorming`

## 8. Milestone Plan

### Default Skills
- `superpowers:writing-plans`

### Supporting Skills
- `karpathy-guidelines`

## 9. Execution

### Default Skills
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:test-driven-development`
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`

### Optional Skills
- stack-specific domain skills
- `context7` for current official docs
- targeted UI/build/deployment/database skills if current task requires them
- `IdeaToTech` only when a milestone has non-trivial dependency choices, API/state/mock-to-real work, feature recipes, streaming/upload/chart/map/form complexity, or verification strategy that should be fixed before implementation; consume its JSON artifacts on later turns instead of reloading it.
- `design-to-code` only when a UI milestone has an approved post-visual Level 3 blueprint package ready for implementation (`implementation-blueprint.json` with approved `visual_freeze_ref`, `page-matrix.json`, `component-blueprint.json`, `debt-ledger.json`) or when a fallback approved design source/brief path is explicitly chosen.
- prefer blueprint-driven `design-to-code` for Foundation -> Coverage -> Refinement -> Fidelity; do not force section slicing before broad route/page coverage unless the blueprint/fidelity target requires it.
- never use `design-to-code` before approved visual sources and either a valid blueprint-path gate or detailed fidelity-path gate exist.
- do not load `idea-to-design` during routine implementation unless design source is missing, stale, conflicting, or the user requests a design change.

### Browser Validation Note
Use Playwright narrowly for critical pages or interactions only.

## 10. Debugging

### Default Skills
- `superpowers:systematic-debugging`

### Supporting Skills
- `superpowers:test-driven-development` when a bug should be reproduced with failing tests
- `context7` if bug involves library behavior that may have changed

### Browser Validation Note
Use Playwright when the defect needs browser evidence.

## 11. Verification

### Default Skills
- `superpowers:verification-before-completion`

### Supporting Skills
- `superpowers:requesting-code-review` when additional review is needed

### Browser Validation Note
Use Playwright when milestone acceptance needs browser evidence.

## 12. Handoff

### Default Skills
- `superpowers:finishing-a-development-branch` for milestone or major work closure

### Supporting Skills
- `caveman` can be used for compact summaries if user wants compression

## 13. Done

### Default Skills
- `superpowers:verification-before-completion`
- `superpowers:finishing-a-development-branch`

## Controlled Extension Skill Rules

Additional skills may be used only if they satisfy all of these:

1. They materially help current stage or task
2. They do not replace orchestrator stage control
3. They are registered or explicitly user-requested
4. Their use does not explode context unnecessarily
5. They are bounded to current need

For `idea-to-design` and `design-to-code`, first read `references/orchestration-core.md`. Read `references/cross-skill-contracts.md` only when equivalent artifact acceptance or detailed handoff contract is unclear.
For artifact-based handoffs, also read `references/artifact-driven-workflow.md`.

Missing dependency rule:

- If a routed skill is required but not installed or not found, do not skip it.
- First search the global skill installation source or registry.
- If it is still unavailable, stop and prompt for permission to install it automatically before continuing.

## Registered Skill Format

Use `docs/orchestrator/skill-registry.md` to record:

- skill name
- purpose
- trigger conditions
- allowed stages
- whether always-on or on-demand
- whether user approval is required
- reasons not to use it outside those stages

## Skill Loading Discipline

When a skill is relevant:
- load it before doing the work it governs
- do not wait until halfway through the task
- do not stack unrelated skills "just in case"

When multiple skills could apply:
- load process skill first
- load implementation/domain skill second
- load optional utility skill only if it materially helps

## Reference and Template Loading by Stage

## Session Start
Read the minimum state needed:
- `project-state/current-state.md`, `project-state/active-slice.json`, and `project-state/artifact-manifest.json` when present
- `references/session-start-protocol.md` only if stage/owner/gate cannot be established from compact state
- `references/artifact-driven-workflow.md` only when artifact state exists and needs interpretation
- `templates/project-state-template.json` only when initializing artifact-driven state

## Intake
Read:
- `references/intake-protocol.md`
- `templates/current-state-template.md`
- `templates/gap-analysis-template.md`
- `templates/session-brief-template.md`

## Discovery / Full Definition
Read:
- `references/planning-contract.md`
- `templates/product-spec-template.md`
- `templates/feature-breakdown-template.md`

## UI Definition
Read:
- `references/ui-planning.md`
- `references/ui-visual-generation.md` when page-oriented UI work is in scope
- `references/cross-skill-contracts.md` when routing to `idea-to-design`
- `references/artifact-driven-workflow.md` when accepting equivalent external design artifacts
- `references/ui-design-gate-testing.md` when validating or tightening the design-before-code workflow
- `references/playwright-browser-validation.md` when UI structure, state, or flow needs browser confirmation
- `templates/ui-style-directions-template.md`
- `templates/ui-spec-template.md`
- `templates/ui-implementation-contract-template.md`
- `templates/section-breakdown-template.md`
- `templates/pre-implementation-brief-template.md`
- `templates/artifact-manifest-template.json`
- `templates/approval-records-template.json`
- `templates/handoff-manifest-template.json`

## Decision Closure
Read:
- `references/stage-gates.md`
- `references/cross-skill-contracts.md` when checking specialized skill handoff readiness
- `references/gate-enforcement-scenarios.md` when user pressure or ambiguity may skip gates
- `references/artifact-driven-workflow.md`
- `templates/decision-log-template.md`
- `templates/gate-check-template.md` before any major stage transition
- `templates/project-state-template.json`

## Roadmap
Read:
- `references/workflow.md`
- `templates/gate-check-template.md` before advancing from definition into roadmap
- `templates/roadmap-template.md`

## Milestone Spec
Read:
- relevant domain references
- `templates/milestone-spec-template.md`

## Milestone Plan
Read:
- `references/testing-strategy.md`
- `references/playwright-browser-validation.md` when critical browser flows are in scope
- `templates/implementation-plan-template.md`
- `templates/milestone-test-plan-template.md`
- `templates/risk-matrix-template.md`

## Execution
Read:
- active milestone spec
- active milestone plan
- active task state
- `references/cross-skill-contracts.md` before routing to `design-to-code`
- `references/gate-enforcement-scenarios.md` before starting implementation if any required approval may be missing
- `references/artifact-driven-workflow.md` when checking implementation-ready artifacts
- only task-relevant domain references
- `references/playwright-browser-validation.md` when critical browser behavior is being checked

## Debugging
Read:
- active milestone plan
- active verification report if present
- domain-specific references only if bug source needs them
- `references/playwright-browser-validation.md` when browser-visible reproduction or evidence capture is needed

## Verification
Read:
- `templates/verification-report-template.md`
- active milestone test plan
- relevant regression plan
- `references/playwright-browser-validation.md` when milestone browser evidence is required

## Handoff
Read:
- `templates/task-state-template.md`
- `templates/session-brief-template.md`
- `templates/final-handoff-template.md` when closing milestone or project
- latest gate check when the next session may transition stages
- `templates/handoff-manifest-template.json` when transferring work between skills or sessions
