# Standalone PlanToDelivery Installation

PlanToDelivery is designed to run as an external Hermes skill. It must not patch
or fork Hermes Agent. The runtime integration boundary is the public
`hermes kanban` CLI plus skill-bundled scripts/templates.

## Requirements

- Hermes Agent installed and on `PATH` as `hermes`.
- `hermes kanban` available in the installed Hermes version.
- Python 3.10+ for the skill scripts.
- Optional provider manifests for real dispatch; doctor treats missing provider
  contracts as a warning, not a hard install failure.

## Install the skill

Install from a skill URL or copy this skill directory into the active Hermes
skills directory:

```bash
hermes skills install <PlanToDelivery-SKILL.md-or-repo-url>
# or copy/sync .agents/skills/plantodelivery to ~/.hermes/skills/PlanToDelivery
```

Then start a new Hermes session or reload skills so the installed copy is loaded.

## Initialize a project board

From the target project root:

```bash
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_setup.py \
  --project-root . \
  --board plantodelivery \
  --write-state
```

This runs only public commands:

```bash
hermes kanban init
hermes kanban boards list --json
hermes kanban boards create plantodelivery --default-workdir "$PWD"
```

No Hermes Agent source files are changed.

## Doctor check

```bash
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_doctor.py \
  --project-root . \
  --board plantodelivery
```

Doctor verifies:

- `hermes` exists on `PATH`;
- `hermes kanban --help` works;
- Kanban storage can initialize;
- board JSON can be read;
- the target board exists;
- provider manifests/registry are discoverable when present.

## Isolated smoke test

Use an isolated temporary `HERMES_HOME` to verify the integration without touching
the user's real board:

```bash
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_smoke.py --project-root .
```

The smoke test creates a temporary board, creates a P2D_META card, claims it,
completes it, and checks that the final Hermes Kanban status is `done`.

## Enforcement wrapper

For real PlanToDelivery execution, do not let providers call `hermes kanban complete`
directly. Use the skill wrapper so claim/result/review/audit are enforced before a
card can move forward:

```bash
# Provider must claim/start before writing a result
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_enforce.py \
  --project-root . --board plantodelivery claim <p2d-task-id> --ttl 3600

# Provider result manifests are accepted only while the card is running
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_enforce.py \
  --project-root . --board plantodelivery ingest project-state/kanban/tasks/<p2d-task-id>/result-manifest.json

# Review-required results stay blocked at the Hermes card level until approved
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_enforce.py \
  --project-root . --board plantodelivery approve <p2d-task-id> \
  --evidence "reviewed screenshot/parity report"

# CI/checkpoint audit: fails non-zero with --fail-on-violation
python ~/.hermes/skills/PlanToDelivery/scripts/p2d_enforce.py \
  --project-root . --board plantodelivery audit --fail-on-violation
```

Current strict gates:

- missing or conflicting `P2D_META` markers are audit violations;
- result ingest is rejected unless the Hermes card status is `running`;
- `review_required=true` writes the result manifest and comments `P2D RESULT READY FOR REVIEW`, then blocks the card as a review gate instead of completing it;
- review approval requires non-empty evidence and comments `P2D REVIEW APPROVED` before completing the Hermes card;
- manually completed cards without result manifests are audit violations.

## Runtime mode

Real PlanToDelivery/Javis execution has one supported backend:

- `state_backend="hermes"`: mandatory execution gate. Hermes Kanban owns lifecycle;
  P2D JSON files are semantic overlays, task envelopes, result manifests, and
  evidence/debug exports.

`state_backend="json"` is intentionally rejected by `KanbanOrchestrator` for real
execution. Use `KanbanStateStore` only in explicit unit tests, migration/export
scripts, or evidence inspection tools; it is not a no-board compatibility mode.

## Independence contract

Do:

- Depend on stable public CLI behavior: `hermes kanban init`, `boards`, `create`,
  `show`, `claim`, `complete`, `block`, `link`.
- Keep P2D metadata inside Markdown-safe `P2D_META` markers in card body/comment.
- Keep provider routing capability-first.
- Ship doctor/setup/smoke scripts with the skill.

Do not:

- Import private Hermes Agent modules from the skill runtime.
- Modify Hermes Agent source code during install.
- Add custom Hermes Kanban columns or project-local lifecycle DB fields.
- Treat P2D JSON status as the authority for execution gates.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `hermes: command not found` | Install Hermes Agent and ensure its bin directory is on `PATH`. |
| `hermes kanban` missing | Update Hermes Agent to a version with Kanban support. |
| Target board missing | Run `p2d_setup.py --board <name>`. |
| Provider contracts missing | Add provider manifests/registry before real dispatch; smoke tests can still run. |
| Need safe verification | Run `p2d_smoke.py`; it uses an isolated temporary `HERMES_HOME` by default. |
