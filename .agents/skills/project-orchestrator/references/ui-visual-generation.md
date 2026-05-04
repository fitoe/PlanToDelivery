# UI Visual Generation

Use when a milestone needs route planning, style framing, and section-by-section page generation.

## Purpose

- derive page routes and responsibilities from project planning
- generate small inspiration frames before code
- generate approved large implementation-reference images before code
- split large pages into reliable section slices
- persist all visual and section artifacts to repository docs
- keep later pages visually consistent with an approved style
- treat the confirmed image design as the source of truth for implementation and acceptance

## Core Flow

1. route plan
2. 2-3 small inspiration frames
3. user approves one direction for expansion
4. large implementation-reference images
5. micro-adjust and confirm the large reference
6. section map
7. persisted `section breakdown`
8. persisted `Pre-Implementation Brief`
9. user confirms reference, section boundaries, and brief
10. `design-to-code` generates code per section
11. stitch and verify

## Use When

- multiple pages or routes exist
- page hierarchy must be planned first
- style needs confirmation before code
- a page is too large for one faithful pass
- later pages must reuse the same visual system
- this is a new project with meaningful UI and no approved visual direction yet

## Route Plan Fields

- route name
- page purpose
- primary user action
- page dependencies
- page priority
- style-anchor flag

## Style Frame Rules

- use `imagegen` for both inspiration frames and implementation-reference images
- small inspiration frames are for style selection only
- large implementation-reference images are for implementation and acceptance
- save both stages to repository docs
- adjust before freezing style
- reuse approved style for later pages unless changed explicitly

## Section Rules

- split into ordered, complete sections
- never cut through the middle of a semantic block
- prefer smaller slices for fidelity
- keep repeated patterns consistent
- if boundaries are unclear, re-cut before coding
- persist the section map and any section slice images before coding
- every section must state:
  - section name
  - layout relationship
  - content scope
  - media role
  - reuse points
  - key unknowns

## Confirmation Gate

Do not start `design-to-code` until:

- route order is approved
- persisted implementation-reference images are approved
- section boundaries are approved
- persisted section artifacts exist
- style continuity is approved
- `Pre-Implementation Brief` is approved

If the brief is not approved, do not generate page code.

Implementation and acceptance must follow the confirmed image design, not re-design from the text brief.
The brief may summarize the confirmed image, but it must not introduce new visual direction.

## Browser Validation

Use Playwright after code generation when needed to confirm section order, continuity, and critical interactions.

## Evidence

- route plan
- approved inspiration direction
- approved implementation-reference images
- section map
- persisted section slice artifacts
- screenshots
- browser verification notes
