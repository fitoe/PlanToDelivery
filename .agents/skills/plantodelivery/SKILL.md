---
name: PlanToDelivery
description: Javis/Kanban orchestrator kernel. Use when coordinating project delivery through state recovery, capability registry matching, provider task envelopes, result manifest ingestion, review gates, progress reporting, and checkpoint handoff.
---

# PlanToDelivery — Javis Orchestrator Kernel

## Role

PlanToDelivery is the canonical **Javis** project orchestrator. It owns project state, capability routing, provider dispatch, result ingestion, review/block/gate decisions, progress rollup, and final handoff.

It does **not** own specialist implementation details. Design, technical planning, and implementation are provided by capability providers through explicit contracts.

Canonical project root for Javis work:

```text
/mnt/c/Users/imjzq/Projects/PlanToDelivery
```

The previous `JavisKanban` project is not canonical.

## When to activate

Use this skill when:

- the user says `贾维斯`, `贾维斯继续`, `Javis`, `kanban`, or asks to continue a project through orchestration;
- a workflow references `kanban-capability-task/v1`, `provider-manifest/v1`, `provider-registry/v1`, review gates, or provider result manifests;
- multiple specialist capabilities must be sequenced, reviewed, or checkpointed;
- project state must be recovered and the next capability selected.

## Core loop

1. **Recover state** — read durable project state first: `.hermes/project-state/*`, `project-state/*`, or legacy `docs/orchestrator/*` only as fallback.
2. **Select active slice** — identify the smallest project/page/feature slice that can move next.
3. **Choose capability** — match the next need to a capability, not to a hard-coded provider.
4. **Create task envelope** — produce one bounded `kanban-capability-task/v1` per provider invocation.
5. **Dispatch provider** — call or instruct the provider using artifact paths, expected outputs, allowed side effects, and review policy.
6. **Ingest manifest** — require a `kanban-capability-result/v1`-shaped result before updating canonical state.
7. **Decide gate** — record review, blocked, partial, or completed status from evidence, not prose confidence.
8. **Roll up progress** — update state, artifact index, blockers/debts, and user-facing checkpoint.
9. **Continue or hand off** — route the next capability unless a hard blocker, destructive action, secret/auth issue, or user approval gate requires stopping.

## Capability registry

Match by capability. Provider identity must be replaceable.

| Capability | Default provider | Purpose |
|---|---|---|
| `product_visual_design` | `idea-to-design` | product/design spec, flows, page inventory, visual direction |
| `visual_source_creation` | `idea-to-design` | persisted visual source, design freeze evidence, handoff inputs |
| `technical_blueprint` | `IdeaToTech` | architecture seams, API/state/mock/dependency decisions |
| `implementation_planning` | `IdeaToTech` | implementation sequence, feature recipes, file map |
| `verification_strategy` | `IdeaToTech` | mock/local/real/edge verification matrix |
| `visual_implementation` | `design-to-code` | code changes from approved visual handoff, screenshots, parity evidence |

Do not import provider internals. Do not assume provider file layouts beyond the registry/manifest contract.

### Runtime helpers

The canonical in-repo runtime entry is `plantodelivery.kanban_runtime`.

Use it for deterministic contract work before/after provider dispatch:

- `write_provider_registry_config(path, providers={...})` writes `provider-registry/v1` with explicit real provider manifest paths such as IdeaToDesign, IdeaToTech, and DesignToCode.
- `load_provider_registry_config(path)` validates that registry config before dispatch.
- `load_provider_registry(root_or_config)` scans `provider-manifest.json` files from either a directory or a `provider-registry/v1` config file and returns a capability-indexed registry.
- `create_task_envelope(...)` builds capability-first `kanban-capability-task/v1` payloads without embedding provider identity.
- `validate_result_manifest(...)` checks `kanban-capability-result/v1` provider outputs before state updates.
- `decide_gate_status(manifest)` maps provider results into Javis gate states; `review_required` becomes `review`, while real blockers remain `blocked`.
- `KanbanStateStore(root)` is the canonical Kanban state source under `project-state/kanban`: it writes task envelopes and result manifests as artifact/evidence files, but `kanban-state.json` owns canonical `tasks`, `gates`, user-visible `cards`, and append-only `events`.
- Do not add board adapters for compatibility. If the state model changes, evolve `KanbanStateStore` and its contract tests directly.
- `display_gate_status(gate_status)` returns the Chinese label for board/UI/progress display while preserving English contract enums for schemas and provider manifests.
- `KanbanOrchestrator(project_root=..., providers_root=...)` is the minimal end-to-end orchestration facade: `dispatch_task(...)` selects a provider by capability and records canonical Kanban state; `ingest_result(...)` or `ingest_result_path(...)` validates and persists provider result artifacts then updates canonical gate/card/event state; `approve_review(task_id, evidence=[...])` advances a reviewed task from `review` to `completed` in canonical state.
- `write_fixture_provider_result(task_envelope_path=..., provider=...)` is a deterministic fake-provider helper for contract tests and local dry-runs; do not treat it as a real provider implementation.

