# UI Visual Generation

Use when a milestone needs route planning, style framing, and section-by-section page generation.

Ownership rule:
- route product design, route/page planning, visual direction, and image iteration to `idea-to-design`
- route approved design image to code implementation to `design-to-code`
- use this reference as PlanToDelivery's validation and handoff checklist, not as a substitute workflow

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

## Page Image Rules

- one page at a time
- every page must go through `small -> large -> prompt`
- `small` means 2-3 same-page, materially different style directions for exploration only
- `small` must not combine multiple routes in one image
- every generated `small` and `large` image must be persisted, including unselected versions
- the approved `large` image must be persisted with a structured prompt artifact intended for reproduction
- the prompt artifact must be version-bound to the approved `large` image
- section slicing is required only for complex pages
- simple mobile pages or lightweight web pages may use fewer slices or no slices
- when slicing is required, do not cut directly from semantic guesswork; first produce a conservative slice preview with forbidden zones, candidate boundaries, merge decisions, and final slice ranges
- when slicing is required, the section boundaries and order must be manually confirmed from that preview before final slices are accepted
- any slice artifacts must be persisted and version-bound to the originating `large` image
- `small`, `large`, `prompt`, and `slice` artifacts must remain traceable to the same page and version
- do not discard historical image versions; preserve them for later reference and regeneration
- persisted artifacts must live inside the project repository, not under `.codex/`, temp folders, or chat-only state
- if a generation tool emits files into `.codex/` first, move or copy the final approved images and slice artifacts into repository paths before continuing

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
- do not start by guessing semantic boundaries; first mark forbidden zones:
  - titles and subtitles
  - CTA/button clusters
  - card bodies or card grids
  - hero media focal areas
  - forms and form labels
  - person/product/illustration focal subjects
  - any obvious section-theme center content
- find candidate safe bands only after forbidden zones are marked
- prefer boundaries through sparse buffer areas rather than through content centers
- prefer larger slices with overlap or safety margin over tight cuts that risk clipping content
- if boundaries are unclear, merge instead of forcing a cut
- allowed final decisions per boundary are `cut`, `merge with previous`, `merge with next`, or `keep as one larger slice`
- generate and persist a slice preview before accepting final section slices
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
- persisted slice preview artifact exists and shows forbidden zones, candidate boundaries, and merge decisions
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
- persisted slice preview artifact
- persisted section slice artifacts
- screenshots
- browser verification notes

Repository evidence rule:
- every evidence artifact must be referenced by a project-relative path
- `.codex/` paths are temporary working paths only and do not satisfy persistence or confirmation gates
