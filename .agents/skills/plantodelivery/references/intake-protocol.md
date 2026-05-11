# Intake Protocol

Use this file when the project is not clearly greenfield.

This protocol handles:
- partially planned projects
- partially implemented projects
- interrupted sessions
- inherited repositories
- repositories with existing `superpowers:brainstorming` outputs
- projects whose code and docs may not match

## Goal

Build a reliable understanding of the current project state without overreacting.

The intake phase should answer:

- What already exists?
- What is already trustworthy?
- What is missing?
- What is stale?
- What can be reused directly?
- What must be repaired before continuing?

## Intake Mindset

Do not restart by reflex.

Prefer this order:
1. adopt
2. patch
3. extend
4. re-plan only when necessary

## Primary Outputs

Intake must produce or update:

- `docs/orchestrator/current-state.md`
- `docs/orchestrator/gap-analysis.md`
- `docs/orchestrator/session-brief.md`

It may also update:
- `docs/orchestrator/decision-log.md`
- `docs/orchestrator/roadmap.md`
- active milestone docs if they exist but are stale

## Intake Order of Operations

Perform intake in this order.

### Step 1: Check for orchestrator state

Look for:
- `docs/orchestrator/session-brief.md`
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/gap-analysis.md`
- `docs/orchestrator/decision-log.md`
- `docs/orchestrator/roadmap.md`
- `docs/orchestrator/milestones/`

If these exist, they are the preferred entrypoint.

### Step 2: Check for prior planning docs outside orchestrator format

Look for:
- `docs/`
- `specs/`
- brainstorm or planning markdown files
- architecture docs
- ADRs
- milestone docs
- README sections that define scope

If existing planning appears useful, adopt it rather than duplicate it.

### Step 3: Inspect code reality

Inspect:
- top-level project structure
- runtime/framework indicators
- test directories
- config/deploy files
- critical modules
- recent implementation shape

Determine:
- current stack
- likely implemented features
- likely incomplete areas
- whether project structure matches documented intent

### Step 4: Inspect verification reality

Check:
- test presence
- build scripts
- deploy scripts
- verification docs
- prior verification reports if any

Determine:
- whether current code has trustworthy validation
- whether docs claim more certainty than the repo supports

### Step 5: Inspect git state when available

Use git only as cross-check, not sole truth.

Check:
- is repo clean or dirty
- are there recent milestones/commits
- do commit messages suggest unfinished work
- is branch state likely to matter

### Step 6: Write current-state

Summarize actual repo condition.

### Step 7: Write gap-analysis

Compare:
- current repo reality
- desired target or planned target

### Step 8: Choose continuation path

Classify continuation as one of:

#### Path 1: Continue directly
Use when:
- docs are coherent
- code aligns enough
- next step is clear

#### Path 2: Patch planning first
Use when:
- project is recoverable
- but docs miss key gates
- or milestone framing is weak

#### Path 3: Material re-plan
Use when:
- target state is unclear
- existing planning is contradictory
- code has drifted far from stated goal
- acceptance target is no longer stable

## What to Capture in `current-state.md`

`current-state.md` should describe what exists now, not what was intended.

Capture:
- current project type
- current stack actually present
- main implemented capabilities
- known incomplete areas
- current UI state if any
- current API/service state if any
- current data/storage state if any
- test state
- deploy/environment state
- observability/security state if visible
- notable repo risks
- confidence level for each major area if needed

## What to Capture in `gap-analysis.md`

`gap-analysis.md` compares current reality to target reality.

Capture:
- goal or milestone target
- what's already complete
- what's partial
- what's missing
- what's contradictory
- what needs re-planning
- what can proceed without change
- recommended next stage

## Trust Levels

During intake, classify artifacts by trust level.

### High trust
Use directly when:
- recent
- coherent
- specific
- aligned with code/tests

### Medium trust
Use after patching when:
- useful but incomplete
- slightly stale
- lacks verification detail
- code alignment uncertain

### Low trust
Do not rely on directly when:
- contradictory
- vague
- obviously outdated
- disproven by code

## Intake and Existing `superpowers:brainstorming` Docs

If brainstorming docs already exist:

- do not discard them
- inspect for:
  - scope clarity
  - decision completeness
  - milestone relevance
  - code alignment
- convert or map them into orchestrator durable outputs as needed

Patch missing gaps rather than cloning content blindly.

## Session Brief Requirements After Intake

At intake completion, `session-brief.md` should clearly state:
- current classified stage
- why that stage is correct
- what docs are trusted
- what docs need patching
- exact next action
- whether user confirmation is needed soon

## Exit Conditions

Intake is complete only when:
- current repo reality is described
- target gap is described
- continuation path is selected
- next stage is explicit

Do not leave intake with only a vague impression.
