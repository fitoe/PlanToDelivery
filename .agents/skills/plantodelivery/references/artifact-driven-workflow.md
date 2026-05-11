# Artifact Driven Workflow

Use this reference to coordinate skills without creating hard skill-to-skill dependencies.

Main rule:
- route by artifact readiness, approval evidence, and gate status
- do not require artifacts to come from one specific skill when an equivalent source exists

---

## Core Files

Recommended repository state:

```text
docs/orchestrator/
  project-state.json
  artifact-manifest.json
  approval-records.json
  handoff-manifest.json
  gate-checks/
```

Use these JSON files for gate checks. Keep Markdown docs for human review.

---

## Artifact Manifest

Use `templates/artifact-manifest-template.json`.

Purpose:
- declare what artifact exists
- declare where files live
- declare artifact status
- connect artifact to flows, pages, sections, and approvals

Gate rule:
- file paths in required manifest entries must exist
- temp-only paths and chat-only references do not satisfy gates

---

## Approval Records

Use `templates/approval-records-template.json`.

Purpose:
- record first-order user decisions
- avoid treating implied consent as approval
- keep approval evidence separate from long chat history

Gate rule:
- UI direction, design source, implementation brief, stack, and final acceptance require explicit approval records unless marked `n/a`

---

## Project State

Use `templates/project-state-template.json`.

Purpose:
- define current owner skill
- record readiness levels
- record blocked reason and next allowed skill

Readiness levels:
- `design_ready`
- `implementation_ready`
- `verification_ready`
- `handoff_ready`

---

## Handoff Manifest

Use `templates/handoff-manifest-template.json`.

Purpose:
- move work between skills without loading full history
- record artifacts, approvals, open questions, and next action

Use when:
- `idea-to-design` finishes design work
- `design-to-code` finishes implementation work
- `PlanToDelivery` pauses or transfers a milestone

---

## Degradation Paths

If `idea-to-design` is unavailable:
- accept manual PRD, Figma files, screenshots, or design docs if manifest and approval records satisfy gates

If `design-to-code` is unavailable:
- use ordinary frontend implementation flow, but keep approved visual source and verification plan

If `PlanToDelivery` is unavailable:
- `idea-to-design` and `design-to-code` remain standalone and may operate from their own inputs

---

## Bypass Rule

User may intentionally bypass a gate only if all are recorded:
- which gate was bypassed
- why it was bypassed
- accepted risk
- rollback or correction path

Record this as `decision_type: gate-bypass` in approval records.

---

## Context Budget

Default loading order:
1. quick-start or current stage summary
2. `project-state.json`
3. latest gate check
4. current artifact manifest
5. current handoff manifest
6. detailed references only if gate fails or ambiguity remains
