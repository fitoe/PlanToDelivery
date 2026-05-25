---
name: PlanToDelivery
description: Use when coordinating a project through Javis, 贾维斯, Hermes Kanban, delivery boards, cross-skill handoffs, review gates, active slices, provider cards, or automatic project continuation.
version: 3.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [javis, kanban, orchestration, project-delivery, gates]
    related_skills: [IdeaToTech, idea-to-design, design-to-code, kanban-orchestrator]
---

# PlanToDelivery — Kanban-Native Javis

## Overview

PlanToDelivery is the only project-level Javis orchestrator. Its job is to keep delivery moving through Hermes Kanban: recover state, choose the next active slice, create/claim/link/review cards, route specialist work, ingest evidence, unblock dependents, and report concise checkpoints.

It is not a design method, technical planning method, or implementation method. Specialist skills may decompose work inside their own phase, but Javis owns the board, gates, dependencies, canonical progress, and user-facing stops.

Canonical source project: `/home/imjzq/Projects/PlanToDelivery`.

## When to Use

Use this skill when the user says `贾维斯`, `Javis`, `P2D`, `PlanToDelivery`, `kanban`, `继续`, asks to resume/coordinate a delivery board, or asks multiple specialist skills to work in sequence.

Do not use it for a single local coding fix that does not need a project board, gate, or cross-skill handoff.

## Operating Principle

Default to a fast Kanban loop. Escalate only when risk demands it.

| Mode | Use when | Required constraint |
|---|---|---|
| `fast` | ordinary continuation, small UI/content/code slices | one clear card, acceptance, evidence, concise checkpoint |
| `controlled` | design approval, D2C parity, architecture/API boundary, multi-card dependency | explicit gate/dependency, required evidence, review result |
| `strict` | destructive/external side effects, disputed quality, audit, provider contract testing | envelope/digest/permit/prewrite/audit tools |

Do not make strict machinery the default. Do not bypass Kanban for gates.

## Core Loop

1. Recover board/project state from the known project state and Hermes Kanban before using chat memory.
2. Pick the smallest active slice that can move next.
3. Create or repair real Kanban cards for missing work, gates, and dependencies.
4. Decide `execution_mode`: fast, controlled, or strict.
5. Load exactly the specialist skill needed for the next card.
6. Give the specialist a bounded card contract: goal, scope, inputs, allowed changes, acceptance, required evidence, and review policy.
7. Ingest its result as evidence, not as automatic truth.
8. Move the card to done, review, blocked, or partial based on evidence.
9. Unlock the next dependent card and continue unless a hard stop applies.
10. Report a short checkpoint: done, current state, next action, blocker/gate if any.

## Card Contract

Every dispatch must be representable as a Kanban card, even in fast mode.

Minimum fields:

```yaml
type: design | tech | implementation | verification | gate | cleanup
goal: one outcome
scope: active slice only
inputs: artifact paths or concrete references
allowed_changes: files/areas/actions permitted
acceptance: observable pass conditions
evidence_required: artifacts/screenshots/tests/logs/review notes
suggested_skill: idea-to-design | IdeaToTech | design-to-code | other
review_required: true | false
execution_mode: fast | controlled | strict
```

Cards are the contract. Long provider envelopes are optional strict-mode artifacts, not the normal interface.

## Specialist Boundaries

| Need | Load | Boundary |
|---|---|---|
| product/design direction, visual source, design handoff | `idea-to-design` | creates design artifacts and review packets; does not implement |
| architecture, API/state/mock strategy, verification matrix | `IdeaToTech` | produces technical decisions; does not code |
| visual implementation from approved source | `design-to-code` | edits code and evidence for one visual slice; does not approve global gates |

Specialists may suggest new cards. Javis decides whether to create/link/claim/complete them.

## Gate Rules

A gate is required when the answer controls whether downstream work may start: scope freeze, product/content direction, visual-source approval, architecture/API decision, implementation-readiness, release/deploy, or user-confirmed acceptance.

Rules:

