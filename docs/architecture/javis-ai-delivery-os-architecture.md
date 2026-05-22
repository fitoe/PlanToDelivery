# Javis AI Delivery OS Architecture

**Status:** Approved architecture direction
**Canonical project:** `/home/imjzq/Projects/PlanToDelivery`

## 1. Overview

PlanToDelivery is the Javis orchestration kernel. It owns state recovery, Kanban constraint policy, capability routing, provider dispatch, result ingestion, review/block decisions, progress rollup, and checkpoint handoff.

Specialist providers own bounded capabilities:

- IdeaToDesign: product visual design, visual source creation.
- IdeaToTech: technical blueprint, implementation planning, verification strategy.
- DesignToCode: visual implementation.
- Built-in/command workers: screenshots, crops, build/test checks, artifact processing.

PlanToDelivery communicates with providers through contracts and artifacts only.

## 2. Canonical state

Kanban DB SHALL be the canonical state. Files are artifacts. JSON state MAY exist as export or test fixture, but MUST NOT be treated as the primary source of truth.

Canonical state includes:

- Project
- Slice
- KanbanDependency
- CapabilityTask
- Provider
- Artifact
- Decision
- Waiver
- ChangeRequest
- DevServer
- ResourceLock
- Event

## 3. Core flow

```text
Project Intake
  -> Brainstorming
  -> Requirements Draft
  -> Delivery Blueprint
  -> Decision Clearance
  -> Design & Asset Planning
  -> Tech Spec
  -> Controlled Execution
  -> Verification & Delivery
```

Every stage produces artifacts and updates Hermes Kanban cards/dependencies/events.

## 4. Board projections

### 4.1 Slice Status Board

The user default board contains Slice cards grouped by user-facing status:

```text
待澄清 / 待蓝图 / 待设计 / 待素材规划 / 待技术说明 / 待决策 / 待实现 / 实现中 / 待验证 / 待审查 / 已阻塞 / 已完成
```

### 4.2 Provider Task Board

The internal execution board contains CapabilityTask cards grouped by engine status:

```text
backlog / ready / dispatched / running / review / blocked / retrying / partial / completed / failed / cancelled / waived
```

### 4.3 Review / Decision Board

The approval board contains Decisions, Reviews, Waivers, and ChangeRequests grouped by review state.

## 5. Kanban Constraint Controller

Kanban Constraint Controller owns unlock rules. Providers MAY recommend Kanban constraint changes, but PlanToDelivery records canonical Kanban transitions.

Project-level Kanban dependencies include brainstorming, requirements, blueprint, decision clearance, execution plan, and final delivery approval.

Slice-level Kanban dependencies include requirements, design reference, asset plan, tech spec, implementation readiness, implementation done, verification passed, and delivery approval.

## 6. Artifact Index

Artifact Index stores metadata and approved refs for documents, images, manifests, screenshots, comparisons, logs, and reports. DB stores refs, versions, summaries, hashes, dimensions, and approval status; file contents remain on disk.

High-fidelity design is split into:

- Design Board: multi-page/state design artifact.
- Page Design Crop: approved implementation reference.

Implementation assets are split into:

- Asset Requirements.
- Asset Board.
- Asset Crop used by code.

## 7. Provider Runtime

Provider runtime is capability-first:

1. Select provider by capability registry.
2. Generate `kanban-capability-task/v1` task envelope.
3. Dispatch manual/subagent/command/builtin provider.
4. Ingest `kanban-capability-result/v1` result manifest.
5. Validate schema and artifact refs.
6. Update task status, Kanban dependencies, events, boards, blockers, debts, and review items.

## 8. Context control

PlanToDelivery MUST avoid loading full project history by default.

It uses:

- ProjectControlSnapshot
- SliceControlSnapshot
- TaskExecutionContext

TaskExecutionContext is the only default payload passed to providers/subagents. It contains objective, artifact summaries, artifact paths, allowed files, forbidden files, locks, dev server URL, verification level, acceptance criteria, and return manifest schema.

## 9. Dev Server Manager

Each project SHOULD have one primary dev server record. Workers MUST query dev server state before starting new processes. Healthy dev servers are reused. Restarts require a recorded event.

## 10. Resource Locks

Shared resources require locks before modification:

- route
- global_style
- theme_tokens
- shared_component
- api_client
- state_store
- build_config
- dev_server
- dependency

Independent slices can run in parallel only when resource locks and dependencies do not conflict.

## 11. Verification Runtime

Verification levels:

- `dev_loop`: targeted developer checks; no routine full build/lint.
- `slice_checkpoint`: route smoke, screenshot or local confirmation, visual deviation report.
- `stage_checkpoint`: stage-level lint/type/test/build as needed.
- `final_checkpoint`: complete build/test/evidence/acceptance report.

## 12. Reporting and resume

Progress reports are generated from snapshots and recent append-only events, not chat memory. Reports should include status, backend execution, recently completed work, current action, next step, decisions needed, and blockers/risks.
