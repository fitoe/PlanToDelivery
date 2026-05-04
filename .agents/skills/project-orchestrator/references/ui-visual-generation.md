# UI Visual Generation

Use when a milestone needs route planning, style framing, and section-by-section page generation.

## Purpose

- derive page routes and responsibilities from project planning
- generate style frames / effect previews before code
- split large pages into reliable section slices
- keep later pages visually consistent with an approved style
- treat the confirmed image design as the source of truth for implementation and acceptance

## Core Flow

1. route plan
2. style frame / effect preview
3. micro-adjust
4. section map
5. `section breakdown`
6. `Pre-Implementation Brief`
7. user confirms section boundaries and brief
8. `design-to-code` generates code per section
9. stitch and verify

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

- use `imagegen` for style frames or effect previews
- adjust before freezing style
- reuse approved style for later pages unless changed explicitly

## Section Rules

- split into ordered, complete sections
- never cut through the middle of a semantic block
- prefer smaller slices for fidelity
- keep repeated patterns consistent
- if boundaries are unclear, re-cut before coding
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
- section boundaries are approved
- style continuity is approved
- `Pre-Implementation Brief` is approved

If the brief is not approved, do not generate page code.

Implementation and acceptance must follow the confirmed image design, not re-design from the text brief.
The brief may summarize the confirmed image, but it must not introduce new visual direction.

## Browser Validation

Use Playwright after code generation when needed to confirm section order, continuity, and critical interactions.

## Evidence

- route plan
- approved style direction
- section map
- screenshots
- browser verification notes
