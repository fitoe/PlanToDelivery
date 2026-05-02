# UI Visual Generation

Use this file when a milestone needs route planning, page planning, visual style framing, or section-by-section page generation.

This capability is for:

- deriving page routes and page responsibilities from project planning
- generating style frames or page effect previews before code
- micro-adjusting the visual direction with the user
- splitting large pages into smaller sections for reliable code generation
- keeping later pages visually consistent with an approved style direction

## Core Rule

Do not jump directly from project plan to full-page code for large pages.

Instead:

1. derive route and page plan
2. define visual direction
3. generate a style frame or effect preview
4. micro-adjust until approved
5. split pages into section slices
6. generate code one section at a time
7. stitch sections into the final page
8. verify with browser evidence

## When to Use

Use this workflow when:

- the project has multiple pages or routes
- page hierarchy must be planned before implementation
- a visual direction needs to be validated before code
- a page is too large to implement faithfully in one pass
- the same visual system must continue across later pages

## Route Planning

Before any visual generation, build a route plan with:

- route name
- page purpose
- primary user action
- page dependencies
- page priority
- whether the page is a style anchor for later pages

Keep the route plan in durable docs when it matters to milestone delivery.

## Visual Style Framing

If the project benefits from image-based style exploration, generate an effect preview or style frame first.

Rules:

- use the style frame to confirm the overall visual direction
- allow small micro-adjustments before freezing the style
- once a style is approved, reuse it for subsequent pages unless a later milestone explicitly changes direction
- do not treat the style frame as final code

## Section Slicing

For large or fidelity-sensitive pages:

- split the page into ordered sections
- generate or implement each section separately
- keep section boundaries explicit
- preserve section continuity when stitching

Recommended section split inputs:

- hero / header
- navigation or control area
- content block 1
- content block 2
- sidebar or support panel
- footer / closing section

Rules:

- prefer smaller slices when fidelity is important
- keep repeated visual patterns consistent across slices
- do not let section boundaries drift without recording the change

## Relationship to Design-to-Code

Use the `design-to-code` skill when the section slices are ready for code generation.

Recommended sequence:

1. route plan
2. style frame / effect preview
3. approve or adjust
4. section map
5. section-by-section code generation via `design-to-code`
6. stitch and verify

## Relationship to Playwright

After code generation, use browser validation when needed to:

- confirm section order
- confirm visual continuity
- confirm critical interactions
- confirm that later pages match the approved style

## Evidence

Retain evidence when it helps later recovery:

- route plan
- approved style direction
- section map
- screenshots
- browser verification notes
