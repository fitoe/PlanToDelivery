# Project Orchestrator

[![Repository](https://img.shields.io/badge/GitHub-fitoe%2FPlanToDelivery-181717?logo=github)](https://github.com/fitoe/PlanToDelivery)
[![Skill](https://img.shields.io/badge/Codex-Local%20Skill-10a37f)](./.agents/skills/project-orchestrator/SKILL.md)
[![Docs](https://img.shields.io/badge/docs-orchestrator-blue)](./docs/orchestrator/)

[简体中文说明](README.zh-CN.md)

`project-orchestrator` is a local Codex skill package for running software projects with stronger process control.

It is designed for long-running work that usually falls apart in execution: unclear scope, weak planning, incomplete testing, context loss between sessions, and constant mid-stream changes.

This repository currently contains:

- the local skill package under `.agents/skills/project-orchestrator/`
- durable repository-state docs under `docs/orchestrator/`
- planning, execution, testing, recovery, and handoff templates

## Table of Contents

- [What It Does](#what-it-does)
- [Core Design](#core-design)
- [Repository Layout](#repository-layout)
- [Quick Start](#quick-start)
- [How to Use the Skill](#how-to-use-the-skill)
- [Current Status](#current-status)
- [Intended Use](#intended-use)
- [Next Step](#next-step)

## What It Does

The skill acts as a project governor, not a generic code generator.

It helps manage a project through:

- intake of new or half-built projects
- deep up-front planning
- milestone-based roadmap slicing
- controlled implementation flow
- TDD and verification discipline
- cross-session recovery from durable docs
- change control, process control, and backlog control

## Core Design

The package is built around a staged workflow:

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

It also follows a few hard rules:

- front-load important decisions
- reuse existing code and dependencies first
- freeze scope once planning is complete
- store project state in repository docs, not only in chat context
- do not claim completion without fresh verification

## Repository Layout

```text
.agents/skills/project-orchestrator/
  SKILL.md
  agents/openai.yaml
  references/
  templates/

docs/orchestrator/
  session-brief.md
  current-state.md
  gap-analysis.md
  roadmap.md
  decision-log.md
  milestones/
```

## Quick Start

1. Open the repository in Codex.
2. Load the local skill at `.agents/skills/project-orchestrator/`.
3. Start from `docs/orchestrator/session-brief.md` if the repo already has state.
4. If the repo is new or half-built, begin with the orchestrator `intake` stage.

## How to Use the Skill

Minimum workflow:

1. Read `.agents/skills/project-orchestrator/SKILL.md`
2. Determine current stage
3. Load only the stage-relevant files from `references/`
4. Use the matching document templates from `templates/`
5. Keep state updated in `docs/orchestrator/`

Useful entrypoints:

- Skill entry: [SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
- Workflow guide: [references/workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)
- Routing guide: [references/skill-routing.md](./.agents/skills/project-orchestrator/references/skill-routing.md)
- Recovery entrypoint: [docs/orchestrator/session-brief.md](./docs/orchestrator/session-brief.md)

## Current Status

This repository currently contains the first-pass landed version of the skill package.

What is already in place:

- core `SKILL.md`
- stage-routing and gate references
- planning, testing, UI, security, observability, performance, and integration references
- a broad template set for durable project docs
- repository-level orchestration state scaffolding

What still needs real-world validation:

- trial runs on real or simulated projects
- iterative tightening based on actual use

## Intended Use

This package is meant for projects where you want Codex to behave more like a project manager + technical lead + execution controller, not just a coding autocomplete layer.

Typical fit:

- greenfield projects that need serious planning before coding
- half-built projects that need intake, gap analysis, and disciplined continuation
- long multi-session work where recovery and handoff matter

## Next Step

The next milestone for this repository is to trial the skill in a real or simulated workflow and refine it based on actual usage.
