# Skill Registry

## Core Always-On
- `superpowers:using-superpowers`
- `karpathy-guidelines`

## Core Planning
- `superpowers:brainstorming`
- `superpowers:writing-plans`

## Core Execution
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:test-driven-development`

## Core Quality
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`
- `superpowers:systematic-debugging`
- `superpowers:finishing-a-development-branch`

## Optional Extensions
- `context7`
  - Allowed stages: `intake`, `full-definition`, `decision-closure`, `execution`, `debugging`
  - Mode: `on-demand`
- `find-skills`
  - Allowed stages: `intake`, `full-definition`
  - Mode: `on-demand`
- `caveman`
  - Allowed stages: `execution`, `handoff`
  - Mode: `optional`

## Browser Validation Capability
- Name: `Playwright browser validation`
- Purpose: Controlled browser assistance for UI validation, bug reproduction, and milestone browser evidence.
- Allowed stages: `ui-definition`, `execution`, `debugging`, `verification`
- Mode: `on-demand`
- User approval required: `no`
- Trigger conditions:
  - critical pages or critical user flows
  - browser-visible interaction bugs
  - milestone browser acceptance
  - need for screenshots, console, or network evidence
- Reasons not to use outside allowed stages:
  - not useful during discovery or decision closure
  - avoid unnecessary browser overhead for non-UI or low-risk changes

## Visual Generation Capability
- Name: `UI visual route and section generation`
- Purpose: Plan routes and pages, generate style frames or effect previews, slice large pages into sections, and hand approved slices to code generation.
- Allowed stages: `ui-definition`, `execution`
- Mode: `on-demand`
- User approval required: `yes` before code generation when style direction changes or first page family is being established
- Trigger conditions:
  - project needs page route planning
  - visual direction needs confirmation before code
  - page is too large to generate faithfully in one pass
  - later pages must keep the same style system
- Reasons not to use outside allowed stages:
  - discovery and decision closure should stay text-led
  - do not generate visual assets before route and page purpose are clear
