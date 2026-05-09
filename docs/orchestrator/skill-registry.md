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
  - Allowed stages: `intake`, `product-definition`, `system-definition`, `decision-closure`, `execution`, `debugging`
  - Mode: `on-demand`
- `find-skills`
  - Allowed stages: `intake`, `product-definition`, `system-definition`
  - Mode: `on-demand`
- `caveman`
  - Allowed stages: `execution`, `handoff`
  - Mode: `optional`

## Specialized Delivery Skills
- `idea-to-design`
  - Purpose: Turn ideas or partial product concepts into product design docs, task flows, page plans, visual direction, staged design images, and resumable design state.
  - Allowed stages: `discovery`, `product-definition`, `ui-definition`, `decision-closure`
  - Mode: `on-demand`
  - User approval required: `yes` before treating design direction or implementation-reference images as approved
  - Trigger conditions:
    - product idea needs design shaping
    - page routes or surfaces need planning
    - visual direction or staged design images are needed
    - existing design material needs formal design documentation
  - Reasons not to use outside allowed stages:
    - it does not implement code
    - it does not own milestone execution or verification
- `design-to-code`
  - Purpose: Convert approved design images or sections into high-fidelity Vue/Astro/UnoCSS code with a confirmed pre-implementation brief and visual verification.
  - Allowed stages: `execution`, `verification`
  - Mode: `on-demand`
  - User approval required: `yes` before code generation when the brief or visual source has not already been confirmed
  - Trigger conditions:
    - approved design image exists
    - target page or section is in current milestone scope
    - implementation needs high visual fidelity
    - Playwright section diff verification is expected
  - Reasons not to use outside allowed stages:
    - it should not create product requirements
    - it should not invent visual direction
    - it requires approved design inputs

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
- Purpose: Plan routes and pages, generate style frames or effect previews, slice large pages into sections, produce the `Pre-Implementation Brief`, and hand approved slices to code generation.
- Allowed stages: `ui-definition`, `execution`
- Mode: `on-demand`
- User approval required: `yes` before code generation and after section boundaries and brief are defined
- Trigger conditions:
  - project needs page route planning
  - visual direction needs confirmation before code
  - small inspiration images must be approved before large implementation-reference images are generated
  - page is too large to generate faithfully in one pass
  - later pages must keep the same style system
  - section boundaries need confirmation before implementation
  - all confirmed visual pages must pass implementation-reference image -> section breakdown -> brief -> confirmation before page code
- Reasons not to use outside allowed stages:
  - discovery and decision closure should stay text-led
  - do not generate visual assets before route and page purpose are clear
  - do not skip artifact persistence, section slicing, or brief confirmation before design-to-code
