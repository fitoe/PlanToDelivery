# Execution Contract

Use this file during `execution`.

## Purpose

Keep implementation aligned with approved planning while preserving speed, verification discipline, and autonomous completion after gates are open.

## Core Rules

- Execute against the active milestone spec and plan.
- Reuse existing code and dependencies before introducing new implementation.
- Follow TDD for new real behavior and bug fixes when it protects current scope.
- Keep scope frozen unless a valid escalation trigger occurs.
- Update durable state as work progresses.
- Use trust-first execution during active development: do not run full lint, full type-check, or full build after every small edit.
- Treat full lint, full type-check, and full build as Kanban checkpoint/review verification commands, not routine edit-loop commands.
- Expand verification at meaningful checkpoints or when high-risk foundations change.
- Use `software-development:project-execution-continuity` as the default sub-rule for chat/messaging execution, heartbeat updates, interruption handling, API preflight, and non-blocking fallback work.
- Continue one execution slice after another until the active milestone is complete, then enter verification and handoff without waiting for the user.
- If the user requested whole-project completion and roadmap/scope is known, after handoff immediately select or create the next milestone and continue unless a hard gate requires user input.
- Use checkpoint reports as status updates only; do not phrase them as stopping points or ask “要不要继续”.
- For reversible choices, choose the recommended option, record the assumption in task state/session brief, and proceed.
- Batch optional questions, polish ideas, and non-blocking uncertainties into the deferred work ledger or handoff notes.

## Autonomous Completion Loop

Run this loop whenever execution is open and the user asked to continue/complete directly:

```text
while active milestone is not done:
  choose next safest valuable slice
  execute the slice
  run narrow verification only when the slice reaches a meaningful checkpoint or a concrete risk signal appears
  classify blockers as hard or soft
  commit/push meaningful checkpoint when verified and appropriate
  update durable state, debt, blocker, and next-step records
  send compact progress or heartbeat
  continue to the next slice
```

If whole-project completion is explicitly requested:

```text
while project is not done:
  complete current milestone loop
  run milestone verification and handoff
  select next roadmap milestone or define the next milestone from approved scope
  continue unless a hard stop condition exists
```

## Next-Slice Selection Order

After every checkpoint, automatically pick the next item in this priority order:

1. unblock execution if a repairable gate/state mismatch exists
2. complete visible/demo path for the current milestone
3. close current milestone acceptance criteria
4. wire real functionality for current scope
5. verify and harden touched real behavior
6. burn highest-severity debt that blocks acceptance or safe continuation
7. update durable state and continue

Do not ask the user to choose between routine A/B/C options. Choose the safest, highest-value next slice yourself.

## Stop Conditions

Stop only for:

- explicit user pause/stop
- destructive or irreversible operation risk
- credentials, token, captcha, missing permission, or auth action that only the user can provide
- real production operation or user-data risk
- security, payment, privacy, or permission-boundary risk
- major product, UI, stack, scope, data-model, or acceptance change
- current plan or hard gate becomes invalid and cannot be repaired autonomously
- repeated verification failure with no new hypothesis
- conflict with explicit user instruction
- final acceptance when acceptance must be user-confirmed

These are not stop conditions by themselves:

- completed slice/page/component/test
- successful build/test/lint for touched scope
- successful commit or push
- clean git status
- context handoff or progress summary
- ordinary component split, page order, mock strategy, or focused test structure
- non-blocking lint/type/test failures that are classified and recorded
- unavailable non-core API when mock/local/contract work can continue honestly

## Soft Blocker Fallbacks

When a blocker does not invalidate current scope, record it and reroute:

- Real API unavailable/403/timeout: record blocker, switch to mock/local adapter, continue UI/interaction/contract work.
- Lint/type failures from existing baseline: record baseline, run focused check for touched files, continue current slice.
- Missing non-core design edge state: use standard loading/empty/error convention, record visual alignment debt, continue.
- High-risk functionality not required for current acceptance: mark pending/disabled/demo, continue lower-risk visible or interaction work.
- Non-core dependency uncertainty: prefer existing project pattern or mature dependency, document assumption, continue.

Soft blockers must be visible in task state, mock/debt ledger, or handoff notes. Never report downgraded mock/demo behavior as real completion.

## Verification Timing

During active editing, preserve implementation flow and trust model-generated local code unless a concrete signal shows breakage.

Do not run these commands as routine edit-loop checks:
- full lint
- full type-check
- full build
- broad regression or E2E suites

Run focused or full verification at these checkpoints:
- visual slice completion
- interaction slice completion
- functional slice completion
- milestone hardening
- merge readiness
- release or production-readiness review

Escalate verification earlier only for high-risk foundation changes:
- dependency manifests or lockfiles
- build, bundler, lint, test, or TypeScript configuration
- shared types, public APIs, routing foundations, or cross-module contracts
- auth, permissions, payment, security, privacy, data mutation, schema, migration, or persistence code
- broad refactors with cross-module blast radius

Before running a Kanban checkpoint/review command, do a quick self-check for obvious issues:
- unused imports or variables introduced by the current work
- unconnected functions, routes, or components
- unresolved placeholders in touched paths
- changed public contracts without matching consumers
- config or dependency changes that require expanded verification

