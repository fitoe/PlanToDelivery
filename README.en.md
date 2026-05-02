# PlanToDelivery

PlanToDelivery is a Codex skill product for disciplined software project delivery.

It is designed to help projects move from idea to implementation with:

- stronger up-front planning
- milestone-based execution
- durable repository state
- built-in testing and verification discipline
- cross-session recovery
- controlled skill routing

## Repository Contents

- local skill package under `.agents/skills/project-orchestrator/`
- reference guidance under `references/`
- reusable templates under `templates/`
- durable orchestration docs under `docs/orchestrator/`

## Product Positioning

PlanToDelivery is intended to behave more like:

- a project governor
- a technical lead
- a workflow controller
- a recovery-friendly orchestration layer

and less like a generic code autocomplete tool.

## Core Workflow

The orchestrator uses staged progression:

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

## Status

This repository contains the first landed version of the local skill package.

What remains next:

- trial use on real or simulated projects
- iterative refinement based on evidence

## Main Documentation

Chinese is the primary documentation language for this repository.

- Primary README: [README.md](README.md)
- Chinese alias: [README.zh-CN.md](README.zh-CN.md)
- Skill entrypoint: [.agents/skills/project-orchestrator/SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
