---
name: PlanToDelivery
description: Javis/Kanban orchestrator kernel. Use when coordinating project delivery through state recovery, capability registry matching, provider task envelopes, result manifest ingestion, Kanban review/block/complete constraints, progress reporting, and checkpoint handoff.
---

# PlanToDelivery — Javis Orchestrator Kernel

## Role

PlanToDelivery is the canonical **Javis** project orchestrator. It owns project state, capability routing, provider dispatch, result ingestion, Kanban review/block/complete decisions, progress rollup, and final handoff.

It does **not** own specialist implementation details. Design, technical planning, and implementation are provided by capability providers through explicit contracts.

Canonical project root for Javis work:

```text
/home/imjzq/Projects/PlanToDelivery
```

The previous `JavisKanban` project is not canonical.

## When to activate

Use this skill when:

- the user says `贾维斯`, `贾维斯继续`, `Javis`, `kanban`, or asks to continue a project through orchestration;
- a workflow references `kanban-capability-task/v1`, `provider-manifest/v1`, `provider-registry/v1`, Kanban review/block/complete constraints, or provider result manifests;
- multiple specialist capabilities must be sequenced, reviewed, or checkpointed;
- project state must be recovered and the next capability selected.

## Core loop

1. **Recover state** — read durable project state first: `.hermes/project-state/*`, `project-state/*`, or legacy `docs/orchestrator/*` only as fallback.
2. **Select active slice** — identify the smallest project/page/feature slice that can move next.
3. **Choose capability** — match the next need to a capability, not to a hard-coded provider.
4. **Create task envelope** — produce one bounded `kanban-capability-task/v1` per provider invocation.
5. **Dispatch provider** — call or instruct the provider using artifact paths, expected outputs, allowed side effects, and review policy.
6. **Ingest manifest** — require a `kanban-capability-result/v1`-shaped result before updating canonical state.
7. **Apply Kanban constraint** — move the card through review, blocked, partial, or completed outcomes from evidence, not prose confidence.
8. **Roll up progress** — update state, artifact index, blockers/debts, and user-facing checkpoint.
9. **Continue or hand off** — route the next capability unless a hard blocker, destructive action, secret/auth issue, or Kanban review/user approval stop requires pausing. After a review/user approval stop is approved, continue immediately: record approval evidence, complete/unlock the reviewed card, resolve only hard prerequisite blockers, then dispatch/resume the next ready child instead of stopping at the checkpoint.

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

