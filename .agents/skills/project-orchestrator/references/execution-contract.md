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
  run narrow verification for touched behavior
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

## Allowed During Execution

- clarify plan-local detail by deciding it autonomously when reversible
- implement approved scope
- add tests
- run verification
- patch small mismatches between plan and repo reality
- use narrow browser validation for critical UI behavior when cheaper checks are insufficient
- send compact checkpoint or heartbeat updates while continuing work

## Not Allowed During Execution

- silent scope expansion
- silent architecture changes
- casual reopening of first-order decisions
- process sprawl
- hand-waving verification
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

## Messaging / Heartbeat Rule

For Weixin or other chat execution:

- send compact checkpoints at meaningful verified slices;
- send a heartbeat every 3-5 minutes during long work;
- if the user asks a question mid-run, answer compactly and resume the queue unless they explicitly pause/stop/change direction;
- do not spam every file edit or command.
