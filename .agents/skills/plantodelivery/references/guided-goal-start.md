# Guided Goal Start

Use this reference when the user wants to start a project simply, without first writing a full goal or choosing a workflow.

## User Entry Points

Treat these as equivalent guided-start triggers:

- `P2D，开始这个项目`
- `P2D，帮我启动这个项目`
- `P2D，给这个项目生成 goal 并开始`
- `PlanToDelivery，开始`
- a similar request to brainstorm, generate a goal, and execute

The user does not need to mention goal contracts, project-state, Visual IR, or specialist skills.

## Core Behavior

Guided Goal Start is a short decision funnel:

1. Restore or inspect project context.
2. Ask for the project goal if missing.
3. Classify the project profile and delivery mode.
4. Brainstorm only direction-level choices.
5. Offer 2-3 flow options with a recommendation.
6. Ask for user approval or choice.
7. Generate goal and project-state artifacts.
8. Start the first active slice.

Do not stop after generating the goal unless the user explicitly asks to stop. A generated goal is the start contract for execution, not the final deliverable.

## Question Discipline

Ask one question at a time.

Prefer not to ask when the answer can be safely inferred from:

- repository structure
- existing state files
- README or docs
- package/config files
- current user request

Ask only for:

- missing project objective
- direction-level product or visual choice
- flow approval
- destructive or irreversible actions
- secrets/auth/permission facts
- user approval for binding visual sources
- explicit waivers for gates or verification

## Minimum Intake

Inspect enough to answer:

- What is the project?
- Is there existing durable state?
- Is this UI-bearing?
- Is high visual fidelity required or likely?
- Is product direction clear?
- Is technical/API/state uncertainty meaningful?
- What is the lightest delivery mode that controls risk?
- What is the first deliverable slice?

Avoid broad scans when a compact answer is enough.

## Flow Options

Present 2-3 options in plain language:

1. Recommended flow: controls the main risk with the least process.
2. Lighter flow: faster, with named risks or waivers.
3. Stricter flow: more gates, useful when rework cost is high.

If the correct path is obvious and low risk, present the recommendation and ask for confirmation instead of over-explaining.

## Artifact Generation

After flow approval, create or update:

- `project-state/goal-contract.md`
- `project-state/goal-prompt.md`
- `project-state/flow-profile.json`
- `project-state/current-state.md`
- `project-state/active-slice.json`
- `project-state/artifact-manifest.json`
- `project-state/gates.json`
- `project-state/verification-ledger.md`

Use templates when available:

- `templates/goal-contract-template.md`
- `templates/goal-prompt-template.md`
- `templates/flow-profile-template.json`
- `templates/active-slice-template.json`
- `templates/project-state-template.json`
- `templates/artifact-manifest-template.json`

## UI High-Fidelity Default

When the project is UI-bearing and high fidelity matters, include this route unless the user waives it:

```text
PlanToDelivery
-> idea-to-design
-> GPT Image 2 or equivalent page-level visual source
-> user approval
-> Visual Freeze
-> Post-Visual Extraction
-> IdeaToTech if API/state/behavior decisions matter
-> design-to-code
-> Playwright screenshot/section diff
-> parity repair or handoff
```

Hard gates:

- No approved or waived visual source means no high-fidelity design-to-code implementation.
- Approved UI mockups are binding unless the user explicitly chooses directional-only implementation.
- Visual Freeze and Post-Visual Extraction must complete before visual fidelity implementation.
- Visual parity claims require screenshot-to-source or section-level evidence unless waived.

## Execution Handoff

After artifacts are created:

1. State the selected flow and first active slice.
2. Record any assumptions and waivers.
3. Move into the first active slice.
4. Load only the specialist skill needed for that slice.

Do not run another broad brainstorming loop unless the user changes direction or the first gate is blocked.

## Common Failures

| Failure | Fix |
|---|---|
| Asking the user to write a full prompt | Ask for the goal, then generate the prompt yourself |
| Explaining every internal artifact before starting | Hide mechanics unless the user asks |
| Stopping after goal generation | Continue into the first active slice |
| Asking many questions at once | Ask one decision-level question at a time |
| UI work skips visual approval | Block D2C until approval, waiver, or equivalent visual source exists |
