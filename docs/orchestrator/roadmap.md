# Roadmap

## Status
- State: `active`
- Last updated: 2026-05-22

## Current Milestones

### M0
- Name: `Orchestrator Adoption`
- Goal: Land a usable first-pass local `plantodelivery` skill package with durable repository state docs.
- User value delivered: Future sessions can load and iterate the skill package reliably.
- Dependencies: None
- Status: `done`

### M1
- Name: `Runtime Hardening and Trial Readiness`
- Goal: Make the local orchestrator/runtime safe for real-project trial use through provider diagnostics, aliases, review packets, and resume snapshots.
- User value delivered: P2D can be resumed and reviewed without relying on implicit chat context or provider-specific shortcuts.
- Dependencies: `M0`
- Status: `done`
- Delivered:
  - Provider doctor report: `p2d-provider-doctor/v1`
  - Project aliases: `p2d-project-aliases/v1`
  - Approval packets: `p2d-approval-packet/v1`
  - Resume snapshots: `p2d-resume-snapshot/v1`
  - Regression coverage: `tests/test_runtime_features.py`

### M2
- Name: `Real-project Trial Use`
- Goal: Run one project milestone through canonical Hermes Kanban using the hardened runtime gates.
- User value delivered: Discover and fix workflow friction under realistic planning, provider dispatch, approval, and checkpoint constraints.
- Dependencies: `M1`
- Status: `planned`

## Notes
- Further milestones should be defined after M2 trial use identifies remaining product/workflow gaps.