These helpers are deliberately small and provider-agnostic. Extend them by contract tests first; do not reintroduce legacy orchestration coupling.

## Task envelope contract

Every provider invocation should be represented as `kanban-capability-task/v1`.

Minimum fields:

```json
{
  "schema": "kanban-capability-task/v1",
  "task_id": "",
  "capability": "",
  "project_root": "",
  "active_slice": {},
  "input_artifact_refs": [],
  "output_root": "",
  "expected_outputs": [],
  "verification_expectations": [],
  "allowed_side_effects": [],
  "review_policy": {},
  "blocking_policy": {}
}
```

Rules:

- The task describes the need, not the implementation provider.
- Keep provider prompts short and artifact-path based.
- Pass only active-slice context unless a gate explicitly requires global reconciliation.
- Make allowed side effects explicit before code, file, network, deploy, or destructive actions.

## Result manifest contract

Providers return `kanban-capability-result/v1`-shaped manifests.

Minimum fields:

```json
{
  "schema": "kanban-capability-result/v1",
  "task_id": "",
  "capability": "",
  "provider": "",
  "result": "completed | partial | blocked | failed",
  "changed_files": [],
  "produced_artifacts": [],
  "evidence": [],
  "blockers": [],
  "debts": [],
  "review_required": false,
  "suggested_gate_updates": [],
  "next_recommended_task": null
}
```

Long reasoning, screenshots, diffs, prompt logs, Visual IR, spikes, parity reports, and repair notes belong in files referenced by the manifest.

## Gate and state semantics

- `review_required` / `review-required` routes to `review`, not generic `blocked`.
- `blocked` is only for missing input, external dependency, contradictory requirements, unsafe/destructive action, auth/permission, or secret issues.
- `partial` preserves usable artifacts and routes only the missing capability.
- Provider output is a recommendation until Javis records canonical project state, artifact manifest, and gate decision.
- Review completion is where downstream children may be unlocked.
- Skipped verification is `skipped` or `waived`, never `passed`.

## Progress reporting

For Weixin/project checkpoints, include:

- status label
- backend execution: yes/no
- completed in the last window
- current action
- next step
- next expected report

Batch updates. Do not send noisy micro-progress.

## Dispatch discipline

- Keep only one persistent orchestrator context.
- Load at most one provider skill per dispatch unless a gate explicitly needs cross-provider conflict resolution.
- Prefer manifest paths over chat history.
- Use parallel or delegated work only for independent slices.
- After answering routine user questions, continue the active orchestration loop unless the user pauses or changes direction.

## Hard stops

Stop and ask/record a blocker when the next step requires:

- destructive changes without explicit scope;
- secrets, tokens, passwords, or credential persistence;
- unknown auth/permission for real API work;
- irreversible external side effects;
- user approval for a direction-level visual/product decision;
- claiming completion without evidence or explicit waiver.

## Progressive references

Load only when needed:

- `references/kanban-skill-v2-redesign.md` — V2 redesign direction and role boundaries.
- `docs/contracts/kanban-capability-envelope-v1.md` — task/result envelope details.
- `docs/contracts/provider-registry-v1.md` — registry semantics.
- `docs/contracts/kanban-gate-policy-v1.md` — review/block/gate policy.
- `docs/contracts/provider-onboarding-checklist.md` — adding or replacing providers.
- `references/main-skill-full-reference.md` — legacy detailed workflow only when the compact kernel is insufficient.
- `references/stage-gates.md` — legacy gate matrix for non-kanban delivery.
- `references/skill-routing.md` — legacy routing details for non-provider work.
- `references/testing-strategy.md` — verification strategy details.
- `references/efficiency-rules.md` — low-token/low-cost execution rules.
- `templates/index.md` — artifact template index.

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Treating Javis as an implementation skill | Keep Javis as state/dispatch/gate owner; route work to providers |
| Matching by provider name first | Match by capability and registry |
| Passing full conversation history | Pass artifact refs and active slice |
| Provider marks global gate passed | Provider recommends; Javis records canonical gate state |
| Visual review becomes blocked | Use `review`, reserve `blocked` for real missing/unsafe input |
| Re-running whole workflows after partial result | Preserve artifacts and route only missing capability |
| Keeping all historical playbooks in main skill | Move depth to references and load only on trigger |
