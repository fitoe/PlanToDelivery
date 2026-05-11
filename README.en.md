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
- lightweight startup and progressive reference loading
- artifact-based contracts instead of hard coupling to one skill implementation

## Workflow

1. `intake`
2. `discovery`
3. `product-definition`
4. `ui-definition`
5. `system-definition`
6. `decision-closure`
7. `roadmap`
8. `milestone-spec`
9. `milestone-plan`
10. `execution`
11. `debugging`
12. `verification`
13. `handoff`
14. `done`

## Skill Collaboration

PlanToDelivery can orchestrate the broader workflow:

- `idea-to-design`: turns ideas into product structure, page planning, design docs, and visual assets
- `design-to-code`: turns approved persisted design sources into implementation and can plan missing image assets
- `PlanToDelivery`: owns stages, gates, durable state, verification, and handoff

These skills remain independently usable. PlanToDelivery accepts equivalent artifacts when gate evidence is sufficient, such as an equivalent design document, resumable state, approved visual source, or implementation brief.

## Lightweight Startup

Current startup is intentionally compact:

- start with `quick-start.md`
- read project state or session brief first
- use `orchestration-core.md` for routing, gates, and handoff decisions
- use `templates/index.md` before loading individual templates
- avoid loading all references by default

The goal is to keep recovery fast and token usage low while preserving full delivery controls.

## Start here

- Main README: [README.md](./README.md)
- Skill name: `PlanToDelivery`
- Quick start: [quick-start.md](./.agents/skills/plantodelivery/quick-start.md)
- Skill entrypoint: [SKILL.md](./.agents/skills/plantodelivery/SKILL.md)
- Orchestration core: [orchestration-core.md](./.agents/skills/plantodelivery/references/orchestration-core.md)
- Template index: [templates/index.md](./.agents/skills/plantodelivery/templates/index.md)

## Status

The repository already contains the first landed version of:

- `PlanToDelivery`
- core references and templates
- durable orchestration docs
- GitHub collaboration files
- lightweight startup, artifact contracts, and template index

Next step: trial use on a real or simulated project.
