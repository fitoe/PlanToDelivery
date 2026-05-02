# Execution Contract

Use this file during `execution`.

## Purpose

Keep implementation aligned with approved planning while preserving speed and verification discipline.

## Rules

- Execute against the active milestone spec and plan.
- Reuse existing code and dependencies before introducing new implementation.
- Follow TDD for new behavior and bug fixes.
- Keep scope frozen unless a valid escalation trigger occurs.
- Update durable state as work progresses.
- Verify narrowly during local loops and more broadly at slice or milestone boundaries.

## Allowed During Execution

- clarify plan-local detail
- implement approved scope
- add tests
- run verification
- patch small mismatches between plan and repo reality
- use narrow browser validation for critical UI behavior when cheaper checks are insufficient

## Not Allowed During Execution

- silent scope expansion
- silent architecture changes
- casual reopening of first-order decisions
- process sprawl
- hand-waving verification

## Browser Validation Rule

Use Playwright during execution only when it materially helps:

- confirm critical page behavior
- confirm key interaction slices
- reproduce browser-visible bugs early

Do not escalate every UI change into broad browser automation.