- `write_provider_registry_config(path, providers={...})` writes `provider-registry/v1` with explicit normalized provider manifest paths.
- `bootstrap_provider_registry_from_manifests(path, provider_manifests={...})` bootstraps the canonical registry from real IdeaToDesign, IdeaToTech, and DesignToCode `contracts/provider-manifest.json` files. It normalizes compact provider manifests (`schema_version`, `provider_id`, string capabilities) into runtime `provider-manifest/v1` snapshots beside the registry config, then routes dispatch through those snapshots.
- `load_provider_registry_config(path)` validates that registry config before dispatch.
- `load_provider_registry(root_or_config)` scans `provider-manifest.json` files from either a directory or a `provider-registry/v1` config file and returns a capability-indexed registry.
- `create_task_envelope(...)` builds capability-first `kanban-capability-task/v1` payloads without embedding provider identity.
- `calculate_file_sha256(path)` returns the sha256 hex digest for a local file and is used by the provenance chain.
- `build_active_slice_digest(...)`, `validate_active_slice_digest(...)`, and `render_provider_handoff_prompt(...)` create/validate the short `active-slice-digest/v1` execution context. The digest is written beside each task envelope as `active-slice-digest.json`, keeps only bounded active-slice/artifact/manifest/verification/stop-rule data, excludes chat history, and provider handoff prompts should reference paths instead of pasting long context. When the task envelope file already exists, the digest records `provenance.task_envelope_path` and `provenance.task_envelope_sha256` so later result/audit steps can detect drift.
- `plantodelivery.provider_guard.validate_provider_execution_context(...)` is the provider-side P2D Kanban admission check. In P2D-dispatched provider mode, call it before implementation work starts with the task envelope path, active-slice digest path, expected capability, and Hermes backend. It rejects missing/invalid envelope or digest files, capability/digest mismatches, non-`output_root/result-manifest.json` handoffs, and cards that are not currently `running`. Providers may still be used standalone outside P2D, but P2D mode must not execute from chat history or unclaimed cards.
- `P2DMeta`, `append_p2d_meta_marker(text, meta)`, `extract_p2d_meta_marker(body=..., comments=[...])`, `validate_p2d_meta(...)`, and `p2d_meta_to_task_envelope(...)` are the bridge from existing Hermes Kanban cards to P2D semantics. They store a base64url JSON `p2d-meta/v1` payload inside a Markdown-safe `<!-- P2D_META ... P2D_META -->` marker in the task body or a task comment. This avoids adding custom Hermes Kanban fields while preserving capability, active slice, artifact refs, expected outputs, side-effect limits, optional provider hints, and dependencies.
- `validate_result_manifest(...)` checks `kanban-capability-result/v1` provider outputs before state updates.
- `diagnose_provider_registry(project_root, required_capabilities=[...])` returns `p2d-provider-doctor/v1` with discovered providers/capabilities, required capabilities, missing capabilities, and violations. `scripts/p2d_doctor.py --required-capability ... --json` must be used before real dispatch when a milestone depends on specific provider capabilities.
- `write_project_alias_registry(...)`, `load_project_alias_registry(...)`, and `resolve_project_alias(...)` handle `p2d-project-aliases/v1`. Unknown aliases are contract errors; do not broad-search the filesystem to guess a project.
- `build_approval_packet(...)` and `validate_approval_packet(...)` produce `p2d-approval-packet/v1` for review-required results. `scripts/p2d_enforce.py approval-packet ...` writes the packet to disk for user confirmation.
- `build_resume_snapshot(...)` produces `p2d-resume-snapshot/v1` with review, blocked/failed, running, ready task lists and deterministic resume actions. `scripts/p2d_enforce.py resume --output ...` should be used at cold-start/checkpoint boundaries.
- `KanbanStateStore(root)` is the JSON-backed artifact/export implementation under `project-state/kanban`: it writes task envelopes and result manifests as evidence files, keeps `kanban-state.json` synchronized for debug, fixtures, migration/export, and contract tests, and must not be treated as an executable backend. New/real Javis projects must not use it through `KanbanOrchestrator`.
- **Self-managed SQLite has been removed.** Do not reintroduce `KanbanSQLiteStateStore`, `state_backend="sqlite"`, `kanban-state.sqlite3`, SQLite event-key recovery, or project-local DB status fields as P2D canonical state. Historical SQLite data may be read only through explicit one-off migration/export tooling if needed.
- **Hermes Kanban is mandatory for execution.** For real V2 orchestration, compile P2D capability/provider work into Hermes Kanban tasks, links, claims, completes, blocks, reviews, runs, and events. Do not provide or preserve a no-board execution mode. Do not treat any project-local JSON/SQLite `status` field as the authority for whether work may start or finish. P2D storage is only a semantic overlay and evidence/export layer; Hermes Kanban owns `todo/ready/running/review/blocked/done` lifecycle enforcement.
- The V2 goal is workflow enforcement, not merely state persistence: task DAG unlocks, review steps, and provider handoffs must go through Hermes Kanban transitions (`create_task` / task links / `claim_task` / `complete_task` / `block_task` / review claim or equivalent CLI/API path) so agents cannot bypass Kanban by directly writing status.
- Do not add board adapters for display-only compatibility. If the state model changes, evolve the Hermes-Kanban-backed compiler/overlay and their contract tests directly.
- `HermesKanbanBackend(project_root=..., board="plantodelivery", hermes_home=...)` is the minimal public-CLI adapter for real execution. It initializes/creates the board through `hermes kanban`, writes the same JSON task/result overlay as evidence, creates cards with `P2D_META`, maps local P2D task ids to Hermes `t_*` ids, and supports create/read/claim/complete/block/link without importing Hermes Agent internals. `record_task(...)` also writes `active-slice-digest.json` beside `task-envelope.json` and includes its path in the card metadata for short-context provider handoff. Enforcement rules now live here: provider results are rejected unless the Hermes card is currently `running`; `review_required=true` writes the result manifest, comments `P2D RESULT READY FOR REVIEW`, and moves the card into Kanban review/block flow instead of marking it done; `approve_review(task_id, evidence=[...])` requires non-empty review evidence, comments `P2D REVIEW APPROVED`, then completes the Hermes card; `audit_enforcement(strict_digest=True)` reports missing/invalid `P2D_META`, missing/invalid active-slice digest, done cards without result manifests, and review-required done cards without approval evidence.
- `KanbanOrchestrator(project_root=..., providers_root=..., state_backend="hermes", state_store=...)` is the minimal contract facade for real execution: `dispatch_task(...)` selects a provider by capability, creates the corresponding Hermes Kanban card, returns `task_path` plus `digest_path`, and uses Hermes Kanban as the execution constraint. `state_backend` defaults to `"hermes"`; passing `state_backend="json"` is rejected because no-board execution is not supported. `state_store=` is only for explicit unit tests, migration/export tooling, or custom injected stores outside real project execution. `ingest_result(...)` or `ingest_result_path(...)` validates and persists provider result artifacts then updates overlay card/event export state; `approve_review(task_id, evidence=[...])` advances a reviewed task through the backend. `dispatch_next_ready_task()` is still a future automation layer; do not use it to bypass Hermes Kanban claim/complete/block transitions.
- Standalone installation uses only skill assets plus public Hermes CLI. The skill ships `scripts/p2d_doctor.py`, `scripts/p2d_setup.py`, `scripts/p2d_smoke.py`, `scripts/p2d_enforce.py`, and `references/standalone-installation.md`; run them from an installed skill copy to verify/install without modifying Hermes Agent source code.
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
- Pass only active-slice context unless Kanban review/conflict resolution explicitly requires global reconciliation.
- Make allowed side effects explicit before code, file, network, deploy, or destructive actions.
- If a Gate decides whether another stage/card may start, model it as Kanban: create a review/approval card and link downstream cards to it. Artifact manifests, provider outputs, and local JSON status may support the Gate, but must not unlock work by themselves.
- Encode the exact approval artifact required for downstream work in `input_artifact_refs`, `review_policy`, `blocking_policy`, or `kanban_constraints` so providers cannot infer approval from prose alone.

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
  "suggested_kanban_updates": [],
  "next_recommended_task": null
}
```

Long reasoning, screenshots, diffs, prompt logs, Visual IR, spikes, parity reports, and repair notes belong in files referenced by the manifest.

## Kanban constraint semantics

- Any Gate that decides whether a downstream stage/card may start must be represented as a Hermes Kanban constraint: a real review/approval card plus explicit dependency/link from the downstream card. A markdown manifest, local JSON status, provider recommendation, or prose checkpoint may document the Gate, but must not be the authority that unlocks work.
- Gate holds must be lifecycle-enforced, not only described. For user/design/content approval Gates, ensure downstream implementation cards depend on an unfinished approval/review parent, or keep the Gate in a real non-dispatchable hold (`blocked`/review-required) and verify with a dispatcher pass that `spawned: []` for downstream cards. Do not rely on `--initial-status blocked` alone when all parents are already done; dispatch may promote/spawn it. If that happens, immediately reclaim the accidental worker, block the Gate with an explicit review-required reason, and re-run dispatch to prove children remain `todo`.
- Stage-admission Gates include product/content direction approval, visual/design-source freeze, architecture/API decision approval, implementation-readiness approval, release/deploy approval, and any user-confirmed scope freeze. If the answer to “can the next phase start?” changes, encode that answer in Kanban.
- Provider `suggested_kanban_updates` / `next_recommended_task` are advisory only. Javis must translate accepted suggestions into concrete Hermes Kanban cards, links, review states, comments, and completion events before treating them as canonical.
- `review_required` / `review-required` routes to `review`, not generic `blocked`.
- If the underlying Hermes Kanban lifecycle lacks a first-class review state in a given path, mechanical `blocked` may only be used as a lifecycle hold. The user-facing state must still be reported as `待确认 / review-required`, with a comment/result that names produced artifacts, review target, required approval, and makes clear this is not missing work.
- When a review gate is reached, do not repeatedly dispatch the same provider just because the card is mechanically held. Summarize the review packet in the main session and wait for explicit approval or requested changes.
- For iterative visual-design review gates, do **not** run an extra self-review / critique pass after generating a new design unless the user explicitly asks for review. Produce the visual artifact, persist the prompt/artifact paths, and send it directly to the user for judgement. This keeps design iteration fast and avoids the orchestrator becoming the reviewer when the user wants to judge the design directly.
- Approval is not a stopping point. Once the user/main session approves a review gate, Javis must record the approval artifact/evidence, mark or approve the reviewed task through Hermes Kanban, unlock/dispatch the next ready child, and keep the orchestration loop moving unless a hard stop applies.
- When a user says a visual/design direction is `定稿`, `可以`, `通过`, or otherwise approved, do **not** stop after recording/unblocking. Treat the approval as permission to continue the already-planned downstream implementation. Immediately resume the next ready Kanban child using the approved artifact as the design source, unless the user explicitly says `暂停/先别做/等一下` or the next action hits a hard stop.
- Visual implementation tasks require explicit approved design-source evidence at the level the user expects for the project. For UI/website rebuilds, a text handoff/tokens/page briefs package is not enough unless the user explicitly waives visual mockup/preview confirmation. The Kanban dependency must name the required visual approval artifact (for example homepage visual preview, Figma/GPT image board, or approved screenshot-as-design-source) and downstream implementation cards must depend on that approval card, not only on a structured D2 handoff.
- For multi-page UI/website rebuilds, homepage approval only releases the homepage/global-shell implementation slice. Before implementing other page families/templates, Javis must create explicit visual-source review Gate card(s) for those page families/templates, such as `other core pages visual confirmation`, `departments/doctors visual confirmation`, `guide/contact/appointment visual confirmation`, or `news/detail visual confirmation`. The downstream implementation cards for those page families must depend on the corresponding approved visual Gate, not merely on homepage approval, global tokens, page briefs, or a single D2 handoff. If the user explicitly approves a reduced Gate (for example one combined board covering all remaining templates), record that approval artifact and make the implementation card depend on it.
- Homepage approval must not be silently widened later. When rebasing or recovering a project from a homepage-finalization point, record an approval anchor card/artifact whose released scope is homepage/global shell only, then model every non-homepage page family behind its own unfinished or review-held Gate. A downstream card is valid only if its real Hermes parent chain includes the corresponding visual-source Gate; prose `depends_on`, local JSON, or chat memory is not enough.
- A project-level UI rebuild DAG should separate design-source confirmation from implementation at the granularity that can affect visual layout. Use the smallest practical Gate set: one combined Gate is acceptable for simple/static sites; split Gates are required when page families have materially different layouts, states, or conversion tasks. Do not silently broaden implementation scope beyond the approved visual-source coverage.
- `blocked` is only for missing input, external dependency, contradictory requirements, unsafe/destructive action, auth/permission, or secret issues.
- `partial` preserves usable artifacts and routes only the missing capability.
- Provider output is a recommendation until Javis records canonical project state, artifact manifest, and Kanban lifecycle decision.
- Review completion is where downstream children may be unlocked; when a task moves from `review` to `completed`, overlay/export stores must append one idempotent `dependency_unlocked` event per newly dispatchable `ready` child whose `depends_on` are now all completed. DB-backed stores use a stable `event_key` unique index for unlock-event idempotency; avoid read-then-insert-only logic that can race during recovery.
- Skipped verification is `skipped` or `waived`, never `passed`.

## Progress reporting

For Weixin/project checkpoints, include:

- status label
- backend execution: yes/no
- completed in the last window
- current action
- next step
- next expected report

Batch updates. Do not send noisy micro-progress. A checkpoint is a visibility artifact, not a lifecycle stop: after sending a routine progress update, continue polling/dispatching if downstream work is ready or already running. Only hard blockers, destructive/irreversible side effects, secret/auth issues, direction-level approvals, or an explicit user pause may stop the loop.

## Dispatch discipline

- Keep only one persistent orchestrator context.
- Load at most one provider skill per dispatch unless Kanban review/conflict resolution explicitly needs cross-provider comparison.
- For implementation/coding cards dispatched by Javis, also load and apply `karpathy-coder` as a coding-discipline constraint. This is an explicit exception to the one-provider-skill limit because `karpathy-coder` is not a provider; it is a cross-cutting guard. It requires: surface assumptions before coding, keep the solution simple, make surgical changes only, avoid speculative abstractions/refactors, and define verifiable success checks before claiming completion.
- Prefer manifest paths over chat history.
- Use parallel or delegated work only for independent slices.
- After answering routine user questions or sending routine checkpoints, continue the active orchestration loop unless the user pauses, changes direction, or a hard stop applies.
- After a user approves a direction-level review gate, do not stop at acknowledgement; immediately record the approval and advance the next eligible Kanban card.
- For approved visual/design freeze gates, acknowledgement is only a checkpoint. If the next implementation card is already planned and unblocked, claim/run it immediately after recording approval; do not wait for a second `继续` unless the user explicitly pauses or changes scope.

## No-bypass provider execution guard

When the active project is being run as `贾维斯` / PlanToDelivery / P2D / Hermes Kanban, provider work is not allowed to start from chat context, restored TODOs, or local confidence alone.

Before any provider-side code edit, design generation, visual implementation, API integration, or verification slice, Javis must establish all of the following:

1. a real Hermes Kanban card exists for the active slice and capability;
2. the card is claimed/running through the P2D/Hermes path, not only represented in the session `todo` tool;
3. a `kanban-capability-task/v1` task envelope exists and names `project_root`, `active_slice`, `input_artifact_refs`, `output_root`, expected outputs, side-effect limits, and review policy;
4. an `active-slice-digest/v1` exists beside the envelope;
5. the provider can run its admission check against the envelope/digest or an equivalent `p2d_enforce.py claim`/backend claim has succeeded.

If any item is missing, do not proceed with provider edits. Create/repair the Kanban card/envelope/digest first, or report the slice as blocked with the missing enforcement artifact. A session `todo` entry may summarize progress for the chat, but it must never substitute for Hermes Kanban lifecycle enforcement.

### Visual implementation hard gate

For `visual_implementation` cards, Javis must pass the D2C provider an approved visual source and require DesignToCode evidence before allowing review or downstream work:

- approved design-source artifact path, not just prose or a previous chat statement;
- page contract and pass criteria in the envelope/digest;
- expected Visual IR or extraction artifact before implementation edits;
- expected screenshot/parity evidence and `kanban-capability-result/v1` manifest;
- `review_required: true` unless the user explicitly waived visual review.

If a user asks `继续` after approving a visual direction, Javis should continue automatically, but only by claiming/running the next eligible Hermes Kanban card and dispatching the provider with the envelope/digest. It must not jump straight into file edits from the main chat.

## Kanban state-machine enforcement

Every Javis step must be represented as an explicit state-machine transition, not as an informal checklist item.

Required model:

```text
intake
  -> normalized
  -> planned
  -> gated
  -> ready
  -> dispatched
  -> claimed/running
  -> provider-admitted
  -> executing
  -> result-produced
  -> manifest-validated
  -> review-required | blocked | failed | completed
  -> approval-recorded | blocker-recorded | done
  -> downstream-unlocked | handoff
