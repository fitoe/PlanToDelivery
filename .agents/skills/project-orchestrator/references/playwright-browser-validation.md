# Playwright Browser Validation

Use this file when browser-assisted work is needed during:

- `ui-definition`
- `execution`
- `debugging`
- `verification`

Do not treat Playwright as an always-on tool.

## Role

Playwright has two roles in this skill:

1. browser-side debugging and implementation assistance
2. browser-side acceptance and evidence collection

It is not a replacement for:

- unit tests
- integration tests
- non-browser verification that is cheaper and sufficient

## When to Use

Use Playwright when any of these are true:

- milestone includes critical pages
- milestone includes critical user flows
- a bug is browser-visible or interaction-specific
- milestone acceptance requires browser evidence
- screenshots, console logs, or network traces are needed to support a conclusion

## When Not to Use

Do not require Playwright by default when:

- project is backend-only
- project is CLI-only
- change is isolated to non-browser logic
- a smaller validation method fully proves the result

## Stage Roles

### `ui-definition`
Use Playwright to:
- inspect live structure
- validate flow feel and screen transitions
- confirm core states are represented
- compare implementation against intended layout or interaction

This is not yet full E2E automation work.

### `execution`
Use Playwright to:
- quickly confirm critical interactions work
- check page state after implementation slices
- validate high-value browser behavior before broader verification

Prefer narrow checks over full browser suites during local loops.

### `debugging`
Use Playwright to:
- reproduce browser-visible bugs
- capture console errors
- capture failed or suspicious network requests
- compare behavior before and after a fix
- capture screenshots or snapshots when they clarify the defect

### `verification`
Use Playwright to:
- run milestone-critical browser checks
- execute lightweight browser acceptance scripts where justified
- collect evidence for milestone verification reports

## Interaction Model

Use a mixed model:

- `ui-definition` and `debugging`: manual controlled browser use is acceptable
- `verification`: prefer repeatable scripts or explicit repeatable validation steps

## Evidence Rules

Evidence may be retained at:

- task level
- milestone level

Suggested structure:

```text
docs/orchestrator/evidence/
  Mx/
    playwright/
      screenshots/
      logs/
      network/
```

Do not keep every artifact by default. Keep evidence when it:

- supports a debugging conclusion
- supports milestone acceptance
- explains a failure or regression

## Minimal Browser Capability Set

Use Playwright for these controlled actions:

- open page
- wait for stable state
- confirm text or element presence
- click / type / select / submit
- inspect console output
- inspect network requests
- capture screenshots
- record browser-side verification results

Avoid turning first-pass skill usage into:

- full cross-browser matrix testing
- large visual diff infrastructure
- broad performance auditing
- always-on background browser sessions

## Relationship to Testing

Use this layering:

- unit tests for logic and state rules
- integration tests for module collaboration and data / permission boundaries
- Playwright for browser behavior, key interaction closure, and browser evidence

## Process Discipline

- Do not leave idle browser processes running without purpose.
- Reuse an active browser context when practical.
- Do not turn quick browser checks into accidental long-lived sessions.
- If Playwright leaves persistent debugging state, record it in `session-brief.md`.
