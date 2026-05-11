# Testing Strategy

Use this file when creating, reviewing, or executing milestone-level testing plans.

This strategy is designed to balance:
- strong quality control
- efficient execution
- milestone-based delivery
- minimal wasted verification work
- cross-session recoverability

## Testing Ladder

Use the lightest layer that matches the current delivery layer:

- Level 0: compile/build smoke or route render check.
- Level 1: touched-file lint and obvious runtime/console checks.
- Level 2: page/demo-path smoke with mock data and visible state checks.
- Level 3: focused unit/integration tests for current real functionality.
- Level 4: full build, full lint, type-check, targeted regression.
- Level 5: E2E/regression/release validation for milestone closure.

Default mapping:
- `visual-shell`: Level 0-1, plus user/dev visual review when appropriate.
- `interaction-shell`: Level 0-2.
- `functional-wiring`: Level 0-3, expanding only around current real paths.
- `hardening`: Level 4-5.

Do not fail a visual-shell checkpoint because real APIs are not wired, and do not claim functional completion with mock-only behavior.

Layer-specific assessment rule: judge each checkpoint only against its declared layer. Visual-shell asks whether the visible page can be reviewed; interaction-shell asks whether the demo path responds; functional-wiring asks whether current real paths work; hardening asks whether the committed real scope is release-stable.

Mock exit rule: before functional-wiring, release, or production integration, each mock item must be replaced, explicitly kept as demo-only, or deferred with user-visible acceptance.

## Deferred Verification Model

Default to trust-first, checkpoint-based verification during active development.

The development loop should preserve flow:
- trust model-generated local code unless there is a concrete signal of breakage
- do not run full lint, full type-check, or full build after every small edit
- use code review, editor diagnostics, and cheap sanity checks during active editing
- defer broad verification until a meaningful checkpoint

Full lint, full type-check, and full build are stage-gate tools, not routine edit-loop tools.

Meaningful checkpoints are:
- visual slice completion
- interaction slice completion
- functional slice completion
- milestone verification and handoff
- merge, release, or production-readiness review

Run earlier verification only when the change touches high-risk foundations:
- dependency manifests or lockfiles
- build, Vite, bundler, lint, test, or TypeScript configuration
- shared types, public APIs, routing foundations, or cross-module contracts
- auth, permissions, payments, security, privacy, or data mutation paths
- database schema, migrations, persistence adapters, or destructive operations
- large refactors that touch many modules

When verification is deferred, record any known risk in the task state, test plan, deferred work ledger, or handoff notes. Deferred verification is acceptable only when the current layer can still be described honestly.

## Core Testing Model

Testing is organized by both:

- risk
- layer

Use both.

## Primary Goals

Testing must protect two things at once:

1. user-value closure
2. high-risk lower-level correctness

## Testing Principles

- Every milestone needs a written test plan before implementation starts.
- Tests should be selected for value, not vanity coverage.
- High-risk behavior gets deeper coverage.
- E2E is expensive. Add it after core flows stabilize.
- Regression scope should be chosen intelligently.
- When tests fail, classify cause before fixing.
- Test artifacts must exist in docs, not only in code.

## Testing Planning Levels

Each milestone test plan should cover two planning views:

### 1. User-flow view
Define:
- critical user journeys
- milestone acceptance journeys
- likely failure or interruption points
- flow-level observable success criteria

### 2. Module-risk view
Define:
- high-risk services, modules, or stateful components
- correctness-sensitive logic
- persistence-sensitive logic
- permission-sensitive logic
- integration-sensitive logic

## Risk-Based Testing

Before implementation or early in milestone planning, build a risk matrix.

Risk can come from:
- core business importance
- security sensitivity
- permission complexity
- state transition complexity
- data mutation severity
- integration fragility
- concurrency or consistency behavior
- production blast radius
- frequent change likelihood

## Layered Testing Model

Choose test type by purpose.

### Unit tests
Best for:
- pure logic
- state transitions
- validation rules
- formatting/parsing rules
- small deterministic utilities

### Integration tests
Best for:
- module interaction
- database interaction
- API route + service wiring
- auth/authz enforcement
- persistence behavior
- external integration wrappers

### E2E tests
Best for:
- critical user journeys
- cross-layer closure checks
- UI-to-backend path validation
- smoke tests for milestone acceptance

### Playwright browser validation
Best for:
- critical browser-side user flows
- interaction-specific bug reproduction
- browser evidence collection
- milestone acceptance checks that need screenshots, console, or network evidence

## Coverage Strategy

Default coverage target is high-value coverage, not universal blanket coverage.

### Must cover deeply
- critical user flows
- high-risk write paths
- permissions and security boundaries
- state machines
- destructive operations
- external integration error handling
- core persistence behavior

### Cover adequately
- important supporting modules
- secondary flows that support milestone closure

### Cover minimally
- low-risk, low-value, stable areas
- cosmetic-only behavior unless acceptance depends on it

## E2E Timing Rule

Default order:
1. unit and integration for core behavior
2. stabilize main implementation path
3. add E2E for accepted critical flows
4. expand E2E only where justified

Playwright may begin early for debugging or narrow validation, but broad browser suites still wait until core flows stabilize.

## Regression Strategy

Regression should be smart, not reflexively global.

Choose regression scope based on:
- files/modules changed
- dependency graph implications
- risk classification
- current milestone criticality
- release proximity

## Test Failure Triage

Never treat red output as automatic proof of implementation bug.

First classify failure:

- implementation defect
- test defect
- environment/setup issue
- flaky timing issue
- outdated expectation after approved design change
- external dependency issue
- spec/plan drift

Then act.

## Milestone Test Plan Contents

Each milestone test plan should define:

- milestone name
- milestone goal
- testing objectives
- critical user flows
- high-risk modules
- risk matrix summary
- planned unit coverage areas
- planned integration coverage areas
- planned E2E coverage areas
- planned Playwright/browser validation areas
- explicit out-of-scope testing
- regression strategy
- security testing needs
- integration testing needs
- performance-sensitive validation if relevant
- milestone acceptance checks

## Documentation Requirements

Testing must not live only in code.

Keep milestone-level durable artifacts:
- `Mx-test-plan.md`
- `Mx-regression-plan.md`
- `Mx-verification-report.md`

When browser evidence matters, also record:
- whether Playwright was used
- which flows or pages it covered
- where screenshots, logs, or network traces were saved

## Efficiency Rules

### Allowed efficiency moves
- trust model-generated local code during active development unless a concrete failure signal appears
- run focused test subsets during local implementation loops
- defer full lint, full type-check, and full build until meaningful checkpoints
- defer broad regression until meaningful checkpoints
- defer E2E until core flows stabilize
- prioritize high-value risk areas first
- in visual-shell, use mock data and page smoke checks instead of full functional test gates
- record historical lint/type/test failures as baseline blockers when unrelated to touched code

### Not allowed
- skipping written test planning for real functionality
- relying only on manual testing for critical real logic
- using full-suite runs for every small edit without reason
- treating full lint, full type-check, or full build as mandatory edit-loop commands
- blocking visible progress on non-blocking historical or third-party failures
- claiming functional coverage because a mock or demo path looks correct
- claiming coverage because "it seems simple"

## Exit Criteria for Testing Readiness

A milestone is testing-ready for execution only when:
- test objectives are documented
- critical user flows are named
- high-risk modules are identified
- test types are allocated appropriately
- regression strategy is defined
- acceptance checks are listed