```

Rules:

- No orchestration step may advance by prose, chat memory, session `todo`, or local JSON status alone. Each advance must map to a Hermes Kanban task event, dependency edge, review/approval event, block event, completion event, or an evidence artifact referenced by such an event.
- State changes must be guarded by preconditions and evidence. Example: `ready -> running` requires dependency satisfaction plus `claim`; `running -> provider-admitted` requires envelope/digest validation; `result-produced -> manifest-validated` requires a valid result manifest; `review-required -> completed` requires approval evidence.
- A provider cannot skip directly from task receipt to done. It must pass through admission, execution, result manifest, validation, and Kanban lifecycle update.
- Gate decisions are state-machine nodes. Product direction, visual freeze, architecture approval, implementation readiness, release/deploy approval, and user scope freeze must be explicit review/approval states with downstream dependencies.
- Dispatcher/resume logic must be state-derived: compute next actions from current Kanban state and dependency graph, not from past conversation. Recovery must rebuild the same state-machine position from Kanban events and evidence.
- If a required state or transition is missing, Javis must create/repair the Kanban card, edge, envelope, digest, approval packet, or result manifest before continuing; otherwise mark the slice blocked with the missing transition as evidence.
- Runtime enforcement lives in `plantodelivery/kanban_runtime.py`: every `_sync_card(...)` event must carry a `state_machine` transition and the canonical `state_machine` log must validate as `p2d-state-machine-transition/v1`.
- `p2d_enforce.py audit --fail-on-violation` must fail when Kanban events have no transition object, a transition has an unknown action/state, or guarded transitions (`dispatch`, `claim`, `provider_admitted`, `ingest_result`, `review_required`, `approve_review`, `dependency_unlocked`) have no evidence.
- Tests or smoke checks must exercise at least dispatch -> ingest_result -> approve_review and assert both the event log and the state-machine log contain matching validated transitions.

## Hard stops

Stop and ask/record a blocker when the next step requires:

- destructive changes without explicit scope;
- secrets, tokens, passwords, or credential persistence;
- unknown auth/permission for real API work;
- irreversible external side effects;
- user approval for a direction-level visual/product/content/IA decision before the decision is frozen;
- after direction-level approval is granted, continuing downstream implementation is not a new hard stop unless scope changes or another hard-stop condition appears;
- claiming completion without evidence or explicit waiver.

## Progressive references

Load only when needed:

- `references/standalone-installation.md` — install/setup/doctor/smoke workflow for using this skill without modifying Hermes Agent; includes the mandatory `p2d_enforce.py claim|ingest|approve|audit` wrapper for strict Hermes Kanban constraints.
- `references/kanban-skill-v2-redesign.md` — V2 redesign direction and role boundaries.
- `docs/contracts/kanban-capability-envelope-v1.md` — task/result envelope details.
- `docs/contracts/provider-registry-v1.md` — registry semantics.
- `docs/contracts/provider-collaboration-v2.md` — provider roles, capability flow, review/block semantics, and alignment checklist.
- `docs/contracts/kanban-constraint-policy-v1.md` — legacy review/block policy reference; do not present it as a separate execution system.
- `docs/contracts/provider-onboarding-checklist.md` — adding or replacing providers.
- `references/main-skill-full-reference.md` — legacy detailed workflow only when the compact kernel is insufficient.
- `references/stage-gates.md` — legacy reference only; do not use it for V2 execution.
- `references/skill-routing.md` — legacy routing details for non-provider work.
- `references/testing-strategy.md` — verification strategy details.
- `references/efficiency-rules.md` — low-token/low-cost execution rules.
- `templates/index.md` — artifact template index.

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Treating Javis as an implementation skill | Keep Javis as state/dispatch/Kanban constraint owner; route work to providers |
| Matching by provider name first | Match by capability and registry |
| Passing full conversation history | Pass artifact refs and active slice |
| Provider tries to bypass Kanban completion | Provider recommends; Javis records canonical Kanban lifecycle state |
| Visual review becomes blocked | Use `review`, reserve `blocked` for real missing/unsafe input |
| Re-running whole workflows after partial result | Preserve artifacts and route only missing capability |
| Keeping all historical playbooks in main skill | Move depth to references and load only on trigger |
