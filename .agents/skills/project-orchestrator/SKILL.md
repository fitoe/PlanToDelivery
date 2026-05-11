---
name: PlanToDelivery
description: Use when the user wants an end-to-end project manager skill that can take a new, half-built, or partially planned software project from planning through implementation, testing, verification, and handoff with strong process control, milestone-based execution, cross-session recovery, controlled skill routing, and minimal user interruption.
compatibility: Works with Codex and other agents that support the SKILL.md-based Agent Skills format and progressive loading from bundled references and templates.
metadata:
  author: fitoe
  version: "0.1.0"
---

# PlanToDelivery

Coordinate a software project from idea to completed milestone or completed project closure.

This skill is a project governor, not a universal implementation brain. Control stage transitions, enforce gates, route to the right skills, keep durable project state in repository documents, and minimize interruption after planning is complete.

## Core Principles

- Plan deeply up front. Reduce execution-time drift.
- Complete one closed milestone at a time. If scope is too large, split it.
- For UI-heavy projects, default to visible-first delivery: visible shell first, mock interactions second, real functionality in phases, hardening last.
- When functionality is large and phased, visual coverage may lead functional coverage. Functional deferral should change capability, not visibility.
- Use the operating motto: visible first, demo path first, mock honestly, wire functionality in phases, harden only what is real.
- For Vue/Vite/uni-app H5 projects that enable the progress overlay, keep `public/orchestrator/project-progress.json` current before reporting checkpoint progress.
- Each execution slice should produce user-visible progress unless invisible work is a blocker for that visible progress.
- Mock honestly: marked mock/demo/placeholder states are acceptable; fake completion is not.
- Do not let non-blocking lint, test, type, integration, or polish loops prevent visible progress. Classify, record, and defer non-blockers.
- User confirms only first-order decisions. Lower-order decisions default to recommended options unless challenged.
- Autonomous Completion Contract / 连续交付执行契约 is the default execution mode after the user says “贾维斯继续/完成/推进/不要停/直接完成这个项目”: keep executing the next safest valuable slice until the active milestone is done; if whole-project completion is explicitly requested and the roadmap/scope is known, continue milestone by milestone until project closure.
- Checkpoints are status updates, not stopping points. A completed slice, passing test/build, successful commit/push, clean git status, context handoff, or routine stage summary is never by itself a reason to stop or ask “是否继续”.
- No option-ending in execution: do not end with “下一步可以 A/B/C” for routine choices. Select the best next slice yourself, state it briefly, and immediately continue unless a hard stop condition exists.
- During autopilot, make reversible implementation decisions yourself, record assumptions/deferred questions in durable state, and keep moving. Batch non-blocking questions into checkpoint/handoff notes instead of interrupting execution.
- Soft blockers do not stop the project: classify them, record debt/blocker evidence, downgrade or reroute to mock/local/demo/placeholder/contract work when honest, then continue visible or acceptance-closing progress.
- User mid-run questions are interrupt communication, not queue cancellation. Answer compactly and resume the active execution queue unless the user explicitly says pause/stop/change direction.
- Progress reports must use the Jarvis progress-reporting contract: every progress update includes `状态`, `后台执行`, recent progress, current work, next step, and next expected report time. If no background work is running, explicitly state `当前未后台执行` and why.
- For Weixin/WeChat project execution, use a 1-minute trailing-edge progress window for meaningful progress, send a waiting heartbeat when long tools/debugging exceed 2 minutes without visible output, and reduce to shorter merged status bars after rate limiting. Never allow 5+ minutes of silence while work is actually running unless the platform is failing and the next successful message summarizes the gap.
- Hard stops only: explicit pause/stop; destructive or irreversible operations; credentials/token/captcha/permissions needed; production operations or user-data risk; security/payment/privacy/permission boundary risk; major product/UI/stack/scope/acceptance change; invalid hard gate that cannot be repaired autonomously; repeated verification failure with no new hypothesis; conflict with explicit user instruction; final acceptance.
- Prefer existing code and existing dependencies over new code. Prefer mature libraries over custom implementation.
- Do not load all references at once. Read only what the current stage needs.
- Start with `quick-start.md`; use `references/orchestration-core.md` before detailed orchestration references.
- Use `templates/index.md` before opening individual templates.
- Repository state is source of truth. Git is cross-check, not sole memory.
- No completion claims without fresh verification evidence.
- `PlanToDelivery` owns orchestration and gates; specialized skills own their domain workflow.
- Do not duplicate `idea-to-design` or `design-to-code` workflows inside orchestration logic.
- Orchestration depends on artifacts and gate evidence, not on a specific skill implementation.
- `idea-to-design` and `design-to-code` are recommended owners, not exclusive dependencies.
- `IdeaToTech` is the recommended owner for implementation-ready technical blueprints: dependency decisions, feature recipes, API/state/mock plans, and verification matrix.
- For UI implementation, prefer the new post-visual blueprint handoff: `idea-to-design` produces `implementation-blueprint.json`, `page-matrix.json`, `component-blueprint.json`, and `debt-ledger.json` only after Visual Freeze and Post-Visual Extraction; `IdeaToTech` produces `technical-decisions.json`, `feature-recipes.json`, and `verification-matrix.json`; `design-to-code` consumes both packages before coding.
- Prefer artifact-driven coordination: manifests, approval records, gate checks, and handoff manifests.

