# Implementation Plan

## Document Control
- Milestone ID:
- Milestone name:
- Plan owner:
- Version:
- Status:
  - `draft / review / approved / superseded`
- Last updated:
- Related spec:
- Related test plan:
- Related risk matrix:
- Scope freeze status:
  - `open / frozen`

## Milestone Goal
State the exact build target for this plan.

- What this milestone must deliver:
- What counts as milestone closure:
- What this plan intentionally does not cover:

## Execution Strategy
Describe the overall implementation approach.

- Recommended implementation order:
- Why this order is chosen:
- What should be built first to reduce uncertainty:
- What should be deferred until core flow is stable:
- Where existing code or dependencies should be reused first:
- Where new dependencies are acceptable:
- Where custom implementation is justified:

## First-Order Constraints
Record already-confirmed decisions that implementation must not silently change.

- Confirmed project goal:
- Confirmed technology stack:
- Confirmed UI direction:
- Confirmed high-risk testing priorities:
- Confirmed acceptance frame:

## Inputs
List the upstream documents this plan depends on.

- `docs/orchestrator/product-spec.md`
- `docs/orchestrator/feature-breakdown.md`
- `docs/orchestrator/decision-log.md`
- `docs/orchestrator/roadmap.md`
- `docs/orchestrator/milestones/Mx-spec.md`
- `docs/orchestrator/milestones/Mx-test-plan.md`
- Other:
  - `docs/orchestrator/...`

## Scope
### In scope for this plan
- Work item:
- Why it belongs here:
- Acceptance relevance:

### Out of scope for this plan
- Work item:
- Why it is excluded:
- Where it belongs instead:

### Deferred by default
- Work item:
- Trigger for reconsideration:
- Backlog category:

## Implementation Slices
Break work into execution slices that can be completed, tested, and reviewed cleanly.

### Slice 1
- Name:
- Goal:
- Why first:
- Depends on:
- Unblocks:
- Risk level:
  - `critical / high / medium / low`

### Slice 2
- Name:
- Goal:
- Why here:
- Depends on:
- Unblocks:
- Risk level:

## Reuse and Dependency Plan
Apply dependency-first rule explicitly.

### Existing code to reuse
- Area:
- Why reusable:
- Any cautions:

### Existing dependencies to reuse
- Dependency:
- Planned use:
- Why preferred over new implementation:

### New dependency candidates
- Dependency:
- Proposed purpose:
- Why existing code/deps are insufficient:
- Approval needed:
  - `yes/no`

### Custom implementation only if necessary
- Area:
- Why not covered by current code/deps:
- Why custom is justified:

## File and Module Change Plan
Describe expected edit zones.

### Create
- Path:
- Purpose:
- Slice:

### Modify
- Path:
- Purpose of change:
- Slice:

### Avoid touching unless necessary
- Path:
- Why avoid:

## Data and Interface Impact
Describe planned changes that affect data or contracts.

### Data model impact
- Change:
- Why:
- Migration needed:
  - `yes/no`

### API/interface impact
- Change:
- Consumer impact:
- Backward compatibility concern:
  - `yes/no`

### State machine or permissions impact
- Change:
- Why:
- Risk:

## UI Implementation Impact
If milestone includes UI, define implementation implications.

### Core pages touched
- Page:
- Slice:
- Key states required:

### Core components touched
- Component:
- Slice:
- Key states required:

### Responsive/a11y/interaction constraints
- Constraint:
- Why it matters:

## Integration Plan
If milestone touches external integrations, define implementation constraints.

### Integration
- Name:
- Slice:
- Real vs mock/sandbox plan:
- Failure handling requirement:
- Verification need:

## Testing Strategy for This Plan
Reference milestone test plan, then translate it into execution rhythm.

### Unit-focused areas
- Area:
- Why unit-heavy:
- Slice:

### Integration-focused areas
- Area:
- Why integration-heavy:
- Slice:

### E2E candidate flows
- Flow:
- When to add:
- Why:

### Security-focused checks
- Area:
- Why:
- Slice:

### Performance-sensitive checks
- Area:
- Why:
- Validation method:

## Verification Rhythm
Define what to run and when.

### During narrow implementation loops
- Run:
- Purpose:
- Expected speed scope:

### After each completed slice
- Run:
- Purpose:

### Before claiming milestone verification-ready
- Run:
- Purpose:

### Before claiming milestone complete
- Run:
- Purpose:

## Review Gates
Define required review points.

### Spec compliance review
- Trigger:
- What reviewer must check:

### Code quality review
- Trigger:
- What reviewer must check:

### Additional specialized review if needed
- Type:
- Trigger:
- Why:

## Process Management Plan
Prevent process sprawl.

### Long-lived processes allowed
- Process:
- Why needed:
- Port/identifier:
- Reuse if already running:
  - `yes/no`

### Commands that must stay foreground-only
- Command type:
- Why:

### Cleanup expectations
- What must be stopped after slice or session:
- What may remain running across sessions:

## Change Freeze Rules
Define what does and does not justify plan interruption.

### Allowed to interrupt this plan
- Trigger:
- Why valid:

### Not allowed to interrupt this plan
- Trigger:
- Why deferred:

### If interruption happens
- Required document updates:
- Required re-evaluation path:

## Risks and Mitigations
Capture plan-local execution risks.

### Critical execution risks
- Risk:
- Why critical:
- Early mitigation:
- Fallback if mitigation fails:

### High execution risks
- Risk:
- Why high:
- Mitigation:

## Slice-by-Slice Execution Checklist

### Slice 1
- [ ] Confirm upstream spec is still valid
- [ ] Confirm scope still frozen
- [ ] Write failing tests first when this slice includes real functional logic or a bugfix
- [ ] Run failing tests and confirm expected failure when applicable
- [ ] Implement minimum code
- [ ] Run layer-appropriate narrow verification
- [ ] Run relevant integration checks
- [ ] Request review
- [ ] Update task state
- [ ] Update session brief if stopping here

### Slice 2
- [ ] Confirm prior slice remains green
- [ ] Write failing tests first when this slice includes real functional logic or a bugfix
- [ ] Run failing tests and confirm expected failure when applicable
- [ ] Implement minimum code
- [ ] Run layer-appropriate narrow verification
- [ ] Run relevant regression
- [ ] Request review
- [ ] Update task state
- [ ] Update session brief if stopping here

## Completion Gate
This plan is complete only when all are true:

- [ ] All in-scope slices implemented
- [ ] Required tests pass with fresh evidence
- [ ] Required reviews completed
- [ ] Required regressions completed
- [ ] Verification report updated
- [ ] Task state updated
- [ ] Session brief updated
- [ ] Backlog changes recorded
- [ ] Remaining gaps explicitly classified

## Final Notes
- Known accepted gaps:
- Expected follow-up milestone links:
- What future sessions should not re-decide:
