# Kanban Orchestrator Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task after the contract envelope is accepted. PlanToDelivery is the kanban-aware orchestrator; provider skills remain decoupled.

**Goal:** Turn PlanToDelivery into the canonical kanban-aware orchestration layer that routes project work by capability contract rather than by hard-coded skill identity.

**Architecture:** PlanToDelivery owns project stage, task graph, Kanban constraint policy, worker assignment, and progress reporting. It talks to providers through a neutral capability envelope and result manifest. Provider-specific implementation details stay outside PlanToDelivery.

**Tech Stack:** Markdown skill docs, JSON-schema-like contract files, Hermes kanban states, provider manifests from IdeaToDesign / IdeaToTech / DesignToCode.

---

## Non-negotiable Boundaries

- PlanToDelivery may know kanban states and transition rules.
- PlanToDelivery must not import, vendor, or hard-code DesignToCode, IdeaToDesign, or IdeaToTech internals.
- Tasks describe the needed capability, not the preferred tool.
- Providers advertise capabilities through manifests.
- `review_required` maps to the Hermes Kanban review flow, not a generic blocker.
- `blocked` is reserved for missing prerequisite, credential, impossible input, or external dependency.

## Capability Envelope v1

Every dispatched provider task should be represented as:

```json
{
  "schema_version": "kanban-capability-task/v1",
  "task_id": "kb_123",
  "correlation_id": "project-stage-task",
  "capability": "visual_implementation",
  "objective": "Implement approved mobile H5 visual source",
  "inputs": {
    "project_path": "/abs/path",
    "source_artifacts": [],
    "requirements": [],
    "constraints": [],
    "acceptance_criteria": []
  },
  "orchestration": {
    "origin": "kanban",
    "stage": "implementation",
    "priority": "normal",
    "review_policy": "required_before_children"
  }
}
```

## Result Manifest v1

Providers return a neutral manifest:

```json
{
  "schema_version": "kanban-capability-result/v1",
  "task_id": "kb_123",
  "capability": "visual_implementation",
  "status": "completed",
  "summary": "Implemented page shell and captured screenshot evidence.",
  "artifacts": [],
  "changed_files": [],
  "evidence": [],
  "review_required": false,
  "blocked": false,
  "blockers": [],
  "debt": [],
  "next_tasks": []
}
```

## State Mapping

| Provider result | Kanban transition | Notes |
|---|---|---|
| `status=completed`, `review_required=false` | `done` | Can unlock children. |
| `status=completed`, `review_required=true` | `review` | Must not become `blocked`. |
| `status=partial`, `review_required=true` | `review` | Human/strong-model review decides continuation. |
| `blocked=true` with blockers | `blocked` | Requires missing input/external dependency. |
| validation failure | `blocked` or retry | Use blocker only when retry cannot proceed. |

## Task Breakdown

### Task 1: Add contract envelope documentation

**Objective:** Document the canonical task/result/provider manifest fields in PlanToDelivery.

**Files:**
- Create: `docs/contracts/kanban-capability-envelope-v1.md`

**Verification:**
- File exists.
- Contains `kanban-capability-task/v1`, `kanban-capability-result/v1`, and `provider-manifest/v1`.
- Contains explicit `review_required != blocked` rule.

**Commit:**
```bash
git add docs/contracts/kanban-capability-envelope-v1.md
git commit -m "docs: define kanban capability envelope"
```

### Task 2: Add provider registry design

**Objective:** Define how PlanToDelivery maps capabilities to provider skills without coupling to implementation details.

**Files:**
- Create: `docs/contracts/provider-registry-v1.md`

**Registry example:**
```json
{
  "schema_version": "provider-registry/v1",
  "providers": [
    {
      "provider_id": "design-to-code",
      "capabilities": ["visual_implementation"],
      "manifest_path": "provider-manifest.json"
    }
  ]
}
```

**Verification:**
- Registry doc explains provider selection order.
- Registry doc says provider ID is metadata, not an orchestrator branch condition.

**Commit:**
```bash
git add docs/contracts/provider-registry-v1.md
git commit -m "docs: design kanban provider registry"
```

### Task 3: Add Kanban constraint policy documentation

**Objective:** Encode how P2D handles review, blocker, stage, and progress gates.

**Files:**
- Create: `docs/contracts/kanban-constraint-policy-v1.md`

**Verification:**
- Includes pre-flight, revision, escalation, and abort gates.
- Defines `review_required` transition to `review`.
- Defines `blocked` transition criteria.
- Defines child unlock behavior after review completion.

**Commit:**
```bash
git add docs/contracts/kanban-constraint-policy-v1.md
git commit -m "docs: define kanban Kanban constraint policy"
```

### Task 4: Add orchestration handoff checklist

**Objective:** Make future provider integration repeatable.

**Files:**
- Create: `docs/contracts/provider-onboarding-checklist.md`

**Verification:**
- Checklist covers capability, input contract, result manifest, evidence, review policy, and validation.
- Checklist bans direct hard-coded provider internals.

**Commit:**
```bash
git add docs/contracts/provider-onboarding-checklist.md
git commit -m "docs: add kanban provider onboarding checklist"
```

### Task 5: Sync skill runtime only after docs stabilize

**Objective:** Avoid drifting runtime skill until the branch contract is reviewed.

**Files:**
- Later modify runtime `PlanToDelivery` skill or source skill files after acceptance.

**Verification:**
- Runtime change references the accepted contract docs.
- Skill still works standalone for non-kanban project planning.

---

## Acceptance Criteria

- PlanToDelivery defines the canonical kanban capability envelope.
- Provider skills can implement contracts without importing PlanToDelivery code.
- Orchestrator can choose a provider by `capability` and manifest metadata.
- Review and blocker states remain semantically distinct.
- The plan leaves tactical skills outside kanban.