## First-Order Decisions

Require explicit user confirmation for:

- Project goal
- Product interaction direction
- Technology stack
- UI style direction
- High-risk testing priorities
- Final acceptance criteria

All other decisions default to orchestrator recommendations unless the user objects.

## Dependency-First Rule

During implementation, choose in this order:

1. Reuse existing project code
2. Reuse existing installed dependencies
3. Add a mature dependency if justified
4. Custom-build only as last resort

Only custom-build when:
- Existing code or dependencies are not suitable
- Adding a dependency creates disproportionate cost
- Security, performance, or maintainability clearly require custom code
- The needed behavior is tiny and direct implementation is simpler

## Stage Machine

Operate in these stages:

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

Always determine current stage before acting.

## Visible-First Delivery Semantics

Use these layered completion states for UI-heavy projects:

- `Visual Complete`: page is reachable, layout and approved visual structure are present, mock data fills the UI, and no visible blocker prevents review. For binding visual sources, route reachability or smoke success alone is not visual completion; screenshot-to-source parity must show the approved page type, module order, card anatomy, density, and action hierarchy are preserved or deviations are recorded.
- `Interaction Complete`: key clicks, navigation, local state, demo flows, loading/empty/error visuals, and feedback are usable without requiring real backend completion.
- `Functionally Complete`: real data, APIs, permissions, persistence, business rules, and true submissions work for the current milestone scope.
- `Hardening Complete`: required full verification, regression, refactor, performance, accessibility, documentation, and release checks are done.

Visual-first does not skip design approval. It starts only after UI scope and visual source are approved enough for the current slice.

Select delivery mode explicitly when planning or entering execution:
- `visual-first`: UI-heavy apps, admin systems, dashboards, mobile/H5 products, or projects where early dev review matters.
- `function-first`: APIs, libraries, CLIs, backend-only features, or computation-heavy work.
- `risk-first`: payment, auth, permissions, destructive operations, security-sensitive, or data-loss-sensitive work.
- `compliance-first`: migration, regulated data, audit, production release, or formal acceptance work.

Maintain lightweight status artifacts when visible-first mode is active:
- Status Matrix: page/module rows with Visual, Interaction, Mock, Real, Hardening, Next.
- Mock Ledger: mock area, current behavior, replace stage, and real source.
- Deferred Work Ledger: item, reason, severity, revisit stage, and owner.

Mock is planned delivery only when it is explicit. Never report mock, demo, pending, disabled, or placeholder behavior as real functionality.

Use demo mode deliberately when useful: mock identity, mock data, no production API, and simulated submissions. Demo mode must have an exit condition before functional wiring, release, or production integration.