If a Kanban constraint/evidence check fails, classify it before fixing. Current-scope blockers interrupt execution; unrelated baseline, environment, third-party, or deferred failures should be recorded and routed without hijacking the current layer.

## Allowed During Execution

- clarify plan-local detail by deciding it autonomously when reversible
- implement approved scope
- add tests
- run verification at meaningful checkpoints
- defer full lint, full type-check, and full build until Kanban checkpoint/review unless risk requires earlier escalation
- patch small mismatches between plan and repo reality
- use narrow browser validation for critical UI behavior when cheaper checks are insufficient
- send compact checkpoint or heartbeat updates while continuing work

## Not Allowed During Execution

- silent scope expansion
- silent architecture changes
- casual reopening of first-order decisions
- process sprawl
- hand-waving verification
- running full lint, full type-check, full build, or broad regression after every small edit without a Kanban checkpoint/review or risk trigger
- ending with routine options instead of continuing the obvious next safe slice
- treating commit/push/test-pass/clean-tree as completion when acceptance remains
- page code generation before UI section breakdown and `Pre-Implementation Brief` approval when those are required by the active UI gate
- page code generation before approved persisted implementation-reference images exist when UI gate requires them
- page code generation before section slice artifacts are written to disk when the blueprint/fidelity target requires them

## Browser Validation Rule

Use Playwright during execution only when it materially helps:

- confirm critical page behavior
- confirm key interaction slices
- reproduce browser-visible bugs early

Do not escalate every UI change into broad browser automation.

## Jarvis Progress Reporting Contract

Use this contract for project execution over Weixin/WeChat or any chat gateway where the user relies on status updates.

### Fixed states

Every progress report must include exactly one state label:

- `推进中`: editing files, generating assets, writing docs, implementing pages, fixing issues.
- `等待工具`: build/test/image generation/network/long command is running or being awaited.
- `汇报点`: a small phase just completed and is being summarized; this is not a stopping point.
- `阻塞`: user decision, credential, permission, captcha, destructive risk, or invalid hard gate blocks the next unsafe action.
- `已暂停`: only after the user explicitly says pause/stop/先别做.

### Required fields

Default structured report:

```text
状态：推进中 / 等待工具 / 汇报点 / 阻塞 / 已暂停
后台执行：是 / 否
过去 1 分钟完成：...
当前正在：...
下一步：...
下一次汇报：约 ... 后
```

If `后台执行：否`, also include:

```text
当前未后台执行：原因...
```

Never leave the user guessing whether the agent is still working or has stopped at a report point.

### Cadence

- When there is meaningful progress, send at most one merged progress report per 1-minute trailing-edge window.
- If there is no visible completion because a tool, build, image generation, network request, or deep debugging loop is still running, send a waiting heartbeat after it exceeds 2 minutes.
- Do not allow 5+ minutes of silence while work is still running. If platform delivery failed, the next successful message must briefly summarize the missed interval.
- Routine progress reports must include `下一次汇报`: normally about 1 minute later; for long tools, state that a waiting heartbeat will be sent if the wait exceeds 2 minutes.

### Weixin rate-limit behavior

If Weixin/iLink rate limiting or send failures appear:

- do not stop the project;
- do not retry noisy progress messages indefinitely;
- reduce frequency and merge updates;
- downgrade routine updates to an ultra-compact status bar when necessary;
- prioritize only hard blockers, phase completion, failures, and user-decision requests;
- after delivery recovers, send one compact recap of what happened during the limited period.

Ultra-compact fallback style:

```text
状态：推进中｜后台执行：是｜当前：...｜下一次：约1分钟后
```

### Report points and continuation

A report point is not a stop condition. After reporting, immediately continue to the next safest valuable slice unless a hard stop exists.

Completed slice, successful build/test, commit/push, clean git status, handoff note, or routine stage summary must not become “是否继续” prompts.

### Inserted user questions

When the user asks a mid-run question:

- simple progress/file/screenshot/explanation question: answer compactly, then resume the active queue;
- new requirement, direction change, pause intent, or major decision: switch state and confirm as needed;
- do not clear the execution queue just because an explanation was sent.

### Soft blocker handling

For soft blockers, retry or narrow the failure 1-2 times. If still blocked:

- record the issue in debt/TODO/blocker/handoff state;
- report impact scope;
- switch to the next safe task that can continue honestly;
- when reporting a blocker, also name alternative work that can still proceed.

Only hard blockers stop execution.

### Milestone and checkpoint behavior

- Git checkpoint, push, and clean worktree are not stop conditions.
- Development/implementation/verification milestones auto-continue after summary.
- Product/design/visual direction gates require user confirmation before crossing the direction line.
- While waiting for a design/visual confirmation, do only non-directional prep work such as docs, mocks, checks, debt cleanup, or next-plan preparation.

### Style modes

- Default: structured small summary.
- Rate-limited: ultra-compact status bar.
- Phase complete: short phase summary plus automatic next action when no hard stop exists.
