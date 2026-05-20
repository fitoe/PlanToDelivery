# Javis Artifact Model v1

## 1. Principle

Artifacts are durable evidence and inputs. DB stores artifact indexes, versions, summaries, approval state, hashes, dimensions, and links. Files store content.

Only approved artifacts can unlock gates, unless an explicit waiver exists.

## 2. Recommended directory layout

```text
project-state/
  artifacts/
    brainstorming/
    blueprints/
    decisions/
    design/
      boards/
      crops/
      prompts/
      index/
    assets/
      requirements/
      boards/
      crops/
      index/
    tech-specs/
      pages/
      components/
    tasks/
      envelopes/
      results/
    verification/
      screenshots/
      comparisons/
      deviation-reports/
    acceptance/
    logs/
```

Directories do not define state. DB refs do.

## 3. Artifact status

```text
draft
generated
ready_for_review
approved
rejected
superseded
archived
```

Rules:

- `approved` artifacts can satisfy gates.
- `superseded` artifacts are historical and MUST NOT be used as new task inputs by default.
- `rejected` artifacts remain for traceability but do not unlock gates.

## 4. Versioning

Versioned artifact examples:

```text
delivery-blueprint-v1.md
decision-list-v1.md
design-board-001-v1.png
home-main-v1.png
asset-requirements-v1.md
home-hero-bg-v1.webp
home-tech-spec-v1.md
result-home-implementation-v1.json
home-design-vs-impl-v1.png
acceptance-report-v1.md
```

## 5. Design Board

Design Board is a high-fidelity multi-page/state visual reference board.

MUST:

- support multiple pages/states;
- avoid phone/browser frames unless explicitly required;
- maintain clear slot boundaries;
- preserve prompt and review artifacts;
- record page slot mapping and crop boxes;
- be treated as design reference, not implementation asset source.

Artifact types:

```text
design_board
design_board_prompt
design_board_review
```

Slot metadata example:

```json
{
  "slot_id": "home-main",
  "slice_id": "home",
  "state": "main",
  "crop_box": {"x": 0, "y": 0, "w": 720, "h": 1280}
}
```

## 6. Page Design Crop

Page Design Crop is the single page/state image used as implementation visual reference.

MUST:

- link to source Design Board;
- store crop box and dimensions;
- be approved before implementation_ready;
- cover every primary state and key layout-changing state;
- not include external presentation frames.

Artifact type:

```text
page_design_crop
```

## 7. Design Review

Design review records:

- approved pages/states;
- rejected pages/states;
- missing states;
- visual decisions;
- user decisions needed;
- readiness for tech spec.

## 8. Asset Requirements

Asset requirements describe real implementation media needs.

Each asset requirement SHOULD include:

```text
asset_id
usage
target_page
target_state
target_component
target_display_size
target_aspect_ratio
safe_area
fit_mode: cover | contain | fill
style_prompt
negative_prompt
format
output_path
reuse_scope
requires_user_approval
```

## 9. Asset Board

Asset Board is an independent generation board for implementation assets.

MUST:

- separate each asset region clearly;
- follow target aspect ratios;
- include sufficient gutter between regions;
- avoid text/logos/UI controls unless the asset explicitly needs them;
- be cropped into individual Asset Crops before code usage.

Artifact types:

```text
asset_board
asset_board_prompt
```

## 10. Asset Crop

Asset Crop is the actual image/background/icon/illustration used by implementation.

MUST:

- link to source Asset Board and requirement;
- record crop box, dimensions, hash, output path, usage, and consuming files;
- be resized/compressed to project needs;
- be approved or explicitly waived before implementation uses it.

Artifact type:

```text
asset_crop
```

## 11. Technical specs

Page tech specs SHOULD include:

- route/entry
- page responsibility
- approved design references
- approved asset references
- layout structure
- components
- data sources
- state management
- interactions
- loading/empty/error states
- responsive behavior
- accessibility notes
- implementation boundaries
- acceptance criteria

Component tech specs SHOULD include responsibility, props/emits or input/output, internal state, data flow, error handling, styling constraints, reuse boundary, and verification needs.

## 12. Task envelope and result manifest artifacts

Every dispatch SHOULD create a task envelope artifact. Every provider return SHOULD create a result manifest artifact.

Task envelope and result manifest schemas remain compatible with `kanban-capability-task/v1` and `kanban-capability-result/v1`.

## 13. Verification artifacts

### Screenshot

Records route, viewport, device, dimensions, dev server URL, capture time, and status.

### Comparison

Pairs approved design crop with implementation screenshot, usually left/right.

### Visual Deviation Report

Status values:

```text
no_significant_deviation
accepted_deviation
needs_revision
user_review_required
```

### Acceptance Report

Final report MUST summarize completed slices, deferred scope, design versions, tech spec versions, verification results, blockers, debts, waivers, visual deviations, build/test evidence, and final state.

## 14. Context usage

Main orchestrator SHOULD read artifact metadata and summaries by default. Full artifact bodies are read only for the active gate, active slice, active decision, or active blocker.