- Put gates in Kanban as review/approval cards with dependencies.
- Downstream cards must depend on the gate card, not on prose or local JSON.
- Match dependency edges to the exact artifact being approved: a plan/document gate may unlock the next design/visual artifact, but must not unlock implementation unless the user explicitly approved an implementation-ready artifact.
- For UI/visual work, implementation cards must depend on the final approved visual/source confirmation gate (for example `G3 visual approval`), not merely on D2 planning or implementation-document approval.
- Approval is not a stop by itself: after explicit approval, record evidence, complete/unblock the gate, then continue the next ready card.
- Homepage/global-shell approval releases only that scope unless the user explicitly approves a broader page-family gate.
- If scope shrinks or expands, create/repair the corresponding gate instead of pretending the old gate covers it.

## Visual-Draft Requests in Strong-Gate Projects

For strong-gate projects, user requests such as “生成视觉稿”, “出设计稿”, “重新开始”, “范围收缩”, “只做首页/Hero”, or “换一个方向” must be converted into Kanban scope/gate updates before any provider generates assets.

The orchestrator must:

- record the restart, replacement, or scope-change decision as board evidence;
- create or update the visual-source approval gate and dependency edges;
- dispatch `idea-to-design` with a bounded design card instead of generating images directly in the main chat;
- prevent D2C or implementation cards from depending on an unapproved generated draft;
- treat generated drafts as pending-review evidence until explicit user approval is recorded.

## D2C Controlled Path

Visual implementation is quality-sensitive. Use `controlled` by default for D2C unless the user explicitly asks for a rough spike.

Before implementation, the card must name:

- approved visual source or approved screenshot-as-source;
- target route/page/component;
- page/section contract or the requirement to create it first;
- allowed implementation files;
- screenshot/parity evidence expected;
- review requirement or explicit waiver.

For high-fidelity or disputed work, split the D2C slice into internal cards:

1. `visual-preflight`: source, page contract, page-level IR, top-risk section IR, asset inventory.
2. `visual-implementation`: code changes for the active page/slice.
3. `visual-parity-review`: screenshots, comparison, remaining debt, suggested fixes.

These are Kanban children, not a second orchestrator.

## Strict Mode Tools

Use strict mode only when needed. Canonical helpers live in `/home/imjzq/Projects/PlanToDelivery` and the installed skill scripts.

Typical strict checks:

```bash
PYTHONPATH=/home/imjzq/Projects/PlanToDelivery python3 /home/imjzq/Projects/PlanToDelivery/.agents/skills/plantodelivery/scripts/p2d_enforce.py audit --fail-on-violation
```

Use task envelopes, active-slice digests, execution permits, provider guards, and prewrite checks for audit-grade provider runs. If the strict path is incomplete or unavailable, downgrade only with an explicit user/project waiver; otherwise block the card with the missing enforcement artifact.

## Hard Stops

Stop for user input only when the next action requires a real decision or risk acceptance:

- destructive or irreversible side effects;
- secrets, tokens, passwords, credential persistence;
- unknown auth/permission for real external APIs;
- visual/product/content direction approval before downstream start;
- scope change that invalidates an existing gate;
- claiming completion without evidence or waiver.

Routine checkpoints, completed approvals, and non-destructive next cards are not stop points.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Turning every card into a provider contract | Use fast card contract by default; strict only when justified |
| Letting specialists update global progress | Specialists return evidence/suggestions; Javis updates board |
| Treating a design artifact as approval | Approval must be a Kanban gate or explicit recorded evidence |
| Treating D2 plan/document approval as implementation approval | Insert the visual/source confirmation task and gate first; implementation depends on that final gate, not D2 |
| Stopping after user says “可以/定稿” | Record approval and immediately continue the next unblocked card |
| Making D2C a second Javis | Allow local preflight/implementation/review cards only inside the visual slice |
| Broadening scope silently | Create a new gate/dependency for the new scope |

## Verification Checklist

- [ ] Active work is represented by real Kanban cards or an explicitly temporary fast card.
- [ ] Each gate that unlocks downstream work has a dependency edge.
- [ ] Only one project-level orchestrator is acting: Javis.
- [ ] Specialist output is evidence, not canonical progress until ingested.
- [ ] Execution mode is appropriate: fast by default, controlled for gates/visual quality, strict for audit/risk.
- [ ] User checkpoint states what moved, what is blocked/reviewing, and what continues next.
