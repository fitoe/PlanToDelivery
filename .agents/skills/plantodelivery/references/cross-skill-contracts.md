# Cross-Skill Contracts

Use this file when `PlanToDelivery` coordinates `idea-to-design`, `IdeaToTech`, and `design-to-code`.

Main rule:
- `PlanToDelivery` owns orchestration, Hermes Kanban constraints, milestone state, and completion claims.
- `idea-to-design` owns product design, visual design, and implementation-ready design handoff artifacts.
- `IdeaToTech` owns functional/technical implementation blueprints, dependency decisions, feature recipes, API/state/mock plans, and verification matrix.
- `design-to-code` owns blueprint-driven UI implementation and targeted fidelity verification.
- orchestration depends on artifacts and Kanban evidence, not on a specific skill implementation.
- `idea-to-design`, `IdeaToTech`, and `design-to-code` are recommended owners, not the only valid sources of equivalent artifacts.

Do not duplicate a downstream skill's workflow inside `PlanToDelivery`. Route to the owning skill, then verify required artifacts.

---

## Ownership

### `PlanToDelivery`

Owns:
- stage machine
- project state
- decision closure
- roadmap and milestone planning
- Kanban evidence checks
- verification and handoff discipline
- routing to specialized skills
- mapping design/code states into milestone completion layers

Does not own:
- detailed product design workflow
- visual design iteration workflow
- implementation blueprint generation
- design-to-code implementation mechanics

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
- Level 3 implementation-ready handoff package

Preferred outputs or equivalent artifacts for Level 3 handoff:
- `Design-Spec.md` or equivalent product/design document
- `state.json` or equivalent resumable design state
- approved core flows
- approved core pages
- approved design assets or equivalent persisted visual source
- `DESIGN.md`
- `tokens.json`
- `visual-source-contract.json`
- recorded Visual Freeze approval and Post-Visual Extraction status in `state.json`
- `visual-proposals.json` for image-generated product-like elements
- `visual-contracts/<page-id>.json`
- `implementation-blueprint.json`
- `page-matrix.json`
- `component-blueprint.json`
- `debt-ledger.json`
- `page-style-briefs/<page-id>.md`
- `design-to-code-inputs/manifest.json`
- `pre-implementation-briefs/<page-id>.md`
- `implementation-parity-checklist.md`
- passing `scripts/check-design-handoff.py` result when present

### `design-to-code`

Owns:
- consuming approved implementation blueprints or equivalent design-to-code inputs
- global foundation implementation: tokens, shell, layout, base components
- full page/route visible coverage
- staged refinement and component extraction
- targeted fidelity checks for core pages, first screens, and key components
- layered handoff reporting with page maturity, foundation status, verification, and debt

Preferred inputs:
- `implementation-blueprint.json` as the first read when it exists
- `page-matrix.json`
- `component-blueprint.json`
- `debt-ledger.json`
- target repo/framework and route/file conventions
- detailed page briefs, visual contracts, source images, and crops only when the current pass needs them

Fallback inputs when no blueprint exists:
- approved persisted design source, such as design image, section image, Figma context, or equivalent visual reference
- page id / section id
- source design path
- confirmed implementation brief when required
- known constraints and ambiguities

Required outputs:
- code changes
- page maturity summary (`L0 route-ready` through `L5 functional-ready`)
- foundation/system status
- section anchors when applicable
- coverage/system/fidelity verification evidence sized to the current pass
- mismatch, debt, accepted deviation, and repair notes when applicable

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

For formal UI implementation, also verify the Level 3 blueprint package:
- `implementation-blueprint.json` exists and is the post-visual low-context downstream entrypoint
- `implementation-blueprint.json.visual_freeze_ref.status` is `approved` and `post_visual_extraction_status` is `complete`
- `page-matrix.json` lists planned routes/pages and maturity targets
- `component-blueprint.json` lists foundation/repeated/page-local/deferred component tiers
- `debt-ledger.json` exists, even if empty
- `design-to-code-inputs/manifest.json` and required visual contracts/briefs exist for binding visual pages
- checker result passes when `scripts/check-design-handoff.py` is available

