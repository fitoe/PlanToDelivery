# Efficiency Rules

Use this file during planning and execution to increase speed without lowering rigor.

## Core Principle

Move faster by reducing low-value loops, repeated context loading, repeated decisions, and unnecessary full verification.

## Rules

- Front-load high-impact decisions.
- Default second-order decisions to orchestrator recommendations.
- Run narrow tests in narrow loops.
- Expand verification only at meaningful checkpoints.
- Do not polish before the core flow closes.
- Defer new ideas to backlog unless they invalidate the active milestone.
- Reuse code and dependencies before building custom solutions.
- Load only stage-relevant references and templates.

## Process Efficiency

- Keep short commands foreground-only.
- Minimize long-lived processes.
- Reuse existing servers/watchers if already running.

## Anti-Patterns

Do not:
- run full suites on every tiny change
- reopen planning during normal execution
- introduce speculative dependencies
- overdesign for unlikely future states
