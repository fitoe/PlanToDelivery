# PlanToDelivery

PlanToDelivery is a Codex project-governance product for skill users.

It is not a prompt dump or a one-shot script. It is a reusable delivery system that helps move a software project from planning to implementation, testing, verification, and handoff with durable state and controlled skill routing.

## Why it exists

Real projects usually fail for workflow reasons, not coding reasons:

- planning is too shallow
- UI, testing, and verification are not coordinated
- long conversations lose context
- new sessions cannot resume cleanly
- state lives in chat instead of the repository

PlanToDelivery turns those problems into a structured workflow.

## What it provides

- project intake and continuation
- deep planning and milestone slicing
- UI route planning and visual generation
- section-by-section page generation support
- browser validation with Playwright
- durable docs for recovery and handoff
- controlled extension with other skills

## Workflow

1. `intake`
2. `discovery`
3. `full-definition`
4. `ui-definition`
5. `decision-closure`
6. `roadmap`
7. `milestone-spec`
8. `milestone-plan`
9. `execution`
10. `debugging`
11. `verification`
12. `handoff`
13. `done`

## Start here

- Main README: [README.md](./README.md)
- Skill name: `PlanToDelivery`
- Skill entrypoint: [SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
- Workflow reference: [workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)

## Status

The repository already contains the first landed version of:

- `PlanToDelivery`
- core references and templates
- durable orchestration docs
- GitHub collaboration files

Next step: trial use on a real or simulated project.