For feature-rich UI projects, visual completeness may intentionally exceed functional completeness. Page shells, navigation, placeholders, mock interactions, and pending states may cover the broader product blueprint while real functionality is delivered by milestone.

Use these safety rules:
- Visual-first does not replace design approval.
- Mock-first does not mean fake complete.
- Placeholder is valid delivery when marked and planned.
- Hidden functionality requires a recorded reason; functional deferral should change capability, not visibility.
- After Visual Freeze, functional work may fix visual blockers but must not redesign page structure without a change request.
- Hardening stabilizes committed scope; it must not add new feature or visual scope.
- Assess each checkpoint only against its declared layer.

- Before each execution checkpoint, report: Visible progress, Interaction progress, Functional progress, Deferred, and Next.
- For UI checkpoints with approved/binding visual sources, explicitly label design parity separately from route/smoke status: `route reachable`, `interaction smoke`, `design parity PASS/WARN/FAIL`, and `visual debt`. Do not merge these into a single “done” claim.

If the Vue Progress Overlay is enabled for the target project, update the overlay JSON before the checkpoint report:
- template source: `templates/progress-overlay/project-progress.template.json`
- Vue component source: `templates/progress-overlay/vue/DeliveryProgressOverlay.vue`
- target JSON path: `public/orchestrator/project-progress.json`
- target component path: `src/components/DeliveryProgressOverlay.vue`
- detailed guide: `references/vue-progress-overlay.md`

## Required Workflow

### Session Start

At the start of every session, run `quick-start.md`.
Use `references/session-start-protocol.md` only when startup recovery, conflicting state, or resume rules need detail.
Do not act on the user's latest request until current stage, owner skill, gate status, and next allowed action are known.

### 1. Intake

Use this stage when:
- Project already has planning docs
- Project already has partial code
- User wants to continue a half-finished effort
- Project may already have `superpowers:brainstorming` outputs

Actions:
- Inspect existing docs and code
- Build `current-state.md`
- Build `gap-analysis.md`
- Decide whether project can:
  - continue directly
  - continue after patching missing planning
  - must be re-planned materially

Do not discard existing planning by default. Prefer patching over rewriting.

### 2. Discovery

Clarify:
- project goal
- users
- scenarios
- non-goals
- success criteria
- scope boundary

If project is too large for one closed build, prepare to split into milestones.

### 3. Product Definition

Lock the product and interaction model before any system design or implementation:
- feature inventory
- primary flows
- branch flows
- error flows
- page inventory
- route responsibilities
- empty/loading/error states
- validation
- acceptance criteria
- component boundaries
- interaction rules
- change rules that affect user-facing behavior

Do not stop at feature names. Push to behavior and interaction detail.

### 4. UI Definition

If project has UI, do both tracks in parallel:
- structural track: IA, pages, flows, states, components
- visual track: 2-3 style directions for user approval

Use this stage only after the product and interaction definition is concrete enough to render.

For product design, page planning, design documentation, visual direction, or staged design images, route to `idea-to-design`.
`PlanToDelivery` validates that required design artifacts exist and are approved; it does not replace the `idea-to-design` workflow.

If this is a new project with meaningful UI, the visual track is mandatory before page implementation:
- generate 2-3 small inspiration frames with `imagegen`
- save those inspiration frames to repository docs, not only in chat
- present them to the user for confirmation
- do not generate large implementation-reference images until one inspiration direction is approved
- after approval, generate the larger implementation-reference images and save them to repository docs
- do not begin page coding until the implementation-reference images are approved
- do not enter execution for UI-bearing work until design images are produced and approved

