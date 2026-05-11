# Vue Progress Overlay

Use this reference when a Vue, Vite, or uni-app H5 target project should show PlanToDelivery progress inside the running app.

## Purpose

The Vue Progress Overlay is a lightweight development-time visibility adapter. It shows the current PlanToDelivery progress as a floating DevTools-like button in the target app.

PlanToDelivery remains the source of truth. The overlay only renders `project-progress.json`.

## MVP Files

The project-orchestrator skill ships two templates:

- `templates/progress-overlay/project-progress.template.json`
- `templates/progress-overlay/vue/DeliveryProgressOverlay.vue`

Copy them into the target project as:

- `public/orchestrator/project-progress.json`
- `src/components/DeliveryProgressOverlay.vue`

## Target Project Usage

```vue
<script setup lang="ts">
import DeliveryProgressOverlay from '@/components/DeliveryProgressOverlay.vue'
</script>

<template>
  <RouterView />
  <DeliveryProgressOverlay />
</template>
```

For uni-app H5, place the component in the root page or shell page that remains mounted during development.

## Refresh Behavior

The component polls:

```txt
/orchestrator/project-progress.json
```

Default interval:

```txt
2000ms
```

The request appends a timestamp query parameter to avoid browser caching. If fetch fails, the overlay keeps the last valid state and marks itself stale.

## Required Update Rule

When Vue Progress Overlay is enabled, update `public/orchestrator/project-progress.json` after every meaningful checkpoint before reporting progress.

Meaningful checkpoints include:

- stage gate passes
- task completion
- task blocking
- task deferral
- milestone change
- verification pass/failure
- user approval of product/UI/system decisions
- visible-first layer changes

## Data Contract

The JSON should stay small and human-readable.

Required fields:

```json
{
  "schemaVersion": "1.0",
  "updatedAt": "2026-05-10T00:00:00+08:00",
  "project": {
    "name": "Project Name",
    "progress": 0,
    "stage": "execution",
    "status": "active"
  },
  "milestone": {
    "id": "M1",
    "name": "Milestone Name",
    "progress": 0,
    "currentTask": "Current task",
    "nextAction": "Next action"
  },
  "layers": {
    "visual": 0,
    "interaction": 0,
    "functional": 0,
    "hardening": 0
  },
  "blockers": [],
  "recent": []
}
```

## Status Values

Use these project status values when possible:

- `active`
- `waiting`
- `blocked`
- `paused`
- `done`
- `warning`

High or critical blockers turn the overlay red even if project status is still `active`.

## Visible-First Semantics

For UI-heavy projects, keep the `layers` object aligned with PlanToDelivery visible-first states:

- `visual`: page reachability, layout, visual structure, mock data visibility
- `interaction`: navigation, clicks, local state, demo flows, loading/empty/error visuals
- `functional`: real APIs, permissions, persistence, business rules, true submissions
- `hardening`: regression, performance, accessibility, refactor, release checks

Do not inflate `functional` progress for mock/demo/placeholder behavior.

## Non-Goals For MVP

Do not add these during MVP installation unless the user explicitly requests it:

- Vite HMR plugin
- npm package dependency
- WebSocket/SSE
- React/vanilla adapter
- multi-project dashboard
- complex nested task tree

## Verification

After copying into a target Vue project:

1. Confirm `public/orchestrator/project-progress.json` is reachable in the browser.
2. Mount `<DeliveryProgressOverlay />` in the app shell.
3. Start the dev server.
4. Edit the JSON file.
5. Confirm the overlay updates within the polling interval.
6. Confirm stale indicator appears if the JSON path is temporarily unavailable.
