# Workflow

This file defines the operating workflow for `project-orchestrator`.

Use it after reading `SKILL.md` and only when workflow-level guidance is needed.

## Operating Model

The orchestrator does not solve every task directly. It manages project flow.

Its responsibilities are:

- identify current project stage
- verify required gates for that stage
- route to the right skill
- ensure durable project documents stay current
- reduce execution drift
- minimize unnecessary user interruption
- preserve recoverability across sessions

## Global Flow

```text
intake
  -> discovery
  -> product-definition
  -> ui-definition (if applicable)
  -> system-definition
  -> decision-closure
  -> roadmap
  -> milestone-spec
  -> milestone-plan
  -> execution
  -> debugging (when needed)
  -> verification
  -> handoff
  -> done
```

Not every project starts at `discovery`.

Existing projects may begin at `intake`, then jump forward after gap assessment.

## Stage Entry Rule

Before acting, determine:

1. what stage the project is currently in
2. what documents already exist
3. what unresolved decisions remain
4. whether current scope is too large for one closed milestone
5. whether there is a valid next action without user interruption

Never assume the project is greenfield.

## 1. Intake

Use when:
- project already has code
- project already has planning docs
- work was interrupted previously
- user wants continuation rather than restart

### Intake Objectives

- identify reusable planning artifacts
- identify actual implemented system state
- identify planning gaps
- classify project continuation path

### Intake Steps

1. Inspect repository docs
2. Inspect codebase structure
3. Inspect tests and verification artifacts
4. Inspect git state if available
5. Create or update:
   - `current-state.md`
   - `gap-analysis.md`
6. Decide one of:
   - continue directly
   - patch planning, then continue
   - materially re-plan

### Intake Rule

Prefer patching and adoption over rewriting.

Only force major re-planning when:
- existing planning is internally contradictory
- planning is too incomplete to safely continue
- code and docs diverge too far
- acceptance target is unclear

## 2. Discovery

Use when project goal or scope is not yet stable.

### Discovery Objectives

Define:
- who project is for
- what problem it solves
- what success means
- what is explicitly out of scope

### Discovery Outputs

Update or create:
- `product-spec.md`

### Discovery Stop Condition

Do not leave discovery until project goal is concrete enough to evaluate:
- scope
- stack
- milestone slicing
- acceptance

## 3. Product Definition

Use when high-level direction is known but feature and interaction behavior are not yet locked.

### Product Definition Objectives

Push product behavior to implementation-guiding detail before system design.

Must cover:
- feature inventory
- main flows
- branch flows
- failure flows
- page responsibilities
- route structure
- component boundaries
- loading/empty/error states
- validation rules
- acceptance expectations
- interaction rules

### Product Definition Outputs

Create or update:
- `feature-breakdown.md`
- supporting planning artifacts as needed

### Product Definition Rule

Do not stop at labels like "user management" or "dashboard".

Every major feature should be understandable as behavior and interaction.

## 4. UI Definition

Use only when project contains meaningful user interfaces.

Enter this stage after the product and interaction definition is concrete enough to render.

### UI Definition Objectives

Plan UI in two parallel tracks:

#### Structural track
- information architecture
- page inventory
- key user flows
- page states
- component boundaries

#### Visual track
- 2-3 style directions
- small inspiration frames saved to disk
- recommended direction
- user-approved direction for expansion
- large implementation-reference images saved to disk
- user-approved final implementation reference

### UI Outputs

Create or update:
- `docs/orchestrator/ui/ui-style-directions.md`
- `docs/orchestrator/ui/ui-spec.md`
- `docs/orchestrator/ui/ui-implementation-contract.md`
- `docs/orchestrator/ui/section-breakdown.md`
- `docs/orchestrator/ui/pre-implementation-brief.md`

Persist assets under:
- `docs/orchestrator/ui/inspirations/`
- `docs/orchestrator/ui/references/`
- `docs/orchestrator/ui/sections/`

### UI Rule

UI planning must guide implementation.

Do not produce visual-only artifacts with no implementation contract.
Do not jump from small inspiration frames directly to page code.
Do not start page implementation until approved implementation-reference images, persisted section artifacts, and an approved `Pre-Implementation Brief` exist.
Do not allow implementation when design images are not produced and approved.

## 5. System Definition

Use after product behavior is defined and, for UI-bearing projects, after UI direction is approved.

### System Definition Objectives

Define the system around approved product and UI decisions.

Must cover:
- roles and permissions
- data model intent
- state transitions
- page/API interfaces
- architecture direction
- external integration needs
- testing expectations
- observability expectations
- deployment assumptions

### System Definition Outputs

Create or update:
- supporting planning artifacts as needed

### System Definition Rule

System design must refine delivery details, not reopen approved product behavior or approved UI.

## 6. Decision Closure

Use after broad planning and before roadmap or implementation.

### Decision Closure Objectives

Close all high-impact decisions that would otherwise interrupt implementation.

Must explicitly resolve:
- technology stack
- architecture direction
- product interaction direction
- UI direction
- data model direction
- permissions model
- testing posture
- milestone slicing
- acceptance rules

### Decision Outputs

Create or update:
- `decision-log.md`

### Decision Closure Rule

No unresolved high-impact decision may remain open before `roadmap`.

## 7. Roadmap

Use after planning is sufficiently closed.

### Roadmap Objectives

Split work into milestones.

Prefer:
- user-value closed loops
- minimal cross-milestone ambiguity
- milestone-level testability
- milestone-level handoff

### Roadmap Outputs

Create or update:
- `roadmap.md`

### Roadmap Rule

A milestone must be independently:
- spec-able
- plannable
- executable
- testable
- handoff-able

## 8. Milestone Spec

Use for the active milestone only.

