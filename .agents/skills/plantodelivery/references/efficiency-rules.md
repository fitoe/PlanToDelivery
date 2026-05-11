# Efficiency Rules

Use this file during planning and execution to increase speed without lowering rigor.

## Core Principle

Move faster by reducing low-value loops, repeated context loading, repeated decisions, and unnecessary full verification.

## Rules

- Front-load high-impact decisions.
- Default second-order decisions to orchestrator recommendations.
- Prefer visible progress over invisible cleanup unless cleanup blocks the visible path.
- For UI-heavy work, build visual shell and mock interactions before deep functional wiring.
- Run narrow tests in narrow loops.
- Expand verification only at meaningful checkpoints.
- Do not polish before the core flow closes.
- Defer new ideas to backlog unless they invalidate the active milestone.
- Reuse code and dependencies before building custom solutions.
- Load only stage-relevant references and templates.

## Validation Budget

Match verification to the current layer:

- active editing: default to no command-driven verification. Trust model-generated local code, use code review and cheap editor/runtime signals, and keep the implementation flow moving.
- `visual-shell`: touched-file lint only when cheap or already available, route/page opens, no visible/runtime blocker.
- `interaction-shell`: visual-shell checks plus demo path smoke, console/runtime check, local state feedback.
- `functional-wiring`: focused tests for real logic, API/adapters, persistence, permissions, and current milestone path.
- `hardening`: full lint/build/type-check, regression, E2E, performance/accessibility/release checks as needed.

Do not run full suites after every small visual edit. Historical lint/type/test failures and third-party type issues should be recorded as baseline blockers unless touched code introduced them.

Full lint, full type-check, and full build are stage-gate commands. Run them at slice closure, milestone hardening, merge readiness, release readiness, or when a high-risk foundation changes.

High-risk foundation changes include:
- dependency manifests or lockfiles
- build, bundler, lint, test, or TypeScript configuration
- shared types, public APIs, routing foundations, or cross-module contracts
- auth, permissions, payment, security, privacy, data mutation, schema, migration, or persistence code
- broad refactors with cross-module blast radius

Default validation budget:
- active editing: 0 command runs unless a cheap concrete signal identifies a problem
- slice completion: 1 focused verification group for touched or impacted behavior
- milestone hardening: full lint, full type-check, full build, and required regression
- merge or release: full verification unless explicitly waived with recorded risk

## Timebox and Defer

Non-blocking problems must not trap execution indefinitely.

Default debug timeboxes:
- visual-shell: 15 minutes
- interaction-shell: 20 minutes
- functional-wiring: 30 minutes
- hardening: resolve or explicitly accept

If the timebox expires and the issue is not a blocker, record it in the Deferred Work Ledger with impact, workaround, and revisit stage, then continue the visible delivery path.

Blockers are limited to: app cannot start, target page cannot render, primary demo path is broken, current real functionality cannot work, data/security risk, or user-approved acceptance is impossible.

## No Endless Loops

If two consecutive attempts at lint, test, type-check, visual polish, or non-blocking debugging do not produce clear progress, stop the loop. Classify the issue as blocker, baseline, deferred, or polish backlog. Continue the next visible or milestone-critical task unless the issue is a blocker.

Do not let full-suite failures hijack a visual-shell or interaction-shell slice when touched code is not responsible. Record baseline failures and keep the current layer moving.

When a deferred stage-gate check fails, classify the failure before fixing:
- blocker: caused by current scope and prevents the current stage goal
- baseline: pre-existing or unrelated project debt
- environment: local setup, network, tool, or third-party issue
- deferred: real issue outside the current stage goal

Only blockers must interrupt the current delivery path.

## Visible Checkpoint Rhythm

Prefer short execution heartbeats. Every visible-first checkpoint should answer:
- what new thing can the user see or try in dev
- what remains mock/demo/pending
- which real functionality is deferred and to what stage
- which issues are blockers vs non-blockers
- the next visible or milestone-critical step

Do not spread effort evenly across all features. Prioritize primary demo path depth, secondary path visibility, and future path placeholders.

## Process Efficiency

- Keep short commands foreground-only.
- Minimize long-lived processes.
- Reuse existing servers/watchers if already running.

## Anti-Patterns

Do not:
- run full suites on every tiny change
- run `build`, full type-check, or full lint as routine edit-loop commands
- reopen planning during normal execution
- introduce speculative dependencies
- overdesign for unlikely future states
