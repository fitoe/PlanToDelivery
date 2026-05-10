# Escalation Rules

Use this file when deciding whether work should continue autonomously or pause for user input.

## Escalate Immediately When

- user explicitly says pause/stop or changes direction
- project goal changes
- technology stack choice must change
- milestone acceptance becomes invalid
- core data model direction must change
- permissions/security boundary changes
- core UI structure changes materially
- a key external dependency changes the feasible solution
- the current milestone plan is no longer valid and cannot be repaired locally
- destructive or irreversible operations are required
- credentials, token, captcha, missing permission, or auth action is required from the user
- real production operation or user-data risk is present
- security, payment, privacy, or permission-boundary risk is present
- repeated verification failures have no new hypothesis or safe fallback
- the next action would conflict with an explicit user instruction
- final acceptance requires the user's approval

## Do Not Escalate By Default For

- second-order implementation detail
- local component split
- log naming detail
- narrow test structure decisions
- low-risk UI polish
- ordinary reuse-vs-library decisions with clear best answer
- missing optional preference where a safe convention exists
- non-blocking lint/type/test failures that can be recorded and deferred without invalidating the milestone
- choice between equivalent mature dependencies or existing project patterns
- incomplete future-scope functionality when current milestone can honestly mark it mock/pending/disabled
- page, component, or feature-slice ordering inside an approved milestone
- mock/local/demo fallback when real integration is blocked but visible/contract progress remains valuable
- successful checkpoint, commit, push, clean working tree, or passing verification

## Soft Blockers: Record And Continue

These should usually become debt/blocker notes, not user questions:

| Situation | Continue by |
|---|---|
| Real API unavailable, 401/403, timeout | Record auth/API blocker; switch to mock/local adapter or contract work |
| Non-core interface missing | Build visible shell and pending/disabled state; record integration gap |
| Lint/type failures unrelated to touched slice | Record baseline; run focused checks; continue |
| Minor visual edge state missing | Apply standard empty/loading/error; record visual-alignment debt |
| Implementation order unclear | Choose value-first order: visible/demo path, acceptance closure, real wiring, hardening |
| Equivalent dependency/pattern options | Prefer existing project pattern, then mature dependency; document assumption |

Soft blockers must be documented in task state, deferred work ledger, mock ledger, blocker list, or handoff notes.

## Autopilot Escalation Discipline

When the user asks for direct completion or uninterrupted execution:

1. Treat all non-escalation items as decisions to make, not questions to ask.
2. Continue through checkpoints automatically; checkpoint messages are progress reports, not permission requests.
3. Stop only for the immediate escalation list above, destructive actions that risk user data, credentials/verification codes, or an invalid hard gate that cannot be repaired autonomously.
4. If unsure whether to ask, default to: choose the safest reversible option, document it, continue.
5. Never end execution with routine A/B/C options while a safe next slice exists.
6. A completed slice, passing test/build, successful commit/push, or clean git state is not a stopping condition.

## Principle

Ask only when autonomy would risk wrong direction, data/user safety, irreversible change, or a hard gate that cannot be repaired. Do not ask when autonomy merely requires ordinary engineering judgment.
