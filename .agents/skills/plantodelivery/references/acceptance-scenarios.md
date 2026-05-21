# Acceptance Scenarios

Use these scenarios after changing cross-skill coordination rules.

## Scenario 1: `idea-to-design` standalone

Input:
- rough product idea

Expected:
- can proceed without `PlanToDelivery`
- produces or plans `Design-Spec.md`, assets, and state
- no implementation work starts

## Scenario 2: `design-to-code` standalone

Input:
- approved persisted design source
- known target framework

Expected:
- can proceed without `PlanToDelivery`
- emits or requests `Pre-Implementation Brief`
- blocks code until brief confirmation when required

## Scenario 3: `PlanToDelivery` orchestrated flow

Input:
- project has UI
- no approved design artifact exists

Expected:
- Kanban state is `blocked`
- next owner is `idea-to-design`
- no code implementation starts

## Scenario 4: External design source

Input:
- Figma or manual design package
- manifest and approval record exist

Expected:
- `PlanToDelivery` accepts equivalent artifacts
- can route to `design-to-code` after input gate passes

## Scenario 5: Missing approval

Input:
- design image exists
- no approval record exists

Expected:
- Kanban state is `blocked`
- next action requests explicit approval

## Scenario 6: Implementation feedback loop

Input:
- `design-to-code` reports design ambiguity or missing asset

Expected:
- issue is classified
- work routes back to design/spec clarification instead of guessing
