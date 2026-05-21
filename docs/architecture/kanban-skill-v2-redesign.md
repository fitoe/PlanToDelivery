# Kanban Skill V2 Redesign

**Date:** 2026-05-20

**Status:** Accepted direction for the `kanban` branch.

**Canonical project:** `/mnt/c/Users/imjzq/Projects/PlanToDelivery`

## Goal

Redesign PlanToDelivery as the Javis/Kanban orchestrator kernel and treat specialist skills as capability providers. This intentionally stops optimizing around historical skill baggage. The runtime surface should become contract-first, short, dispatchable, and easy for an agent to execute.

## Non-goals

- Do not continue the separate `JavisKanban` project as the canonical line.
- Do not merge DesignToCode, IdeaToDesign, or IdeaToTech into PlanToDelivery.
- Do not make PlanToDelivery depend on provider internals, file structures, or long prompt memories.
- Do not preserve every historical workflow in the main `SKILL.md`.

## Architecture

```text
Javis / PlanToDelivery
  = orchestrator kernel
  = Hermes Kanban constraints + registry + dispatch + review/block/complete + progress rollup

IdeaToDesign
  = design provider
  = product_visual_design + visual_source_creation

IdeaToTech
  = technical provider
  = technical_blueprint + implementation_planning + verification_strategy

DesignToCode
  = implementation provider
  = visual_implementation
```

The orchestrator talks to providers only through contract files and manifests:

- `provider-manifest/v1`
- `provider-registry/v1`
- `kanban-capability-task/v1`
- `kanban-capability-result/v1`

## Role boundaries

### PlanToDelivery / Javis Orchestrator

Owns:

- project state recovery
- current slice selection
- capability matching
- task envelope creation
- provider dispatch instructions
- result manifest ingestion
- Kanban review/block/complete decisions
- progress reporting
- checkpoint and handoff summaries

Does not own:

- visual design internals
- technical architecture internals
- implementation details
- provider-specific playbooks
- provider-side lifecycle closure or Kanban bypass

### Provider skills

Providers own one bounded capability invocation. They consume a task envelope and return a result manifest.

Providers may recommend outcomes and evidence, but they must not move work forward outside Hermes Kanban claim/review/block/complete transitions.

## Runtime skill shape

Each main `SKILL.md` should become a small kernel rather than a historical handbook.

Target sections:

1. Role
2. When to activate
3. Inputs
4. Outputs
5. Contract rules
6. Kanban constraint semantics
7. Failure semantics
8. Review semantics
9. Progressive references
10. Pitfalls

Historical material moves under `references/legacy/`, `references/playbooks/`, or focused reference files and is loaded only when a trigger applies.

## Capability registry model

The registry maps capability names to provider skills. The orchestrator must match by capability, not by provider identity.

Canonical capabilities:

- `product_visual_design`
- `visual_source_creation`
- `technical_blueprint`
- `implementation_planning`
- `verification_strategy`
- `visual_implementation`

Provider selection should be replaceable. A future provider can implement the same capability without changing orchestrator logic.

## Task envelope requirements

A `kanban-capability-task/v1` task must include:

- `task_id`
- `capability`
- `project_root`
- `active_slice`
- `input_artifact_refs`
- `output_root`
- `expected_outputs`
- `verification_expectations`
- `allowed_side_effects`
- `review_policy`
- `blocking_policy`

The task describes the need, not the provider implementation.

## Result manifest requirements

A `kanban-capability-result/v1` result must include:

- `task_id`
- `capability`
- `provider`
- `result`: `completed | partial | blocked | failed`
- `changed_files`
- `produced_artifacts`
- `evidence`
- `blockers`
- `debts`
- `review_required`
- `suggested_kanban_updates`
- `next_recommended_task`

Long reasoning, screenshots, diffs, visual analysis, spike notes, and detailed repair notes should live in files referenced by the manifest.

## Kanban constraint semantics

- `review_required` / `review-required` routes to `review`.
- `blocked` is reserved for missing input, external dependency, contradictory requirements, unsafe/destructive action, permission/auth issues, or secrets.
- `partial` should preserve usable artifacts and route only the missing capability.
- Review completion is the point where downstream children may be unlocked.
- Providers recommend; the orchestrator records canonical Hermes Kanban lifecycle state and evidence overlays.

## V2 migration plan

### Phase 1 — Orchestrator kernel

Rewrite PlanToDelivery `SKILL.md` as the Javis orchestrator kernel. Move historical workflow material behind progressive references.

### Phase 2 — Provider kernels

Rewrite IdeaToDesign, IdeaToTech, and DesignToCode main `SKILL.md` files into provider kernels. Keep specialist depth in references.

### Phase 3 — Contract templates

Add or normalize templates:

- `templates/kanban-capability-task.template.json`
- `templates/kanban-capability-result.template.json`
- `templates/provider-registry.template.json`
- `templates/kanban-decision.template.json`

### Phase 4 — End-to-end dry run

Run a sample flow:

1. Javis creates a `product_visual_design` task.
2. IdeaToDesign returns a result manifest.
3. Javis ingests it and routes review or next capability.
4. Javis creates `technical_blueprint` / `implementation_planning` tasks.
5. IdeaToTech returns result manifests.
6. Javis creates a `visual_implementation` task.
7. DesignToCode returns changed files and evidence.
8. Javis records the Kanban lifecycle decision and progress rollup.

## Acceptance criteria

- `skill_view('PlanToDelivery')` shows a concise Javis orchestrator kernel.
- The runtime skill still clearly exposes `Kanban Orchestrator Mode` semantics.
- The source skill and Hermes runtime skill are synchronized.
- Old large workflow content is reachable through references, not duplicated in the main kernel.
- The work is committed on the `kanban` branch of PlanToDelivery.