For `gpt-image-2` page effect generation, apply the following rules:
- one page at a time
- every page must go through `small -> large -> prompt`
- `small` means 2-3 same-page, materially different style directions for exploration only
- `small` must not combine multiple routes in one image
- every generated `small` and `large` image must be persisted, including unselected versions
- the approved `large` image must be persisted with a structured prompt artifact that is intended for reproduction, not human readability
- the prompt artifact must be version-bound to the approved `large` image
- section slicing is required only for complex pages
- simple mobile pages or lightweight web pages may use fewer slices or no slices
- when slicing is required, do not cut directly from semantic guesswork; first produce a conservative slice preview with forbidden zones, candidate boundaries, merge decisions, and final slice ranges
- when slicing is required, section boundaries and order must be confirmed from the preview before any final slice artifacts are accepted
- any slice artifacts must be persisted and version-bound to the originating `large` image
- `small`, `large`, `prompt`, and `slice` artifacts must remain traceable to the same page and version
- do not discard historical image versions; preserve them for later reference and regeneration

If the project has UI and the visual direction is already confirmed, page implementation should prefer the Level 3 blueprint handoff first:
- `idea-to-design` prepares `implementation-blueprint.json`, `page-matrix.json`, `component-blueprint.json`, and `debt-ledger.json` as the low-context implementation entrypoint
- `design-to-code` starts from Blueprint Intake, then Foundation Pass, Coverage Pass, Refinement Pass, and Fidelity Pass
- broad route/page coverage may proceed from the blueprint without re-analyzing every design image
- section slicing is required only for complex pages, high-fidelity targets, or pages whose blueprint/visual contract requires it
- when slicing is required, use a conservative slicing protocol:
  - identify forbidden zones first: titles, CTA/button clusters, card bodies, hero/media focal areas, forms, and any section-theme center content
  - identify candidate safe bands second; prefer boundaries that pass through sparse buffer areas rather than semantic centers
  - allow `merge with previous`, `merge with next`, or `keep as one larger slice` when a safe boundary is unclear
  - prefer larger slices with overlap or safety margin over tight cuts that risk clipping content
  - generate a persisted preview artifact before accepting final section slices
- required section maps, briefs, and slice artifacts must be saved to repository docs before claiming `L4 core-fidelity` for that page
- implementation must follow the confirmed visual source and blueprint as the source of truth; briefs cannot re-design the UI

For page-oriented work, persist UI artifacts under repository docs:
- inspiration images
- implementation-reference images
- section map
- section slice records
- `Pre-Implementation Brief`

Persistence rules:
- persisted UI artifacts must live inside the project repository, not under `.codex/`, user-home temp folders, or chat-only state
- if a tool first writes to `.codex/` or another temporary workspace, copy the final approved artifacts into repository paths before treating the gate as satisfied
- repository-relative paths must be recorded in the related docs so later sessions can reopen the exact files without depending on `.codex` state

Default artifact locations:
- `docs/orchestrator/ui/inspirations/`
- `docs/orchestrator/ui/references/`
- `docs/orchestrator/ui/sections/`
- `docs/orchestrator/ui/`

Rules:
- core pages high fidelity
- secondary pages medium fidelity
- edge pages low fidelity
- core pages and core components require full state definition
- UI spec must be implementation-guiding, not decorative only

If project has no meaningful UI, skip this stage.

### 5. System Definition

Define system details only after product behavior and UI direction are fixed:
- permissions model
- data shapes
- state transitions
- interfaces
- architecture direction
- deployment assumptions
- testing strategy
- observability expectations
- external integrations

Do not let system design redefine approved product behavior or approved UI.

### 6. Decision Closure

Before roadmap or implementation, close all high-impact unresolved decisions:
- stack
- architecture direction
- product interaction direction
- UI direction
- data model direction
- permissions model
- testing strategy
- milestone slicing
- acceptance rules

If the user says "先生成 ui 效果图，确认了再实施" or equivalent:
- stay in `ui-definition` and `decision-closure`
- do not enter execution
- do not write page code
- require approved implementation-reference images or equivalent visual sources plus a valid Level 3 blueprint package before broad implementation starts
- require confirmed section slices and page briefs only for pages whose complexity or fidelity target needs them

Do not enter implementation with open high-impact decisions.

### 7. Roadmap

Split project into milestones.

Prefer:
- user-value closed loops first
- technical split only when value-loop split is impossible

