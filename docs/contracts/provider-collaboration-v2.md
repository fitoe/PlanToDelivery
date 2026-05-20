# Provider Collaboration v2

This document is the PlanToDelivery-side map for the V2 provider ecosystem. It keeps provider routing capability-first and prevents Javis from hard-coding specialist internals.

## Roles

| Role | Owner | Owns | Does not own |
|---|---|---|---|
| Orchestrator | PlanToDelivery / Javis | canonical state, provider registry, task envelopes, result ingestion, gates, progress, checkpoint handoff | provider implementation details, visual design authority, technical architecture internals, coding details |
| Design provider | IdeaToDesign | `product_visual_design`, `visual_source_creation`, design artifacts, visual source contracts, Visual IR / Level-3 handoff | canonical gates, coding, technical architecture |
| Technical provider | IdeaToTech | `technical_blueprint`, `implementation_planning`, `verification_strategy`, decisions/recipes/matrices | canonical gates, visual direction, final code changes |
| Visual implementation provider | DesignToCode | `visual_implementation`, code from approved sources, screenshots, parity reports, implementation debts | design decisions, architecture decisions, canonical gates |

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

1. Select by requested capability from `provider-registry/v1`.
2. Load the selected provider's `provider-manifest/v1` snapshot or compact manifest.
3. Create a `kanban-capability-task/v1` envelope with active-slice artifacts, expected outputs, allowed side effects, review policy, and blocking policy.
4. Dispatch exactly one bounded provider task unless a gate explicitly calls for conflict resolution.
5. Require a `kanban-capability-result/v1` manifest before updating canonical state.
6. Ingest produced artifacts, evidence, blockers, debts, `suggested_gate_updates`, and `next_recommended_task`.
7. Decide canonical gate state from evidence and policy, not from provider prose alone.

## Review and blocker semantics

- `review_required: true` maps to `review`; it is not a generic blocker.
- `blocked` is reserved for missing/contradictory inputs, inaccessible systems, auth/permission/secrets, unsafe/destructive side effects, or unavailable required tools/dependencies.
- `partial` preserves usable artifacts and routes only the missing follow-up capability.
- Skipped or waived verification remains `skipped` / `waived`; it is never converted to `passed`.
- Providers may recommend gate changes, but only PlanToDelivery records canonical gates and progress.

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
