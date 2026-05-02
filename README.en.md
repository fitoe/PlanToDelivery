# PlanToDelivery

PlanToDelivery is a Codex skill product for disciplined software project delivery.

It is built around a local skill package, `project-orchestrator`, that helps move a software project from idea to implementation through:

- deep up-front planning
- milestone-based execution
- durable repository state
- built-in testing and verification discipline
- cross-session recovery
- controlled skill routing

## What It Is

PlanToDelivery is closer to:

- a project governor
- a workflow controller
- a recovery-oriented orchestration layer

and not a generic code autocomplete tool or a single long prompt.

## Repository Structure

- `.agents/skills/project-orchestrator/`
  - local skill package
  - references
  - templates
  - agent metadata
- `docs/orchestrator/`
  - durable workflow and recovery state

## Core Workflow

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

## Start Here

- Main Chinese README: [README.md](./README.md)
- Skill entrypoint: [`.agents/skills/project-orchestrator/SKILL.md`](./.agents/skills/project-orchestrator/SKILL.md)
- Workflow reference: [workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)

## Status

This repository already contains the first landed version of the product:

- local skill package
- core references
- core templates
- durable orchestration docs
- GitHub collaboration files

Next major step: trial use on real or simulated project workflows.
