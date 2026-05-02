# Feature Breakdown

## Status
- State: `draft`
- Last updated: 2026-05-02

## Current Context
- The repository currently focuses on landing the local `project-orchestrator` skill package itself.
- This breakdown therefore describes the skill package as the current delivery target.

## Feature Areas

### 1. Orchestrator Core Skill
- Purpose: Provide the top-level staged workflow and project-governance rules.
- User value: A future session can invoke one skill to govern planning, execution, verification, and recovery.

#### Core behaviors
- Determine the current stage before acting
- Enforce stage gates
- Route to the correct underlying skills
- Keep durable state in repository docs

#### Branch behaviors
- Handle greenfield projects
- Handle partially planned projects
- Handle partially implemented projects
- Handle interrupted sessions

#### Failure behaviors
- Fall back to `intake` when durable state is stale or contradictory
- Escalate when first-order decisions or plan validity are impacted

### 2. Reference Guidance Layer
- Purpose: Provide stage-specific operational guidance without bloating `SKILL.md`.
- User value: Progressive loading keeps context smaller while preserving detailed process rules.

#### Core behaviors
- Planning guidance
- Execution guidance
- Recovery guidance
- Change-control guidance
- Testing/security/observability/performance/integration guidance

### 3. Template Layer
- Purpose: Provide reusable structured documents for planning, execution, testing, and handoff.
- User value: Future sessions can generate consistent artifacts quickly.

#### Core behaviors
- Product/spec planning templates
- Milestone planning templates
- Testing and verification templates
- Security, data, deployment, observability, and integration templates
- Change/backlog and handoff templates

### 4. Repository State Layer
- Purpose: Store durable orchestration state under `docs/orchestrator/`.
- User value: Cross-session recovery does not depend on chat memory alone.

#### Core behaviors
- Session brief
- Current state and gap analysis
- Decision log and roadmap
- Milestone task state
- Backlog and skill registry

## Current Gaps
- Some optional reference/template files from the original broad design may still be unimplemented
- No end-to-end real-world trial run of the skill has been recorded yet

## Acceptance Notes
- The feature breakdown is sufficient for the current target only if it supports completing the skill package coherently
- If the repository later starts managing a separate real product, this file should be rewritten for that product
