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
- recommended option
- user-approved final direction

If a milestone needs route planning, page planning, style framing, or section-by-section page generation, also read `references/ui-visual-generation.md`.

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

- `ui-style-directions.md`
- `ui-spec.md`
- `ui-implementation-contract.md`

## Browser-Aided Validation

If UI work includes critical pages or interaction-heavy flows, browser-aided validation may be used during `ui-definition`.

Use Playwright selectively to:
- inspect structure in a live page
- confirm key state coverage
- validate flow feel or navigation expectations
- collect screenshots that clarify implementation intent

Do not turn UI planning into full browser automation by default.