### Milestone Spec Objectives

Turn roadmap milestone into a complete milestone-level spec.

Must define:
- scope
- non-scope
- user flows
- system behavior
- interfaces
- data changes
- permissions
- UI states
- test targets
- integration requirements
- acceptance criteria

### Milestone Spec Outputs

Create or update:
- `milestones/Mx-spec.md`

### Milestone Spec Rule

Spec should be complete enough that implementation planning does not invent behavior.

## 9. Milestone Plan

Use only after milestone spec is complete.

### Milestone Plan Objectives

Translate milestone spec into implementable steps.

Include:
- work decomposition
- file ownership or edit zones where useful
- testing plan
- verification commands
- review points
- handoff expectations

### Milestone Plan Outputs

Create or update:
- `milestones/Mx-plan.md`
- `milestones/Mx-test-plan.md`
- `risk-matrix.md` if missing or stale

### Milestone Plan Rule

After entering this stage, scope freezes by default.

Only blocking or validity-breaking changes may interrupt.

## 10. Execution

Use when plan is approved and gates are clear.
For UI-bearing work, `execution` is allowed only after design images exist, are persisted, and are user-approved.

### Execution Objectives

Implement current milestone with minimal drift.

### Default Execution Stack

Use:
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:test-driven-development`
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`

### Execution Rule

Execution should not reopen major planning.

Execution may:
- clarify plan-local details
- implement
- test
- verify
- patch small mismatches

Execution may not:
- silently expand scope
- silently revise acceptance
- silently replace stack choices

### Execution Durable Updates

During execution, update:
- `milestones/Mx-task-state.md`
- `session-brief.md`

## 11. Debugging

Use when progress is blocked by failing behavior, unstable tests, broken assumptions, or unclear defect source.

### Debugging Objectives

Identify root cause before repair.

Use:
- `superpowers:systematic-debugging`

### Debugging Rule

Do not guess-fix.

Classify failure first:
- implementation bug
- test bug
- environment issue
- spec drift
- integration issue

Then repair accordingly.

## 12. Verification

Use after implementation or repair work.

### Verification Objectives

Confirm milestone behavior using fresh evidence.

Verification includes:
- required test runs
- regression runs based on impact
- critical path checks
- acceptance checks

### Verification Outputs

Create or update:
- `milestones/Mx-verification-report.md`

### Verification Rule

No stale evidence.
No assumed passing state.
No completion claim before fresh verification.

## 13. Handoff

Use whenever:
- ending a work session
- ending a milestone
- transferring work to future session
- pausing after major progress

### Handoff Objectives

Make next session low-friction.

Must record:
- current stage
- active milestone
- active task
- latest verification
- blockers
- backlog changes
- persistent process inventory
- next exact step

### Handoff Outputs

Create or update:
- `session-brief.md`
- `milestones/Mx-task-state.md`
- `final-handoff.md` when closing milestone or project

## 14. Done

Use only when current milestone or project closure is real.

### Done Conditions

All must be true:
- scope complete for target closure
- acceptance satisfied
- verification fresh
- backlog categorized
- handoff complete
- no hidden unresolved blocker

## Workflow Shortcuts

These are allowed only when gates still hold:

### Shortcut A: Existing planning is strong
`intake -> roadmap` or `intake -> milestone-spec`

Allowed when:
- existing docs are coherent
- high-impact decisions already closed
- current-state and gap-analysis confirm continuity

### Shortcut B: Existing milestone plan already valid
`intake -> execution`

Allowed when:
- milestone plan is current
- test plan exists
- scope freeze is clear
- active state docs are reliable

### Shortcut C: No UI project
Skip `ui-definition`

Allowed when:
- project is backend-only
- infra-only
- CLI/tooling-only
- UI is not meaningful to delivery

## Cross-Stage Rules

### Rule: Durable state first
If repo state is stale, update repo state before continuing long work.

### Rule: Narrow loading
Read only the stage-relevant references and templates.

### Rule: Reuse first
Before implementation choices, prefer:
1. existing code
2. existing deps
3. mature dependency
4. custom code

### Rule: New ideas go to backlog
Do not interrupt execution for every new thought.

### Rule: Freeze means freeze
Once in `milestone-plan` or `execution`, scope remains frozen by default.

### Rule: Human interruption is expensive
Ask user only for:
- first-order decisions
- blocking contradictions
- invalidated acceptance
- stack decision
- final acceptance

## Recommended Stage-to-Skill Routing

| Stage | Primary skill(s) |
|------|-------------------|
| `intake` | `superpowers:using-superpowers`, `karpathy-guidelines` |
| `discovery` | `superpowers:brainstorming` |
| `product-definition` | `superpowers:brainstorming` |
| `ui-definition` | `superpowers:brainstorming` plus UI-related registered skills when applicable |
| `system-definition` | `superpowers:brainstorming` |
| `decision-closure` | `superpowers:brainstorming` |
| `roadmap` | `superpowers:brainstorming` |
| `milestone-spec` | `superpowers:brainstorming` |
| `milestone-plan` | `superpowers:writing-plans` |
| `execution` | `superpowers:using-git-worktrees`, `superpowers:subagent-driven-development`, `superpowers:test-driven-development` |
| `debugging` | `superpowers:systematic-debugging` |
| `verification` | `superpowers:verification-before-completion` |
| `handoff` | `superpowers:finishing-a-development-branch` when closing major work |

## Session Resume Flow

On a fresh session:

1. Read `docs/orchestrator/session-brief.md`
2. Read active milestone task state
3. Read `decision-log.md`
4. Read milestone plan or spec only if needed
5. Cross-check current code state
6. Continue from recorded next step

Do not re-expand the whole project unless the recorded state is stale or contradictory.