If any required item fails:
- stay in `ui-definition` or `decision-closure`
- route back to `idea-to-design`
- do not enter `execution`

---

## 3. IdeaToTech -> PlanToDelivery

`IdeaToTech` owns implementation-ready technical planning. `PlanToDelivery` validates that technical decisions are explicit enough to enter execution.

Required default package:
- `technical-decisions.json`
- `feature-recipes.json`
- `verification-matrix.json`

Optional expanded package:
- `api-contracts.json`
- `state-management-plan.json`
- `mock-to-real-plan.json`
- `integration-plan.json`
- `technical-spikes/<decision-id>.md`

Gate checks:
- `technical_gate.status` is `open`
- dependency decisions are `lock_now`, explicitly `defer_to_implementation`, or out of current scope
- `spike_first` decisions have spike results or are not in current milestone
- `blocked` decisions are resolved or user-waived
- feature recipes define service/store/composable/component boundaries for current scope
- verification matrix distinguishes mock acceptance from real acceptance
- no secrets, tokens, passwords, or private connection strings are persisted

## 4. PlanToDelivery -> design-to-code

Before routing to `design-to-code`, prefer the blueprint path:
- target pages/routes are in current milestone scope
- `implementation-blueprint.json` exists or an equivalent post-visual blueprint is recorded
- blueprint includes approved visual freeze metadata and complete Post-Visual Extraction status
- `page-matrix.json`, `component-blueprint.json`, and `debt-ledger.json` exist or equivalent artifacts are recorded
- target framework and repo conventions are known
- implementation gate is open or a user waiver is recorded

When the blueprint path is valid:
- route to `design-to-code` for Blueprint Intake -> Foundation -> Coverage -> Refinement -> Fidelity
- do not require `design-to-code` to re-analyze all design images or rewrite all briefs
- do not require section slicing as a blocker for broad route/page coverage
- load detailed page briefs, visual contracts, crops, and source images only for the current pass or a blocker

Fallback path when no blueprint exists:
- approved persisted design source path exists
- design source is the visual source of truth
- `Pre-Implementation Brief` exists or will be produced by `design-to-code`
- user confirmation requirement is satisfied before code generation
- implementation target framework is known
- required assets are persisted in repository paths

If any required item fails:
- block code generation
- return to `ui-definition` or `milestone-plan`
- do not let implementation reinterpret the design from text alone

---

## Completion Mapping

Map `design-to-code` page maturity into `PlanToDelivery` delivery layers:

- `L0 route-ready` + `L1 skeleton-ready` contribute to Visual Shell.
- `L2 content-ready` + `L3 system-styled` can satisfy broad Visual Complete for non-core pages when mock/fallbacks are honest.
- `L4 core-fidelity` is expected for core pages, first screens, or explicitly high-fidelity surfaces before claiming visual acceptance.
- `L5 functional-ready` contributes to Functional Complete only when real interactions/API/state are in milestone scope.

Never report broad coverage as final high-fidelity or functional completion. Report maturity and debt explicitly.

---

## Conflict Resolution

If documents disagree:
1. approved user decision wins
2. `PlanToDelivery` stage state wins for process stage
3. `idea-to-design` `Design-Spec.md` and Level 3 blueprint package win for product, visual, and implementation intent
4. `design-to-code` implementation report wins for actual code state, maturity, and debt

Do not silently merge contradictions. Write the conflict into `decision-log.md` or current Kanban evidence record.

---

## Required Gate Behavior

Before every major transition:
- write a gate check
- list required artifacts
- mark each item `pass`, `fail`, or `n/a`
- choose `allowed` or `blocked`
- name the next owning skill

No stage transition is allowed from implicit confidence alone.
