# Cross-Skill Contracts

Use this file when `PlanToDelivery` coordinates `idea-to-design` and `design-to-code`.

Main rule:
- `PlanToDelivery` owns orchestration and gates.
- `idea-to-design` owns product design and visual design artifacts.
- `design-to-code` owns approved design image to code implementation.
- orchestration depends on artifacts and gate evidence, not on a specific skill implementation.
- `idea-to-design` and `design-to-code` are recommended owners, not the only valid sources of equivalent artifacts.

Do not duplicate a downstream skill's workflow inside `PlanToDelivery`. Route to the owning skill, then verify required artifacts.

---

## Ownership

### `PlanToDelivery`

Owns:
- stage machine
- project state
- decision closure
- roadmap and milestone planning
- gate checks
- verification and handoff discipline
- routing to specialized skills

Does not own:
- detailed product design workflow
- visual design iteration workflow
- image-to-code implementation mechanics

### `idea-to-design`

Owns:
- idea clarification
- product design document
- task flows
- page/surface inventory
- design brief
- visual direction
- staged design images
- design recovery state

Preferred outputs or equivalent artifacts for handoff:
- `Design-Spec.md` or equivalent product/design document
- `state.json` or equivalent resumable design state
- approved core flows
- approved core pages
- approved design assets or equivalent persisted visual source
- handoff notes or equivalent recovery notes

### `design-to-code`

Owns:
- converting approved design images or sections into code
- pre-implementation brief
- section-level implementation plan
- framework-specific output rules
- Playwright section screenshot diff
- repair loop after visual mismatch

Required inputs:
- approved persisted design source, such as design image, section image, Figma context, or equivalent visual reference
- page id / section id
- source design path
- confirmed implementation brief
- target framework and route/file location
- known constraints and ambiguities

Required outputs:
- code changes
- section anchors when applicable
- verification evidence
- mismatch notes and repair summary when applicable

---

## Handoff: `idea-to-design` -> `PlanToDelivery`

Before `PlanToDelivery` can move a UI-bearing project toward roadmap or implementation, verify:
- formal design document or equivalent product/design document exists
- core task flows are approved
- core pages are approved or explicitly scoped
- design direction is approved
- approved design assets or equivalent persisted visual source exist for pages that will be implemented visually
- `state.json` or equivalent recovery state is current
- open design questions are either closed or explicitly out of current scope

If any item fails:
- stay in `ui-definition`
- route back to `idea-to-design`
- do not enter `execution`

---

## Handoff: `PlanToDelivery` -> `design-to-code`

Before routing to `design-to-code`, verify:
- target page or section is in current milestone scope
- approved persisted design source path exists
- design source is the visual source of truth
- `Pre-Implementation Brief` exists or will be produced by `design-to-code`
- user confirmation requirement is satisfied before code generation
- implementation target framework is known
- required assets are persisted in repository paths

If any item fails:
- block code generation
- return to `ui-definition` or `milestone-plan`
- do not let implementation reinterpret the design from text alone

---

## Conflict Resolution

If documents disagree:
1. approved user decision wins
2. `PlanToDelivery` stage state wins for process stage
3. `idea-to-design` `Design-Spec.md` wins for product and visual design
4. `design-to-code` brief wins for implementation translation details

Do not silently merge contradictions. Write the conflict into `decision-log.md` or current gate check.

---

## Required Gate Behavior

Before every major transition:
- write a gate check
- list required artifacts
- mark each item `pass`, `fail`, or `n/a`
- choose `allowed` or `blocked`
- name the next owning skill

No stage transition is allowed from implicit confidence alone.
