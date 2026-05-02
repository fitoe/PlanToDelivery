# Escalation Rules

Use this file when deciding whether work should continue autonomously or pause for user input.

## Escalate Immediately When

- project goal changes
- technology stack choice must change
- milestone acceptance becomes invalid
- core data model direction must change
- permissions/security boundary changes
- core UI structure changes materially
- a key external dependency changes the feasible solution
- the current milestone plan is no longer valid

## Do Not Escalate By Default For

- second-order implementation detail
- local component split
- log naming detail
- narrow test structure decisions
- low-risk UI polish
- ordinary reuse-vs-library decisions with clear best answer

## Principle

Ask only when autonomy would risk wrong direction, not when autonomy merely requires judgment.
