# Orchestration Core

Use this file when deciding routing, artifact validity, stage gates, or cross-skill handoff. It is the compact entry for orchestration rules. Load detailed references only when this file is not enough.

## Owner Model

- `PlanToDelivery` owns stage control, gates, durable state, routing, and handoff.
- `idea-to-design` is the recommended owner for product design, route/page planning, design brief, visual directions, page images, and design documentation.
- `design-to-code` is the recommended owner for converting approved persisted design sources into high-fidelity implementation.
- Recommended owner does not mean exclusive source. Equivalent artifacts are valid if they satisfy the same gate evidence.

## Artifact Contract

Orchestration depends on durable artifacts, not on a specific skill implementation.

Valid equivalents include:

- `Design-Spec.md` or equivalent product/design document
- `state.json` or equivalent resumable design state
- approved design assets or equivalent persisted visual source
- approved section breakdown or equivalent implementation-ready page segmentation
- `Pre-Implementation Brief` or equivalent code-facing design brief

Artifacts must be repository-persisted. Chat-only output, temp files, and unrecorded tool output do not satisfy gates.

## Gate Rule

Each gate item is one of:

- `pass`: evidence exists and is current
- `fail`: required evidence is missing, stale, or contradicted
- `n/a`: item does not apply

Any `fail` blocks stage advancement. `unknown` should be treated as blocked until inspected or repaired.

Gate checks should name:

- stage
- required artifacts
- evidence paths
- decision
- next allowed action

## Startup Rule

At session start, decide before doing work:

- current stage
- current owner
- current gate state
- next allowed action
- durable evidence used

Prefer loading `quick-start.md`, project state, session brief, and latest gate evidence before detailed references.

## Blocking Scenarios

- Idea-only request to start coding: block. First produce product definition and implementation plan.
- UI coding with no approved persisted design source: block. Route to design or collect equivalent approved source.
- UI coding with design source but no section breakdown or brief: block. Produce the missing implementation-ready artifact.
- Approved image exists only in chat or temp folder: block. Persist it in the repository and record path.
- User asks to skip a gate: allow only after recording explicit approval and risk.
- Existing equivalent artifact exists: accept it if evidence satisfies the gate; do not force a specific skill rerun.

## Context Budget

Use this order to save tokens:

1. session brief and project state
2. latest gate check and approval records
3. compact orchestration core
4. stage-specific reference
5. exact template being written
6. historical docs only when there is a contradiction or missing decision

Do not read all references, all templates, or all historical artifacts by default.

## Speed Rules

- Do not re-ask confirmed first-order decisions.
- Do not re-run design or planning when equivalent approved artifacts exist.
- Do not expand a milestone beyond the closed scope.
- Use detailed references only when a gate, stage, or artifact is ambiguous.
- Prefer patching missing evidence over rewriting complete documents.
