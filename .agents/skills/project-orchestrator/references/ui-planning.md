# UI Planning

Use this file during `ui-definition`.

## Core Model

Plan UI in two tracks:

1. structural track
2. visual track

## Structural Track

Define:
- information architecture
- page inventory
- key user flows
- core page states
- component boundaries

## Visual Track

Produce:
- 2-3 style directions
- small inspiration images for each direction
- recommended option
- user-approved direction for expansion
- large implementation-reference images for the approved direction
- user-approved final implementation reference

For a new project with meaningful UI, generate the style directions with `imagegen` before page implementation starts.
Do not jump directly from a text brief to a large implementation image.
Confirm the small inspiration direction first, then generate the larger implementation-reference images.

If a milestone needs route planning, page planning, style framing, or section-by-section page generation, also read `references/ui-visual-generation.md`.

When visual direction is already confirmed, do not move to page code until section slicing and brief confirmation are complete.
The confirmed image design remains the source of truth for implementation and acceptance.

## Fidelity Rules

- core pages: high fidelity
- secondary pages: medium fidelity
- edge pages: low fidelity

## State Rules

Core pages and core components should define:
- default
- loading
- empty
- error
- success
- disabled/forbidden where relevant
- responsive behavior where relevant

## Output Files

- `docs/orchestrator/ui/ui-style-directions.md`
- `docs/orchestrator/ui/ui-spec.md`
- `docs/orchestrator/ui/ui-implementation-contract.md`
- `docs/orchestrator/ui/section-breakdown.md`
- `docs/orchestrator/ui/pre-implementation-brief.md`

Persist visual artifacts to disk:
- `docs/orchestrator/ui/inspirations/` for small idea frames
- `docs/orchestrator/ui/references/` for approved implementation-reference images
- `docs/orchestrator/ui/sections/` for section maps and section slice images

## Section Slicing

For each page or route, output section slices before implementation.

Each section must include:
- section name
- layout relationship
- content scope
- media role
- reuse points
- key unknowns

Do not merge section slicing into code generation.
Do not let the text brief redefine the visual design; it only records implementation constraints from the confirmed image.
Do not keep section slicing only in chat; write it to disk with image paths or slice references when available.

## Browser-Aided Validation

If UI work includes critical pages or interaction-heavy flows, browser-aided validation may be used during `ui-definition`.

Use Playwright selectively to:
- inspect structure in a live page
- confirm key state coverage
- validate flow feel or navigation expectations
- collect screenshots that clarify implementation intent

Do not turn UI planning into full browser automation by default.
