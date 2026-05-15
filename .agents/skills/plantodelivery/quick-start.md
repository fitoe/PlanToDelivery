# Quick Start

Use this as the minimal reminder for `PlanToDelivery`. The authoritative rules are in `SKILL.md`.

## Startup Checklist

Before acting:

1. Verify project root and git status.
2. Read authoritative state in this order:
   - `project-state/execution-progress.json` + `project-state/artifact-manifest.json`
   - fallback: `.hermes/project-state/*`
   - legacy fallback: `docs/orchestrator/*`
3. Establish stage, current task/slice, owner skill, latest gate, blockers, next allowed action.
4. If anything is unknown or conflicting, inspect/repair state before implementation.

## Required Startup Output

```md
Session Start
- Project root:
- Stage:
- Current task/slice:
- Owner skill:
- Latest gate:
- Blocked reason:
- Next allowed action:
- Must update:
```

## Fast Path

Fast path is allowed only when authoritative state proves:

- current task is eligible
- dependencies are complete/skipped/waived with evidence
- required gates are passed/waived
- blockers are resolved/waived
- required user confirmations are approved/waived/not required

Low-token mode reduces reading volume, not rigor.
