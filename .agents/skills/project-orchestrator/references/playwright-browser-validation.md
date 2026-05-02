# Playwright Browser Validation

Use during `ui-definition`, `execution`, `debugging`, and `verification` for browser-visible work.

## Role

- browser debugging aid
- browser acceptance / evidence tool

## Use When

- critical page or flow needs browser confirmation
- a bug is browser-visible or interaction-specific
- screenshots, console logs, or network traces are needed
- milestone acceptance needs browser evidence

## Do Not Use By Default

- backend-only or CLI-only work
- non-browser logic already proven cheaper
- broad browser suites before core flows stabilize

## Stage Use

- `ui-definition`: validate structure, state, and flow feel
- `execution`: check critical interactions after slices
- `debugging`: reproduce and capture browser evidence
- `verification`: run milestone browser checks and record evidence

## Interaction Model

- `ui-definition` / `debugging`: manual controlled browser use is acceptable
- `verification`: prefer repeatable steps or scripts

## Evidence

Keep only what matters:

- screenshots
- logs
- network traces
- browser-side conclusions

Suggested path:

```text
docs/orchestrator/evidence/Mx/playwright/
```

## Minimal Actions

- open page
- wait for stable state
- confirm text / element presence
- click / type / select / submit
- inspect console / network
- capture screenshots

## Discipline

- no idle browser sessions
- reuse a live browser only when useful
- record persistent browser state in `session-brief.md`
