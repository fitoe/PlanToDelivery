# Skill Routing

This file defines which skills the orchestrator should activate, when they should be used, and how to keep routing controlled.

Use it after stage is known.

## Routing Principles

- Route by stage, not by habit.
- Use the smallest necessary skill set for the current task.
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

### Optional Registered Skills
Use when enabled and appropriate:
- frontend/design-related skills
- component-system skills
- framework-specific UI skills

Examples:
- `build-web-apps:frontend-app-builder`
- `build-web-apps:react-best-practices`
- `build-web-apps:shadcn`
- `design-to-code`
- `magicpath`

### Browser Validation Note
Playwright may be used in this stage as a controlled browser aid for structure, state, and flow validation when text-only reasoning is insufficient.

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

### Browser Validation Note
Playwright may be used here for narrow browser-side validation of critical pages or interactions. Do not broaden small implementation loops into full browser suites by default.

## 10. Debugging

### Default Skills
- `superpowers:systematic-debugging`

### Supporting Skills
- `superpowers:test-driven-development` when a bug should be reproduced with failing tests
- `context7` if bug involves library behavior that may have changed

### Browser Validation Note
Use Playwright when the defect is browser-visible, interaction-specific, or requires console / network / screenshot evidence.

## 11. Verification

### Default Skills
- `superpowers:verification-before-completion`

### Supporting Skills
- `superpowers:requesting-code-review` when additional review is needed

### Browser Validation Note
Use Playwright here when milestone acceptance depends on browser behavior or when browser evidence is required.

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
- `references/playwright-browser-validation.md` when UI structure, state, or flow needs browser confirmation
- `templates/ui-style-directions-template.md`
- `templates/ui-spec-template.md`
- `templates/ui-implementation-contract-template.md`

## Decision Closure
Read:
- `references/stage-gates.md`
- `templates/decision-log-template.md`

## Roadmap
Read:
- `references/workflow.md`
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
