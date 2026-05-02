# Testing Strategy

Use this file when creating, reviewing, or executing milestone-level testing plans.

This strategy is designed to balance:
- strong quality control
- efficient execution
- milestone-based delivery
- minimal wasted verification work
- cross-session recoverability

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

Playwright use may begin earlier for debugging or narrow browser-side validation, but broad browser suites should still wait until core flows stabilize.

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
- run focused test subsets during local implementation loops
- defer broad regression until meaningful checkpoints
- defer E2E until core flows stabilize
- prioritize high-value risk areas first

### Not allowed
- skipping written test planning
- relying only on manual testing for critical logic
- using full-suite runs for every small edit without reason
- claiming coverage because "it seems simple"

## Exit Criteria for Testing Readiness

A milestone is testing-ready for execution only when:
- test objectives are documented
- critical user flows are named
- high-risk modules are identified
- test types are allocated appropriately
- regression strategy is defined
- acceptance checks are listed
