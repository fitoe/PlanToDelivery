# Template Index

Use this index before opening individual templates. Load only the template needed for the current artifact.

## Session And Intake

- `project-state-template.json` - required when creating durable orchestrator state
- `current-state-template.md` - required for intake on existing or partial projects
- `gap-analysis-template.md` - required when current state has missing or stale planning
- `session-brief-template.md` - recommended for cross-session recovery and token saving

## Gate And Coordination

- `gate-check-template.md` - required before stage advancement
- `artifact-manifest-template.json` - required when multiple artifacts must remain traceable
- `approval-records-template.json` - required when user approval gates design or scope
- `handoff-manifest-template.json` - required for cross-skill or milestone handoff

## Product Planning

- `product-spec-template.md` - required for product definition
- `feature-breakdown-template.md` - required when scope must split into features
- `decision-log-template.md` - recommended for first-order decisions
- `roadmap-template.md` - required when planning multiple milestones
- `change-trigger-rules-template.md` - optional unless scope drift is likely
- `scope-freeze-rules-template.md` - optional unless user requests strict control

## Milestone Planning

- `milestone-spec-template.md` - required before milestone implementation
- `implementation-plan-template.md` - required before execution
- `milestone-test-plan-template.md` - required when milestone has meaningful behavior
- `task-state-template.md` - recommended during multi-session execution
- `verification-report-template.md` - required before completion claim

## UI And Design

- `ui-spec-template.md` - required for UI-bearing milestones
- `ui-style-directions-template.md` - required when visual direction is not approved
- `ui-visual-route-template.md` - required when tracking per-route visual artifacts
- `section-breakdown-template.md` - required before design-to-code on complex UI
- `pre-implementation-brief-template.md` - required before UI implementation
- `ui-implementation-contract-template.md` - recommended for handoff to code
- `progress-overlay/project-progress.template.json` - optional when enabling Vue progress overlay
- `progress-overlay/vue/DeliveryProgressOverlay.vue` - optional Vue/Vite/uni-app H5 floating progress overlay template

## Engineering And System

- `data-model-template.md` - required when persistent domain data exists
- `state-machine-template.md` - required when behavior has important state transitions
- `error-taxonomy-template.md` - recommended for non-trivial failure states
- `integration-contract-template.md` - required for external service integrations
- `env-vars-template.md` - required when runtime configuration matters

## Verification And Debugging

- `playwright-validation-template.md` - optional, use for browser-visible acceptance
- `playwright-debug-report-template.md` - optional, use for UI/browser defects
- `release-checklist-template.md` - required before release or final handoff
- `final-handoff-template.md` - required at project or milestone closure

## Strict-Only Or Domain-Specific

Use these only when the project domain requires them:

- Security: `security-baseline-template.md`, `security-test-plan-template.md`, `secret-management-template.md`, `input-output-protection-template.md`
- Permissions: `permission-matrix-template.md`, `auth-authz-template.md`
- Deployment: `deployment-plan-template.md`, `environment-plan-template.md`, `backup-recovery-template.md`, `healthcheck-template.md`
- Observability: `observability-plan-template.md`, `logging-spec-template.md`, `alerting-thresholds-template.md`, `event-instrumentation-template.md`, `ownership-visibility-template.md`
- Performance: `performance-plan-template.md`, `performance-strategy-template.md`, `performance-sensitive-paths-template.md`, `performance-validation-template.md`, `capacity-assumptions-template.md`
- Integrations: `integration-registry-template.md`, `integration-mock-strategy-template.md`, `integration-failure-strategy-template.md`, `integration-verification-template.md`
- Data and operations: `data-governance-template.md`, `migration-strategy-template.md`, `consistency-concurrency-template.md`
- Backlog and risk: `backlog-template.md`, `risk-matrix-template.md`, `change-request-template.md`