Each milestone must be independently spec-able, executable, testable, and handoff-able.

### 8. Milestone Spec

Create full spec for the current milestone.

### 9. Milestone Plan

Create detailed implementation and testing plan for the current milestone.

After entering `milestone-plan`, scope freezes by default.

### 10. Execution

Execute the current milestone plan with:
- visible-first priority for UI-heavy work
- TDD where it protects current real functionality
- review gates
- verification gates sized to the current layer
- controlled progress
- durable state updates

For UI-heavy milestones, execute in this order unless a blocker requires otherwise:
1. `visual-shell`: pages/routes, layout, visual structure, mock data, placeholders, and visible states. When a Level 3 blueprint package exists, route to `design-to-code` for Foundation Pass and Coverage Pass first.
2. `interaction-shell`: clicks, local state, mock flows, loading/empty/error visuals, and demo path feedback. Use Refinement Pass outputs and page maturity updates to choose what to deepen.
3. `functional-wiring`: real APIs, adapters, persistence, permissions, business rules, and true submissions for the current milestone.
4. `hardening`: full verification, regression, refactor, performance, accessibility, release checks, and debt burn-down.

Map blueprint-driven `design-to-code` maturity to delivery layers:
- `L0 route-ready` and `L1 skeleton-ready` contribute to visual-shell progress.
- `L2 content-ready` and `L3 system-styled` can satisfy broad non-core visual coverage when mock/fallbacks are honest.
- `L4 core-fidelity` is required before claiming core page visual acceptance.
- `L5 functional-ready` contributes to functional completion only when real behavior is in scope.

Feature-rich projects may implement broad visual coverage before broad real functionality. Unimplemented features should remain visible as marked mock, disabled, pending, demo, or placeholder states instead of disappearing.

After entering `execution`, scope remains frozen except for blocking or validity-breaking changes.

### 11. Debugging

If blocked by failing behavior, use systematic debugging. Do not guess-fix.

### 12. Verification

Run milestone acceptance, targeted regression, and required cross-checks. Use fresh evidence only.

### 13. Handoff

Update durable state files:
- task state
- session brief
- verification status
- next step
- blockers
- persistent processes

### 14. Done

Mark done only when:
- acceptance criteria satisfied
- verification evidence is fresh
- state files are current
- remaining backlog is explicitly categorized

## Hard Gates

Do not allow implementation when any of these are missing:

- `product-spec.md`
- approved product/interaction definition
- `decision-log.md` resolved for high-impact items
- `roadmap.md`
- current milestone spec
- current milestone implementation plan
- current milestone test plan
- current gate check allows the transition
- artifact manifest and approval records satisfy any UI or implementation-specific gate

For UI-bearing projects, also require all of these before `roadmap` or `execution`:

- `docs/orchestrator/current-state.md` records `product_definition_status: approved`
- `docs/orchestrator/current-state.md` records `ui_design_status: approved`

For any UI page implementation based on an approved visual direction, prefer the Level 3 blueprint gate before `design-to-code` or page code generation:

- approved persisted implementation-reference images or equivalent visual sources
- recorded Visual Freeze approval for the visual source
- Post-Visual Extraction refreshed tokens, visual contracts, briefs, and blueprint files from the approved visual source
- `implementation-blueprint.json` with approved `visual_freeze_ref`
- `page-matrix.json`
- `component-blueprint.json`
- `debt-ledger.json`
- `visual-contracts/<page-id>.json` for binding core pages
- `design-to-code-inputs/manifest.json`
- `pre-implementation-briefs/<page-id>.md` where required by the blueprint or fidelity target
- checker-passing handoff evidence when an `idea-to-design` checker is available

Section breakdown, slice preview artifacts, and section slice artifacts are required when the blueprint, page complexity, or target fidelity says they are required. They must not block broad Foundation/Coverage work for simple pages or pages whose current target is only `L0-L3` maturity.

Do not allow implementation when design images or equivalent approved visual sources are not produced and approved.
Do not treat `.codex/`-only artifacts as produced/persisted; required UI evidence must exist under project paths.

