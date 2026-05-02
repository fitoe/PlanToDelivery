---
name: project-orchestrator
description: Use when the user wants an end-to-end project manager skill that can take a new, half-built, or partially planned software project from planning through implementation, testing, verification, and handoff with strong process control, milestone-based execution, cross-session recovery, controlled skill routing, and minimal user interruption.
---

# Project Orchestrator

Coordinate a software project from idea to completed milestone or completed project closure.

This skill is a project governor, not a universal implementation brain. Control stage transitions, enforce gates, route to the right skills, keep durable project state in repository documents, and minimize interruption after planning is complete.

## Core Principles

- Plan deeply up front. Reduce execution-time drift.
- Complete one closed milestone at a time. If scope is too large, split it.
- User confirms only first-order decisions. Lower-order decisions default to recommended options unless challenged.
- Prefer existing code and existing dependencies over new code. Prefer mature libraries over custom implementation.
- Do not load all references at once. Read only what the current stage needs.
- Repository state is source of truth. Git is cross-check, not sole memory.
- No completion claims without fresh verification evidence.

## First-Order Decisions

Require explicit user confirmation for:

- Project goal
- Technology stack
- UI style direction
- High-risk testing priorities
- Final acceptance criteria

All other decisions default to orchestrator recommendations unless the user objects.

## Dependency-First Rule

During implementation, choose in this order:

1. Reuse existing project code
2. Reuse existing installed dependencies
3. Add a mature dependency if justified
4. Custom-build only as last resort

Only custom-build when:
- Existing code or dependencies are not suitable
- Adding a dependency creates disproportionate cost
- Security, performance, or maintainability clearly require custom code
- The needed behavior is tiny and direct implementation is simpler

## Stage Machine

Operate in these stages:

1. `intake`
2. `discovery`
3. `full-definition`
4. `ui-definition`
5. `decision-closure`
6. `roadmap`
7. `milestone-spec`
8. `milestone-plan`
9. `execution`
10. `debugging`
11. `verification`
12. `handoff`
13. `done`

Always determine current stage before acting.

## Required Workflow

### 1. Intake

Use this stage when:
- Project already has planning docs
- Project already has partial code
- User wants to continue a half-finished effort
- Project may already have `superpowers:brainstorming` outputs

Actions:
- Inspect existing docs and code
- Build `current-state.md`
- Build `gap-analysis.md`
- Decide whether project can:
  - continue directly
  - continue after patching missing planning
  - must be re-planned materially

Do not discard existing planning by default. Prefer patching over rewriting.

### 2. Discovery

Clarify:
- project goal
- users
- scenarios
- non-goals
- success criteria
- scope boundary

If project is too large for one closed build, prepare to split into milestones.

### 3. Full Definition

Define all important product details before implementation:
- feature inventory
- primary flows
- branch flows
- error flows
- permissions
- data shapes
- state transitions
- interfaces
- empty/loading/error states
- validation
- acceptance criteria
- deployment assumptions
- testing strategy
- observability expectations
- external integrations
- change rules

Do not stop at feature names. Push to implementable detail.

### 4. UI Definition

If project has UI, do both tracks in parallel:
- structural track: IA, pages, flows, states, components
- visual track: 2-3 style directions for user approval

Rules:
- core pages high fidelity
- secondary pages medium fidelity
- edge pages low fidelity
- core pages and core components require full state definition
- UI spec must be implementation-guiding, not decorative only

If project has no meaningful UI, skip this stage.

### 5. Decision Closure

Before roadmap or implementation, close all high-impact unresolved decisions:
- stack
- architecture direction
- UI direction
- data model direction
- permissions model
- testing strategy
- milestone slicing
- acceptance rules

Do not enter implementation with open high-impact decisions.

### 6. Roadmap

Split project into milestones.

Prefer:
- user-value closed loops first
- technical split only when value-loop split is impossible

Each milestone must be independently spec-able, executable, testable, and handoff-able.

### 7. Milestone Spec

Create full spec for the current milestone.

### 8. Milestone Plan

Create detailed implementation and testing plan for the current milestone.

After entering `milestone-plan`, scope freezes by default.

### 9. Execution

Execute the current milestone plan with:
- TDD
- review gates
- verification gates
- controlled progress
- durable state updates

After entering `execution`, scope remains frozen except for blocking or validity-breaking changes.

### 10. Debugging

If blocked by failing behavior, use systematic debugging. Do not guess-fix.

### 11. Verification

Run milestone acceptance, targeted regression, and required cross-checks. Use fresh evidence only.

