# Stage Gates

This file defines entry conditions, prohibited actions, and exit conditions for each orchestrator stage.

Use it when deciding whether a project may move forward.

## Global Gate Rules

### Rule 1: No silent stage skipping
A stage may be skipped only when repository state proves its outputs already exist and are still valid.

### Rule 2: Outputs before transition
Do not claim a stage is complete until its required durable outputs are written or updated.

### Rule 3: High-impact ambiguity blocks progress
If ambiguity affects scope, stack, acceptance, permissions, data model, UI structure, or integration behavior, do not advance.

### Rule 4: Frozen stages stay frozen
Once in `milestone-plan` or `execution`, scope is frozen by default.

### Rule 5: Verification gates completion
No milestone or project completion without fresh verification evidence.

## 1. Intake

### Entry Conditions
Enter when any of these are true:
- repository already contains code
- repository already contains planning docs
- work was interrupted previously
- user asked to continue an existing project
- current project state is unclear

### Required Inputs
- repository contents
- existing docs if any
- existing code if any
- git state if available

### Required Outputs
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/gap-analysis.md`
- initial or updated `docs/orchestrator/session-brief.md`

### Prohibited
- rewriting existing planning before assessing it
- assuming project is greenfield
- starting implementation before continuity is understood

### Exit Conditions
Exit only when one of these is explicitly true:
- existing state is valid enough to continue directly
- existing state needs specific planning patches first
- project must materially re-plan

## 2. Discovery

### Entry Conditions
Enter when:
- project goal is not precise enough
- user outcomes are unclear
- scope boundary is unclear
- non-goals are missing
- success criteria are weak

### Required Inputs
- user objective
- target users if known
- repo context if relevant

### Required Outputs
- `docs/orchestrator/product-spec.md`

### Prohibited
- jumping into stack selection before goal clarity
- jumping into implementation planning
- treating vague feature labels as finished requirements

### Exit Conditions
Exit only when all are true:
- project goal is concrete
- target users or usage mode are clear enough
- scope boundary exists
- non-goals exist
- high-level success criteria exist

## 3. Full Definition

### Entry Conditions
Enter when:
- project goal exists
- high-level direction exists
- implementation detail is still incomplete

### Required Inputs
- `product-spec.md`

### Required Outputs
- `feature-breakdown.md`
- supporting planning docs as needed

### Prohibited
- stopping at feature names only
- leaving main, branch, or error flows undefined for core functionality
- leaving ownership, permissions, or state behavior implicit for core entities

### Exit Conditions
Exit only when:
- core features are decomposed to implementable detail
- high-impact states and behaviors are defined
- acceptance-relevant behavior is understandable without guesswork

## 4. UI Definition

### Entry Conditions
Enter when:
- project has meaningful UI
- page structure, flows, or style direction are still unresolved

Skip only when project is meaningfully non-UI.

### Required Inputs
- `product-spec.md`
- `feature-breakdown.md`

### Required Outputs
- `ui-style-directions.md`
- `ui-spec.md`
- `ui-implementation-contract.md`
- persisted inspiration images for candidate directions
- approved persisted implementation-reference images for pages that are moving toward implementation

### Prohibited
- entering UI implementation with only visual mood and no structural definition
- entering implementation with only wireframes and no state behavior for core pages
- deferring core UI state definitions to implementation for core flows
- for a new project with meaningful UI, skipping the visual track and jumping directly to page code
- jumping from a small inspiration image directly to page code without producing and approving a larger implementation-reference image

### Exit Conditions
Exit only when:
- user-approved style direction exists
- core pages are defined at high fidelity
- secondary pages are defined enough for planned implementation
- core components have defined states
- implementation contract exists

If the project has confirmed UI direction but page code is not yet allowed, stay in `ui-definition` / `decision-closure` until all of these are true:
- section breakdown exists
- persisted section slice artifacts exist
- `Pre-Implementation Brief` exists
- approved implementation-reference images exist
- user has confirmed the brief
- user has confirmed the section breakdown

Do not enter page implementation with only a concept image, only a style frame, or only a route sketch.
For confirmed UI work, the approved image design is the acceptance baseline; the text brief must not replace or reinterpret it.

## 5. Decision Closure

### Entry Conditions
Enter when:
- broad planning exists
- high-impact decisions remain unresolved

### Required Inputs
- `product-spec.md`
- `feature-breakdown.md`
- UI planning outputs if applicable

### Required Outputs
- `decision-log.md`

### Prohibited
- moving to roadmap with unresolved stack choice
- moving to roadmap with unresolved acceptance model
- moving to roadmap with unresolved core data or permissions direction

### Exit Conditions
Exit only when all high-impact decisions are explicitly:
- resolved
- deferred outside current project scope
- or converted into blocking user decisions

No unresolved high-impact item may remain open.

## 6. Roadmap

### Entry Conditions
Enter when:
- discovery and definition are strong enough
- high-impact decisions are closed
- project scope can be split into milestones

### Required Inputs
- `product-spec.md`
- `feature-breakdown.md`
- `decision-log.md`

### Required Outputs
- `roadmap.md`

### Prohibited
- milestone slicing that produces only technical fragments with no usable closure unless unavoidable
- starting milestone implementation without milestone ordering and dependencies

### Exit Conditions
Exit only when:
- milestone list exists
- dependencies between milestones are clear enough
- current milestone is identified
- milestone closure criteria are meaningful

## 7. Milestone Spec

### Entry Conditions
Enter when:
- roadmap exists
- current milestone is selected
- milestone needs detailed definition

### Required Inputs
- `roadmap.md`
- relevant global planning docs

### Required Outputs
- `milestones/Mx-spec.md`

### Prohibited
- implementation planning without milestone-level spec
- deferring core milestone behavior to implementation guesses
- leaving milestone non-scope undefined when scope pressure exists

### Exit Conditions
Exit only when:
- milestone scope is explicit
- milestone non-scope is explicit
- milestone behavior is detailed enough for planning
- milestone acceptance criteria exist

## 8. Milestone Plan

### Entry Conditions
Enter when:
- milestone spec exists
- milestone acceptance exists
- milestone is implementation-ready in definition

### Required Inputs
- `milestones/Mx-spec.md`

### Required Outputs
- `milestones/Mx-plan.md`
- `milestones/Mx-test-plan.md`
- `risk-matrix.md` if missing or stale

### Prohibited
- implementation without test planning
- scope expansion during planning without updating spec
- leaving verification commands undefined
- leaving task decomposition too vague to execute predictably

### Exit Conditions
Exit only when:
- implementation plan is specific enough to execute
- test plan exists
- risk matrix exists and reflects current milestone
- current scope freeze can begin

## 9. Execution

### Entry Conditions
Enter when all are true:
- milestone spec exists
- milestone plan exists
- milestone test plan exists
- high-impact decisions remain closed
- scope freeze is active
- for UI pages, section breakdown exists
- for UI pages, persisted section slice artifacts exist
- for UI pages, `Pre-Implementation Brief` exists
- for UI pages, approved implementation-reference images exist
- for UI pages, user has confirmed the brief
- for UI pages, user has confirmed the section breakdown

### Required Inputs
- active milestone docs
- active risk matrix
- relevant references only

### Required Outputs
- code changes
- tests
- updated `milestones/Mx-task-state.md`
- updated `session-brief.md`
- verification evidence as work progresses

### Prohibited
- reopening first-order decisions casually
- expanding scope silently
- replacing existing dependencies with custom code without justification
- starting duplicate long-lived processes without need
- letting process sprawl accumulate
- entering page code generation without the UI hard gates above
- re-designing confirmed UI from the text brief instead of implementing the approved image design

### Exit Conditions
Exit only when:
- planned task batch is implemented
- required tests and reviews are complete for that batch
- state files are updated
- either next execution step is clear or blocking issue is escalated

## 10. Debugging

### Entry Conditions
Enter when:
- failing tests block progress
- broken behavior blocks progress
- environment ambiguity blocks progress
- defect source is unclear

### Required Inputs
- failing evidence
- relevant code and tests
- current milestone docs

### Required Outputs
- root cause classification
- repair strategy
- updated verification evidence
- updated task state

### Prohibited
- guess-fixing
- changing spec to excuse a bug without explicit re-evaluation
- treating flaky symptoms as resolved without evidence

### Exit Conditions
Exit only when:
- root cause is identified
- repair is verified
- or blocker is escalated clearly

## 11. Verification

### Entry Conditions
Enter when:
- implementation or debugging work is ready to be checked
- acceptance-relevant behavior changed
- milestone closure is being considered

### Required Inputs
- milestone plan
- milestone test plan
- current code state

### Required Outputs
- `milestones/Mx-verification-report.md`

### Prohibited
- using stale test runs as evidence
- making completion claims before running current checks
- substituting intuition for evidence

### Exit Conditions
Exit only when:
- required verification commands were run freshly
- results were read and classified
- milestone closure state is evidence-backed

## 12. Handoff

### Entry Conditions
Enter when:
- ending a session
- pausing substantial work
- closing a milestone
- transferring context to future session

### Required Inputs
- current execution or verification status
- backlog changes
- blocker list
- process inventory

### Required Outputs
- updated `session-brief.md`
- updated `milestones/Mx-task-state.md`
- `final-handoff.md` when closing milestone or project

### Prohibited
- ending session with stale next-step info
- leaving hidden blockers undocumented
- leaving persistent processes undocumented

### Exit Conditions
Exit only when:
- next session first step is explicit
- current stage is explicit
- current milestone is explicit
- blockers are explicit
- process inventory is explicit if relevant

## 13. Done

### Entry Conditions
Enter only when claiming closure.

### Required Inputs
- fresh verification evidence
- current milestone or project docs
- acceptance criteria

### Required Outputs
- final updated handoff documents
- categorized backlog remainder

### Prohibited
- calling work done because code exists
- calling work done because partial tests passed
- calling work done while acceptance is ambiguous

### Exit Conditions
Exit only when closure is real and documented.

## Scope Freeze Gates

### Freeze Starts At
- `milestone-plan`
- `execution`

### Allowed Through Freeze
- blocker fixes
- acceptance-validity fixes
- severe risk fixes
- spec/plan correction when existing docs are wrong

### Not Allowed Through Freeze By Default
- opportunistic new features
- speculative enhancements
- low-value polish
- architecture rewrites without trigger condition

## Change Escalation Gate

Escalate change formally when it affects:
- project goal
- technology stack
- milestone acceptance
- core data model
- permissions/security boundary
- core UI structure
- key external integration
- validity of current plan

When escalated, use change request workflow before continuing.

## First-Order Decision Gate

These require user confirmation before advancing past closure-relevant stages:
- project goal
- stack
- UI style direction
- high-risk testing priorities
- final acceptance

No silent confirmation.

## Recovery Gate

If durable project state is stale or contradictory:
- update durable state before large new work
- do not proceed on memory alone

## Minimal Resume Gate

A new session may resume execution only when:
- `session-brief.md` exists and is current enough
- active milestone task state exists
- no unresolved contradictory blocker is hidden

Otherwise return to `intake`.
