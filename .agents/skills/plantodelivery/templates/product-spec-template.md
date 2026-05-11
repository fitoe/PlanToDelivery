# Product Spec

## Document Control
- Project name:
- Spec owner:
- Version:
- Status:
  - `draft / review / approved / superseded`
- Last updated:
- Related milestone roadmap:
- Related decision log:

## Project Goal
Describe the project in one sharp paragraph.

- Problem being solved:
- Intended outcome:
- Why this project should exist now:

## Success Definition
Define what success means at project level.

- Primary success outcome:
- Secondary success outcomes:
- Failure conditions:
- What would make this project not worth shipping:

## Users
Define who the project is for.

### Primary users
- User type:
- Core motivation:
- Main job to get done:

### Secondary users
- User type:
- Core motivation:
- Main job to get done:

### Non-target users
- Who is explicitly not the target:
- Why:

## Usage Context
Define where and how the product is used.

- Environment of use:
- Frequency of use:
- Device or platform assumptions:
- Time-sensitivity assumptions:
- Collaboration or solo-use assumptions:

## Scope
Define what this project includes.

### In scope
- Capability:
- Why it belongs in scope:

### Out of scope
- Capability:
- Why it is excluded:

### Deferred
- Capability:
- Why it is deferred:
- Expected future milestone or backlog category:

## Core User Value
Describe the user-value loop this project must close.

- Trigger:
- User action:
- System response:
- User receives value:
- What must be true for this loop to count as closed:

## Core Workflows
List the primary workflows the product must support.

### Workflow 1
- Name:
- Entry condition:
- Happy path:
- Key branches:
- Failure/interrupt conditions:
- Completion condition:

### Workflow 2
- Name:
- Entry condition:
- Happy path:
- Key branches:
- Failure/interrupt conditions:
- Completion condition:

## Functional Areas
List the major product areas.

### Area
- Name:
- Purpose:
- Why it matters:
- Dependencies:
- Planned milestone placement:
- Notes:

## Non-Goals
State what this project should not try to become.

- Non-goal:
- Why:
- Risk if accidentally included:

## High-Impact Constraints
Capture constraints that shape the product.

### Business constraints
- Constraint:
- Impact:

### Technical constraints
- Constraint:
- Impact:

### Operational constraints
- Constraint:
- Impact:

### Compliance/security/privacy constraints
- Constraint:
- Impact:

## Project Type Signals
Mark what planning depth this project likely needs.

- Has meaningful UI:
  - `yes/no`
- Has persistent data:
  - `yes/no`
- Has authentication:
  - `yes/no`
- Has authorization:
  - `yes/no`
- Has external integrations:
  - `yes/no`
- Has async/background work:
  - `yes/no`
- Has high-risk operations:
  - `yes/no`
- Has multi-user or tenant logic:
  - `yes/no`
- Has deployment beyond local:
  - `yes/no`
- Has performance-sensitive paths:
  - `yes/no`

## First-Order Decisions Requiring User Confirmation
List only the decisions the user must explicitly confirm.

- Project goal confirmation:
  - Current proposed answer:
  - Status:
    - `pending / confirmed`
- Technology stack confirmation:
  - Current proposed answer:
  - Status:
    - `pending / confirmed`
- UI style direction confirmation:
  - Current proposed answer:
  - Status:
    - `pending / confirmed / not-applicable`
- High-risk testing priorities confirmation:
  - Current proposed answer:
  - Status:
    - `pending / confirmed`
- Final acceptance framing confirmation:
  - Current proposed answer:
  - Status:
    - `pending / confirmed`

## Second-Order Decisions Delegated to Orchestrator
Record areas where orchestrator can recommend defaults unless user objects.

- Area:
- Default recommendation style:
- User override needed:
  - `yes/no`

## Acceptance Frame
Define project-level acceptance before milestone-level acceptance.

### Project must achieve
- Requirement:
- Why it matters:
- How it will be judged at high level:

### Project must not violate
- Constraint:
- Why it matters:

## Risks
Capture project-level risks early.

### Critical risks
- Risk:
- Why it matters:
- Early mitigation idea:

### High risks
- Risk:
- Why it matters:
- Early mitigation idea:

## Backlog Boundary
Define how new ideas should be treated.

- What kinds of changes should be deferred by default:
- What kinds of changes would justify interrupting current planning:
- What kinds of changes would justify interrupting execution:

## Related Durable Outputs Expected Next
- [ ] `feature-breakdown.md`
- [ ] `decision-log.md`
- [ ] `roadmap.md`
- [ ] `ui-style-directions.md` if UI exists
- [ ] `ui-spec.md` if UI exists
- [ ] `data-model.md` if persistent data exists
- [ ] `permission-matrix.md` if authz exists
- [ ] `security-baseline.md` if relevant
- [ ] `integration-registry.md` if integrations exist
- [ ] `performance-sensitive-paths.md` if performance-sensitive paths exist

## Review Notes
- What is still weak:
- What needs confirmation next:
- What should not block moving to full definition:
