# Javis AI Delivery OS Requirements

**Status:** Approved direction for PlanToDelivery B implementation
**Canonical project:** `/mnt/c/Users/imjzq/Projects/PlanToDelivery`
**Primary branch:** `kanban`

## 1. Positioning

PlanToDelivery SHALL evolve from a kanban-aware orchestrator kernel into the Javis AI Delivery OS: a stateful delivery system that moves a project from idea intake through brainstorming, blueprint, design, technical specification, implementation, verification, and final delivery.

The selected direction is **B: AI Delivery OS with Kanban DB as canonical state**.

This is not:

- a generic Trello/Jira clone;
- a one-shot prompt wrapper around provider skills;
- a full SaaS product rewrite in the first milestone;
- a merger of IdeaToDesign, IdeaToTech, or DesignToCode into PlanToDelivery.

## 2. Problems to solve

PlanToDelivery MUST solve these recurring delivery failures:

1. Project state gets lost when chat context is compacted or a session ends.
2. Agents skip requirements, design, assets, or technical specification and start coding too early.
3. Visual design, implementation assets, technical specs, screenshots, and acceptance evidence are not versioned or traceable.
4. Provider/subagent contexts become too large and include irrelevant history.
5. Parallel workers can overwrite shared routes, global styles, API clients, state stores, or dev server configuration.
6. Review-required work is incorrectly treated as blocked.
7. A blocked slice can stall the whole project even when independent slices can continue.
8. Progress reports depend on chat memory instead of durable events and snapshots.

## 3. Goals

PlanToDelivery MUST provide:

- a durable Kanban DB canonical state;
- project and slice gates that prevent skipped stages;
- a user-facing Slice Status Board;
- an internal Provider Task Board;
- a Review / Decision Board for user approvals, waivers, and change requests;
- artifact indexing and versioning for all important documents, images, manifests, and verification evidence;
- capability-first provider dispatch through neutral contracts;
- bounded TaskExecutionContext for subagents/providers;
- dev server reuse and resource locking;
- context snapshots for low-token recovery and reporting;
- layered verification for dev-loop, slice, stage, and final gates.

## 4. Non-goals

The first implementation MUST NOT:

- replace specialist providers with PlanToDelivery internals;
- depend on provider-specific file structures beyond provider manifests and artifact paths;
- use chat history as canonical state;
- use filesystem directories as state truth;
- treat high-fidelity page design boards as implementation asset sources;
- require a polished web UI before the runtime model works;
- rename all existing `kanban-*` contracts before compatibility is secured.

## 5. User stories

### 5.1 Project owner

As the user, I want to see each page/feature as a Slice card so that I know what is waiting for design, tech spec, implementation, verification, review, or completion.

As the user, I want decisions and waivers concentrated in one Review / Decision Board so that I can approve work in batches instead of being interrupted by low-value questions.

As the user, I want progress reports generated from durable state so that I can ask “continue” after context loss and the system knows what to do next.

### 5.2 Orchestrator

As Javis, PlanToDelivery needs a short ProjectControlSnapshot and SliceControlSnapshot so that it can recover state without loading every artifact.

As Javis, PlanToDelivery needs Hermes Kanban constraints so that it cannot dispatch implementation before requirements, design references, asset plans, tech specs, and blocking decisions are cleared.

### 5.3 Provider / subagent

As a provider, I want a bounded task envelope with artifact refs, allowed files, forbidden files, resource locks, and acceptance criteria so that I can execute without knowing the full project history.

As a provider, I want to return a result manifest so that the orchestrator can ingest artifacts, blockers, debts, evidence, and next recommendations deterministically.

## 6. Success criteria

The B implementation is successful when:

1. A single project and single slice can complete an end-to-end flow from requirements artifact to verification evidence.
2. Hermes Kanban state, not JSON files, SQLite, or chat history, determines the current executable board status.
3. Implementation tasks cannot be unlocked without required Hermes Kanban dependencies, review evidence, or explicit waivers recorded as Kanban evidence.
4. `review_required` routes to review, not blocked.
5. Artifact refs can identify the approved design crop, asset crop, tech spec, screenshot, comparison, and acceptance report.
6. A project can resume from ProjectControlSnapshot after context loss.
7. Dev server state and resource locks prevent duplicate dev servers and unsafe parallel edits.

## 7. Implementation priority

The first implementation priority is:

1. Hermes Kanban canonical state.
2. Kanban constraint compiler/review controller.
3. Artifact Index.
4. Board projections.
5. Provider runtime integration.
6. Dev server manager and resource locks.
7. Verification runtime.
8. Reporting and resume snapshots.
