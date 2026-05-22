# Gap Analysis

## Target State
The repository should support a durable `plantodelivery` workflow that can:

- understand the real project scope
- manage milestone-based planning
- resume across sessions
- drive implementation with strong gates and verification
- coordinate capability-based providers without hard-coding provider internals
- hand review-required results back to the user as explicit approval packets

## Current State
- Orchestrator skill package exists under `.agents/skills/plantodelivery/`.
- Runtime enforcement exists in `plantodelivery/kanban_runtime.py`.
- Hermes Kanban wrapper scripts exist for setup, doctor, and enforcement.
- Runtime tests cover the existing Kanban state store plus the new provider doctor, alias, approval packet, and resume snapshot helpers.

## Closed Gaps

### Closed: Provider Doctor
- Added runtime-level structured provider diagnostics via `diagnose_provider_registry(...)`.
- Added `p2d_doctor.py --required-capability` so provider readiness can fail before dispatch instead of becoming an execution-time surprise.

### Closed: Project Alias Registry
- Added `p2d-project-aliases/v1` helpers to write, load, normalize, and resolve project aliases.
- Unknown aliases now raise `KanbanContractError` instead of silently guessing a project root.

### Closed: Approval Packet
- Added `p2d-approval-packet/v1` builder/validator for review-required provider results.
- Added `p2d_enforce.py approval-packet` to write a user-facing packet with changed files, artifacts, evidence, debts, blockers, and approval options.

### Closed: Resume Snapshot
- Added `p2d-resume-snapshot/v1` to summarize review, blocked/failed, running, and ready tasks.
- Added `p2d_enforce.py resume` for cold-session continuation evidence.

## Remaining Gaps

### Gap 1: Real-project Trial Friction
- Status: open
- Impact: Unit/runtime coverage cannot prove the end-to-end human workflow is pleasant under a live project.
- Next action: run one real project milestone through canonical Hermes Kanban and record friction in `docs/orchestrator/backlog.md`.

### Gap 2: Packaging Metadata
- Status: accepted for local workflow
- Impact: root `pyproject.toml` is absent, so this is not yet a clean installable Python package.
- Next action: add package metadata only if/when PlanToDelivery needs distribution outside the local skill/source workflow.

### Gap 3: Provider Ecosystem Fixtures
- Status: open
- Impact: doctor can validate required capabilities, but the repo does not ship canonical provider fixture manifests for every downstream provider repo.
- Next action: keep provider manifests owned by provider repos; add examples only if needed for onboarding tests.

## Recommended Next Stage
- `M1`: real-project trial use with provider doctor + approval packet + resume snapshot gates enabled.

## Recommended Next Actions
1. Use `p2d_doctor.py --required-capability ...` before dispatch.
2. Use `p2d_enforce.py approval-packet` for every review-required provider result.
3. Use `p2d_enforce.py resume` at cold-start/checkpoint boundaries.
4. Keep adding regression tests when trial use exposes workflow gaps.
