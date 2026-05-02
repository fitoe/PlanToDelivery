# Planning Contract

Use this file during `discovery`, `full-definition`, `ui-definition`, `decision-closure`, and `milestone-spec`.

## Purpose

Keep planning deep enough to reduce execution drift, but not so abstract that implementation still has to invent core behavior.

## Rules

- Plan behavior, not labels.
- Define main paths, branch paths, and failure paths for core features.
- Close high-impact ambiguity before implementation planning.
- Prefer explicit defaults for second-order decisions.
- Capture enough detail that milestone plans can decompose work without inventing product logic.

## Required Planning Outputs

At the appropriate stages, planning should produce or update:

- `product-spec.md`
- `feature-breakdown.md`
- `decision-log.md`
- `roadmap.md`
- `ui-*` docs when UI exists
- milestone specs

## Anti-Patterns

Do not:
- stop at feature names
- defer key state behavior to implementation
- leave acceptance ambiguous
- ask the user to decide every minor detail
