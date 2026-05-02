# UI Visual Generation

Use when a milestone needs route planning, style framing, and section-by-section page generation.

## Purpose

- derive page routes and responsibilities from project planning
- generate style frames / effect previews before code
- split large pages into reliable section slices
- keep later pages visually consistent with an approved style

## Core Flow

1. route plan
2. style frame / effect preview
3. micro-adjust
4. section map
5. user confirms section boundaries
6. `design-to-code` generates code per section
7. stitch and verify

## Use When

- multiple pages or routes exist
- page hierarchy must be planned first
- style needs confirmation before code
- a page is too large for one faithful pass
- later pages must reuse the same visual system

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

## Confirmation Gate

Do not start `design-to-code` until:

- route order is approved
- section boundaries are approved
- style continuity is approved

## Browser Validation

Use Playwright after code generation when needed to confirm section order, continuity, and critical interactions.

## Evidence

- route plan
- approved style direction
- section map
- screenshots
- browser verification notes