If UI is not yet confirmed, do not enter execution for page implementation; return to `ui-definition` / `decision-closure` instead.
Do not use the text brief to reinterpret or replace the confirmed image design during implementation or acceptance.

Before moving from `ui-definition` toward `execution`, complete a gate check using `templates/gate-check-template.md`.

Do not mark work complete when any of these are missing:

- fresh verification evidence
- updated milestone task state
- updated `session-brief.md`

## Required Skill Routing

### Always activate first
- `superpowers:using-superpowers`
- `karpathy-guidelines`

### Planning
Use:
- `superpowers:brainstorming`
- `superpowers:writing-plans`

### Execution
Use selectively:
- `superpowers:using-git-worktrees` when isolation is needed
- `superpowers:subagent-driven-development` when the user allows delegation and tasks are independent
- `superpowers:test-driven-development` for real functional logic, business rules, and bugfixes where behavior must be protected

### Quality
Use:
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`

### Failure handling
Use:
- `superpowers:systematic-debugging`

### Completion
Use:
- `superpowers:finishing-a-development-branch`

### Skill creation / maintenance
Use:
- `superpowers:writing-skills`
- `skill-creator`

### Product and visual design
Use:
- `idea-to-design`

### Functional and technical implementation planning
Use:
- `IdeaToTech`

### Design image to code
Use:
- `design-to-code`

## UI Implementation Example

Example sequence for a confirmed UI project:
1. generate 2-3 small inspiration frames and save them to `docs/orchestrator/ui/inspirations/`
2. user confirms one direction for expansion
3. generate larger implementation-reference images or equivalent visual sources and save them to repository docs
4. route to `idea-to-design` for Level 3 handoff: `implementation-blueprint.json`, `page-matrix.json`, `component-blueprint.json`, `debt-ledger.json`, visual contracts, and design-to-code input manifest
5. run/record the handoff checker or equivalent gate evidence
6. route to `design-to-code` for Blueprint Intake -> Foundation -> Coverage -> Refinement -> Fidelity
7. use section slicing and detailed briefs only where required for complex/high-fidelity pages, then claim `L4 core-fidelity` only for verified core pages

### Optional extensions
Use only when relevant:
- `context7`
- `find-skills`
- `caveman`

## Controlled Skill Extensions

Additional skills may be registered and used, but only through controlled routing.

For `idea-to-design` and `design-to-code`, follow `references/cross-skill-contracts.md`.

If a required dependency skill is not installed or cannot be found:

- do not skip it silently
- first search the global skill installation source or registry
- if still unavailable, stop and ask whether to install it automatically before continuing

For each additional skill define:
- skill name
- use conditions
- allowed stages
- always-on or on-demand
- whether user approval is required

Read `docs/orchestrator/skill-registry.md` when present.

## Planning Discipline

Planning order for UI-bearing projects:
1. `discovery`
2. `product-definition`
3. `ui-definition`
4. `system-definition`
5. `decision-closure`
6. `roadmap`
7. `milestone-spec`
8. `milestone-plan`
9. `execution`

For UI-bearing projects, treat approved product behavior and approved UI as the source of truth. System design, milestone planning, and implementation must derive from them rather than redefining them.

Use two decision layers:

### Layer 1: user-confirmed
- project goal
- stack
- UI direction
- high-risk testing priorities
- final acceptance

### Layer 2: orchestrator-recommended
Everything else defaults to orchestrator recommendation unless the user objects.

This prevents planning from stalling on too many tiny decisions.

## Testing Discipline

Testing is risk-prioritized and layered.

Rules:
- every milestone has a written test plan
- prioritize both user-flow closure and high-risk lower-level modules
- use high-value coverage, not mechanical blanket coverage
- add E2E after main flows stabilize
- use smart regression based on impact and risk
- when tests fail, classify cause before fixing

Maintain milestone testing documents, not just test code.

## Change Control

New ideas do not interrupt current execution by default.

Default path:
- record in backlog
- classify into:
  - must handle now
  - next milestone candidate
  - future idea
  - explicitly not doing

Only escalate if change affects:
- project goal
- stack
- milestone acceptance
- core data model
- core permissions/security
- core UI structure
- key external dependency
- validity of current plan

Major changes require a written change request.

## Efficiency Rules

Move fast by reducing low-value loops, not by lowering quality.

Rules:
- front-load decisions, reduce execution churn
- run narrow tests during small development loops
- expand verification at task or milestone boundaries
- do not run full suites by default for every small change
- do not polish before core flow closes
- do not reload whole project context every session
- use `session-brief.md` as recovery entrypoint

## Process Management Rules

Avoid shell/process sprawl.

Rules:
- short commands run foreground only
- minimize long-lived processes
- reuse existing dev services when possible
- do not start duplicate servers/watchers
- record long-lived process purpose, command, and port
- clean up temporary processes before ending session unless they must persist

## Git And Branch Management

Use git to isolate work, not as the primary project memory.

Rules:
- keep `main` stable and merge only verified work into it
- use short-lived branches for each stage, milestone, or focused task
- prefer one branch per closed loop; delete it after merge
- keep branch names explicit, such as `docs/...`, `feat/...`, or `chore/...`
- for implementation work, prefer a dedicated worktree when parallel work or dirty state exists
- never overwrite or reset user changes without explicit instruction
- make small commits with one purpose each
- keep state/document edits separate from code or behavior edits when practical
- write durable project state into `docs/orchestrator/`, not only into commit history
- before merge or handoff, verify the current branch, changed files, and latest task state
- prefer squash merge for milestone work unless history preservation is important
- if the worktree is dirty on arrival, inspect and preserve existing changes before proceeding
- if a branch is no longer needed, remove it after merge and state sync

## Progressive Loading

Do not load every reference or template file at once.

Read in this order:
1. `SKILL.md`
2. on every session start, read `references/session-start-protocol.md`
3. determine current stage
4. read only stage-relevant files from `references/`
5. read only needed files from `templates/`
6. on new session, read `docs/orchestrator/session-brief.md` and `docs/orchestrator/project-state.json` first when present

For stage transitions, read:
- `references/cross-skill-contracts.md` when routing between skills
- `references/artifact-driven-workflow.md` when checking equivalent artifacts, approval evidence, or handoff manifests
- `references/vue-progress-overlay.md` when enabling or updating the Vue progress overlay
- `templates/gate-check-template.md` before allowing the transition
- `references/gate-enforcement-scenarios.md` when pressure exists to skip required planning, design, confirmation, or verification

## Repository State

Use repository docs as durable state.

Important files include:
- `docs/orchestrator/project-state.json`
- `docs/orchestrator/artifact-manifest.json`
- `docs/orchestrator/approval-records.json`
- `docs/orchestrator/handoff-manifest.json`
- `docs/orchestrator/product-spec.md`
- `docs/orchestrator/feature-breakdown.md`
- `docs/orchestrator/decision-log.md`
- `docs/orchestrator/roadmap.md`
- `docs/orchestrator/session-brief.md`
- `docs/orchestrator/current-state.md`
- `docs/orchestrator/gap-analysis.md`
- milestone-specific spec/plan/test/task-state files

Cross-check with git, but do not rely only on git history for recovery.

## Recovery Protocol

At the end of meaningful work, ensure durable state includes:
- current stage
- current milestone
- current task
- latest verification result
- blockers
- persistent process inventory
- next session first step
- any pending user confirmation

On new session:
1. read `session-brief.md`
2. read active milestone task state
3. read `decision-log.md`
4. read milestone plan/spec as needed
5. cross-check code, branch, and git status
6. continue from exact next step

## Output Standard

When guiding execution:
- say what stage project is in
- say why next action is allowed
- say which skill to use next
- say which durable files must be updated
- show the gate decision when moving between major stages
- cite artifact manifest or approval evidence when a gate depends on design or implementation readiness

Do not dump all process theory each time. Stay stage-specific and concise.