### 12. Handoff

Update durable state files:
- task state
- session brief
- verification status
- next step
- blockers
- persistent processes

### 13. Done

Mark done only when:
- acceptance criteria satisfied
- verification evidence is fresh
- state files are current
- remaining backlog is explicitly categorized

## Hard Gates

Do not allow implementation when any of these are missing:

- `product-spec.md`
- `decision-log.md` resolved for high-impact items
- `roadmap.md`
- current milestone spec
- current milestone implementation plan
- current milestone test plan

Do not mark work complete when any of these are missing:

- fresh verification evidence
- updated milestone task state
- updated `session-brief.md`

## Required Skill Routing

### Always activate first
- `superpowers:using-superpowers`
- `karpathy-guidelines`

### Planning
Use:
- `superpowers:brainstorming`
- `superpowers:writing-plans`

### Execution
Use:
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:test-driven-development`

### Quality
Use:
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`

### Failure handling
Use:
- `superpowers:systematic-debugging`

### Completion
Use:
- `superpowers:finishing-a-development-branch`

### Skill creation / maintenance
Use:
- `superpowers:writing-skills`
- `skill-creator`

### Optional extensions
Use only when relevant:
- `context7`
- `find-skills`
- `caveman`

## Controlled Skill Extensions

Additional skills may be registered and used, but only through controlled routing.

For each additional skill define:
- skill name
- use conditions
- allowed stages
- always-on or on-demand
- whether user approval is required

Read `docs/orchestrator/skill-registry.md` when present.

## Planning Discipline

Use two decision layers:

### Layer 1: user-confirmed
- project goal
- stack
- UI direction
- high-risk testing priorities
- final acceptance

### Layer 2: orchestrator-recommended
Everything else defaults to orchestrator recommendation unless the user objects.

This prevents planning from stalling on too many tiny decisions.

## Testing Discipline

Testing is risk-prioritized and layered.

Rules:
- every milestone has a written test plan
- prioritize both user-flow closure and high-risk lower-level modules
- use high-value coverage, not mechanical blanket coverage
- add E2E after main flows stabilize
- use smart regression based on impact and risk
- when tests fail, classify cause before fixing

Maintain milestone testing documents, not just test code.

## Change Control

New ideas do not interrupt current execution by default.

Default path:
- record in backlog
- classify into:
  - must handle now
  - next milestone candidate
  - future idea
  - explicitly not doing

Only escalate if change affects:
- project goal
- stack
- milestone acceptance
- core data model
- core permissions/security
- core UI structure
- key external dependency
- validity of current plan

Major changes require a written change request.

## Efficiency Rules

Move fast by reducing low-value loops, not by lowering quality.

Rules:
- front-load decisions, reduce execution churn
- run narrow tests during small development loops
- expand verification at task or milestone boundaries
- do not run full suites by default for every small change
- do not polish before core flow closes
- do not reload whole project context every session
- use `session-brief.md` as recovery entrypoint

## Process Management Rules

Avoid shell/process sprawl.

Rules:
- short commands run foreground only
- minimize long-lived processes
- reuse existing dev services when possible
- do not start duplicate servers/watchers
- record long-lived process purpose, command, and port
- clean up temporary processes before ending session unless they must persist

## Progressive Loading

Do not load every reference or template file at once.

Read in this order:
1. `SKILL.md`
2. determine current stage
3. read only stage-relevant files from `references/`
4. read only needed files from `templates/`
5. on new session, read `docs/orchestrator/session-brief.md` first

## Repository State

Use repository docs as durable state.

Important files include:
- `docs/orchestrator/product-spec.md`
- `docs/orchestrator/feature-breakdown.md`
- `docs/orchestrator/decision-log.md`
- `docs/orchestrator/roadmap.md`
- `docs/orchestrator/session-brief.md`
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/gap-analysis.md`
- milestone-specific spec/plan/test/task-state files

Cross-check with git, but do not rely only on git history for recovery.

## Recovery Protocol

At the end of meaningful work, ensure durable state includes:
- current stage
- current milestone
- current task
- latest verification result
- blockers
- persistent process inventory
- next session first step
- any pending user confirmation

On new session:
1. read `session-brief.md`
2. read active milestone task state
3. read `decision-log.md`
4. read milestone plan/spec as needed
5. cross-check code and git status
6. continue from exact next step

## Output Standard

When guiding execution:
- say what stage project is in
- say why next action is allowed
- say which skill to use next
- say which durable files must be updated

Do not dump all process theory each time. Stay stage-specific and concise.
