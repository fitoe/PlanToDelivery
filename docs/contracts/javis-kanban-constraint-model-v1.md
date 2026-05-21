# Javis Kanban Constraint Model v1

## 1. Purpose

PlanToDelivery V2 uses Hermes Kanban as the only executable constraint system. Requirements, design references, asset plans, technical specifications, decisions, waivers, reviews, blockers, verification evidence, and final acceptance are represented as Kanban cards, dependencies, lifecycle states, comments, and result-manifest evidence.

Provider outputs are recommendations until PlanToDelivery ingests a valid `kanban-capability-result/v1` manifest and records the corresponding Hermes Kanban transition. Providers must not directly bypass claim/review/block/complete transitions.

Legacy note: older documents used the term "kanban_constraint" for these checkpoints. In V2 that term is semantic only; it is not a separate state machine or authority.

## 2. Canonical lifecycle

```text
todo / ready -> running -> review -> done
running -> blocked
running -> failed / partial -> review or follow-up
blocked -> ready/cancelled after evidence repair
```

Rules:

- `done` unlocks downstream cards only when dependencies are satisfied.
- `review` holds downstream work until explicit review/approval evidence is recorded.
- `blocked` is only for missing input, external dependency, contradictory requirement, unsafe/destructive action, auth/permission, secret issue, or impossible prerequisite.
- skipped verification is `waived`/`skipped` evidence, never silently treated as passed.

## 3. Project-level Kanban constraints

Project-level cards/dependencies should cover:

```text
project_intake_created
brainstorming_completed
requirements_draft_approved
delivery_blueprint_approved
decision_list_cleared
execution_plan_approved
final_delivery_approved
```

They are not an independent project state system. They exist as Hermes Kanban cards/dependencies/evidence.

### 3.1 Brainstorming completed

Required artifacts/evidence:

- brainstorm summary
- requirements draft
- project goal
- user/scenario summary
- success criteria
- scope boundary
- page/feature candidates
- risks and unknowns
- candidate decisions

MUST NOT proceed directly from brainstorming to code.

### 3.2 Delivery blueprint approved

Required artifact:

- delivery blueprint

The blueprint MUST include product goals, scope, tech stack rationale, page/route inventory, visual direction, technical implementation outline, components/state/API/data draft, decisions, risks, acceptance criteria, and Kanban execution plan.

### 3.3 Decision list cleared

All blocking decisions MUST have selected outcomes, explicit rejection/deferment, or waiver evidence.

### 3.4 Execution plan approved

Required:

- complete initial Slice list
- required Kanban dependencies per Slice
- acceptance criteria per Slice
- dependency graph
- provider routing plan
- resource lock plan
- verification plan

## 4. Slice-level Kanban constraints

Slice-level cards/dependencies should cover:

```text
slice_requirements_approved
design_reference_approved
asset_plan_approved
tech_spec_approved
implementation_ready
implementation_done
verification_passed
slice_delivery_approved
```

### 4.1 Slice requirements approved

Required facts:

- Slice objective
- page/feature responsibility
- route or entry
- user scenario
- key states
- dependencies
- acceptance criteria draft

### 4.2 Design reference approved

Required:

- approved Page Design Crop for every primary page/state
- approved Page Design Crop for key layout-changing states
- source Design Board linkage and crop metadata

MUST NOT implement a page from text-only design unless an explicit waiver exists as Kanban evidence.

### 4.3 Asset plan approved

Required when page needs real images/backgrounds/icons/illustrations/product media:

- asset requirements
- asset board or explicit not-required decision
- asset crops with dimensions, hash, source board, usage, and output path

MUST NOT treat a high-fidelity page design board as the implementation asset source.

### 4.4 Tech spec approved

Required:

- page tech spec
- component tech specs for critical components
- approved design refs
- approved asset refs
- route/entry
- data source/state/interaction definitions
- acceptance criteria

### 4.5 Implementation ready

All must be true:

```text
slice_requirements_approved
design_reference_approved
asset_plan_approved or not_required/waived
tech_spec_approved
decisions_cleared
acceptance_criteria_defined
resource_locks_available
provider_available
TaskExecutionContext can be generated
```

### 4.6 Implementation done

Required evidence:

- result manifest
- changed files
- produced artifacts
- dev route or local verification evidence
- smoke result
- console error check where applicable
- debts/blockers recorded
- resource locks released

### 4.7 Verification passed

Required by verification level:

- route/functionality smoke
- screenshot or local-dev confirmation
- visual deviation report
- critical issues resolved
- user review or approval path if needed

### 4.8 Slice delivery approved

Required:

- verification passed
- no unresolved blocking debt
- waivers recorded
- artifact index complete

## 5. User-visible status projection

User statuses:

```text
clarification_required      待澄清
blueprint_required          待蓝图
design_required             待设计
asset_planning_required     待素材规划
tech_spec_required          待技术说明
decision_required           待决策
implementation_ready        待实现
implementing                实现中
verification_required       待验证
review_required             待审查
blocked                     已阻塞
completed                   已完成
```

Priority order when multiple conditions apply:

```text
已阻塞
待决策
待审查
实现中
待验证
待技术说明
待素材规划
待设计
待蓝图
待澄清
待实现
已完成
```

## 6. Review vs blocked

`review_required` MUST route to `review`, not `blocked`.

`blocked` is reserved for missing input, external dependency, contradictory requirement, unsafe/destructive action, auth/permission, secret issue, or impossible prerequisite.

## 7. Waiver rules

Waivers MUST record:

- affected Kanban card/dependency id
- reason
- risk
- approver
- approval time
- compensation requirement if any

A waiver does not delete the card/dependency. It records explicit risk acceptance and may unlock downstream work only through Hermes Kanban state/evidence.

## 8. Change control

New requirements during execution MUST enter ChangeRequest analysis before being inserted into active implementation. Major changes may return affected slices to blueprint, design, asset, or tech spec Kanban cards.
