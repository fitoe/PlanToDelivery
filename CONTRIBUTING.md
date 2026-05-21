# Contributing to PlanToDelivery

Thanks for contributing.

PlanToDelivery is a workflow product, not only a file collection. Good contributions improve:

- process clarity
- recovery reliability
- milestone execution quality
- testing/verification discipline
- real-world usability

## Contribution Priorities

High-value contributions usually fall into one of these categories:

- fix contradictions between `SKILL.md`, `references/`, `templates/`, and `docs/orchestrator/`
- improve Hermes Kanban constraints or routing logic
- improve durable-state or recovery behavior
- improve template usefulness in real project work
- add evidence-backed improvements from trial runs

## Before You Change Anything

1. Understand the current stage model.
2. Check whether the change affects:
   - first-order decisions
   - stage transitions
   - recovery assumptions
   - durable docs
3. Prefer surgical changes.

## Working Rules

- Keep changes traceable to a real workflow need.
- Prefer improving existing files over adding new clutter.
- Do not add broad theory with no execution value.
- Do not silently change the meaning of a stage.
- Keep progressive loading in mind. Avoid bloating `SKILL.md`.

## Recommended Workflow

1. Open an issue or trial-use feedback entry if the change is non-trivial.
2. Make a focused branch or commit.
3. Update related docs when behavior changes.
4. Include validation evidence in the PR.

## Validation Expectations

At minimum, contributors should:

- check file consistency
- confirm referenced files exist
- review affected docs for contradictions

If the change affects workflow behavior, include trial-use evidence when possible.

## What Not to Add Casually

- extra top-level docs with low signal
- duplicate guidance already covered elsewhere
- speculative frameworks with no real use case
- new stages without strong justification

## Pull Requests

Use the PR template and describe:

- what changed
- why it changed
- what was validated
- what remains risky or deferred
