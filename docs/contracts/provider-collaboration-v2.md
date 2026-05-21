# Provider Collaboration v2

This document is the PlanToDelivery-side map for the V2 provider ecosystem. It keeps provider routing capability-first and prevents Javis from hard-coding specialist internals.

## Roles

| Role | Owner | Owns | Does not own |
|---|---|---|---|
| Orchestrator | PlanToDelivery / Javis | canonical state, provider registry, task envelopes, result ingestion, Kanban review/block/complete constraints, progress, checkpoint handoff | provider implementation details, visual design authority, technical architecture internals, coding details |
| Design provider | IdeaToDesign | `product_visual_design`, `visual_source_creation`, design artifacts, visual source contracts, Visual IR / Level-3 handoff | canonical Kanban lifecycle, coding, technical architecture |
| Technical provider | IdeaToTech | `technical_blueprint`, `implementation_planning`, `verification_strategy`, decisions/recipes/matrices | canonical Kanban lifecycle, visual direction, final code changes |
| Visual implementation provider | DesignToCode | `visual_implementation`, code from approved sources, screenshots, parity reports, implementation debts | design decisions, architecture decisions, canonical Kanban lifecycle |

## Canonical capability flow

```text
product_visual_design
  -> visual_source_creation
  -> technical_blueprint / implementation_planning / verification_strategy
  -> visual_implementation
  -> review / approval / downstream unlock in PlanToDelivery
```

The flow is not always strictly linear. PlanToDelivery may skip a capability only when the required artifact already exists and is approved/still-current. If a provider returns `partial`, PlanToDelivery routes only the missing capability rather than restarting the whole workflow.

## Dispatch contract

### Existing Hermes Kanban bridge

PlanToDelivery must not require custom Hermes Kanban columns or project-local DB fields. For existing Hermes Kanban tasks, P2D-specific routing metadata is carried as an opaque marker in the task body or in a task comment:

```md
<!-- P2D_META <base64url-json> P2D_META -->
```

Decoded payload schema:

```json
{
  "schema": "p2d-meta/v1",
  "task_id": "task-001",
  "capability": "technical_blueprint",
  "active_slice": {"page": "/mall"},
  "provider": "idea-to-tech",
  "output_root": "project-state/kanban/tasks/task-001",
  "input_artifact_refs": [],
  "expected_outputs": ["result-manifest.json"],
  "verification_expectations": [],
  "allowed_side_effects": ["write output_root only"],
  "depends_on": []
}
```

Rules:

- `schema`, `task_id`, `capability`, and non-empty `active_slice` are required.
- Body marker and comment marker are both valid. This supports migration from cards whose body is already user-facing prose.
- If both body and comments contain markers, they must decode to the same object; conflicting markers are invalid and must be resolved before dispatch.
- The marker is a semantic adapter only. Hermes Kanban remains canonical for claim/complete/block/review lifecycle; P2D marker payloads only compile a card into a `kanban-capability-task/v1` envelope.
- Prefer comment markers when retrofitting existing tasks to avoid rewriting user-visible task bodies.
- Use `append_p2d_meta_marker`, `extract_p2d_meta_marker`, `validate_p2d_meta`, and `p2d_meta_to_task_envelope` from `plantodelivery.kanban_runtime` for deterministic migration/validation.

1. Select by requested capability from `provider-registry/v1`.
2. Load the selected provider's `provider-manifest/v1` snapshot or compact manifest.
3. Create a `kanban-capability-task/v1` envelope with active-slice artifacts, expected outputs, allowed side effects, review policy, and blocking policy.
4. Dispatch exactly one bounded provider task unless Kanban review/conflict resolution explicitly calls for comparison.
5. Require a `kanban-capability-result/v1` manifest before updating canonical state.
6. Ingest produced artifacts, evidence, blockers, debts, `suggested_kanban_updates`, and `next_recommended_task`.
7. Decide canonical Kanban lifecycle state from evidence and policy, not from provider prose alone.

## Review and blocker semantics

- `review_required: true` maps to `review`; it is not a generic blocker.
- `blocked` is reserved for missing/contradictory inputs, inaccessible systems, auth/permission/secrets, unsafe/destructive side effects, or unavailable required tools/dependencies.
- `partial` preserves usable artifacts and routes only the missing follow-up capability.
- Skipped or waived verification remains `skipped` / `waived`; it is never converted to `passed`.
- Providers may recommend outcomes and evidence, but only PlanToDelivery moves canonical Hermes Kanban lifecycle and progress forward.

## Registry alignment

Current default providers:

| Capability | Provider | Manifest |
|---|---|---|
| `product_visual_design` | `idea-to-design` | `IdeaToDesign/contracts/provider-manifest.json` |
| `visual_source_creation` | `idea-to-design` | `IdeaToDesign/contracts/provider-manifest.json` |
| `technical_blueprint` | `idea-to-tech` | `IdeaToTech/contracts/provider-manifest.json` |
| `implementation_planning` | `idea-to-tech` | `IdeaToTech/contracts/provider-manifest.json` |
| `verification_strategy` | `idea-to-tech` | `IdeaToTech/contracts/provider-manifest.json` |
| `visual_implementation` | `design-to-code` | `DesignToCode/contracts/provider-manifest.json` |

Provider repo docs that must stay aligned:

- IdeaToDesign: `docs/provider-collaboration-v2.md`
- IdeaToTech: `docs/provider-collaboration-v2.md`
- DesignToCode: `docs/provider-collaboration-v2.md`

## Anti-coupling checklist

Before merging orchestration changes, verify:

- no provider-specific execution branch is required for normal dispatch;
- capability matching comes from registry/manifest, not hard-coded provider names;
- task envelopes pass artifact paths instead of full chat history;
- result manifests are validated before state updates;
- review/block/partial/completed transitions preserve evidence paths;
- downstream dependency unlock happens from canonical state, not provider self-claims.
