# Vue Progress Overlay MVP Design

**Date:** 2026-05-10
**Status:** Approved for implementation
**Project:** PlanToDelivery

## Goal

Add a minimal Vue progress overlay capability to PlanToDelivery so monitored Vue/Vite/uni-app H5 projects can show automatic development progress inside the app through a DevTools-like floating button.

## Scope

The MVP supports Vue only and ships as two templates:

- `.agents/skills/project-orchestrator/templates/progress-overlay/vue/DeliveryProgressOverlay.vue`
- `.agents/skills/project-orchestrator/templates/progress-overlay/project-progress.template.json`

When used in a target project, these become:

- `src/components/DeliveryProgressOverlay.vue`
- `public/orchestrator/project-progress.json`

## Non-Goals

The MVP does not include:

- Vite HMR plugin
- npm package distribution
- React/vanilla adapters
- WebSocket/SSE live updates
- multi-project dashboard
- complex task tree visualization

## User Experience

The overlay appears as a fixed floating button in the bottom-right corner.

Collapsed state shows the active milestone and progress, for example:

```txt
M1 68%
```

Expanded state shows:

- project name and total progress
- active milestone and milestone progress
- current stage
- current task
- next action
- visible-first layer progress: Visual, Interaction, Functional, Hardening
- blockers
- recent progress events
- last updated time

Status color semantics:

- active: blue
- waiting: purple
- blocked: red
- paused: gray
- done: green
- warning/deferred: amber

## Data Model

The overlay reads `public/orchestrator/project-progress.json`.

Required top-level fields:

```json
{
  "schemaVersion": "1.0",
  "updatedAt": "2026-05-10T00:00:00+08:00",
  "project": {
    "name": "Project Name",
    "progress": 0,
    "stage": "intake",
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

The Vue component must tolerate missing fields and malformed data by falling back to safe defaults.

## Refresh Strategy

The MVP uses polling only.

- Default endpoint: `/orchestrator/project-progress.json`
- Default interval: 2000ms
- Cache busting: append `?t=Date.now()`
- If fetch fails, keep the last valid state and display a small stale/error indicator.

The polling interval is local browser behavior and independent from Weixin message throttling.

## Integration Pattern

Target Vue project usage:

```vue
<script setup lang="ts">
import DeliveryProgressOverlay from '@/components/DeliveryProgressOverlay.vue'
</script>

<template>
  <RouterView />
  <DeliveryProgressOverlay />
</template>
```

The component exposes props so target projects can customize without editing internals:

- `src?: string`
- `pollInterval?: number`
- `initialOpen?: boolean`
- `position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'`

## PlanToDelivery Rules

When a target project enables the Vue Progress Overlay:

1. Copy the Vue component template into the target project.
2. Copy the JSON template to `public/orchestrator/project-progress.json`.
3. Update the JSON after each meaningful checkpoint before reporting progress.
4. Never report mock/demo/placeholder work as real functional progress.
5. Use visible-first layer fields for UI-heavy projects.
6. Keep the JSON small and human-readable.

## Acceptance Criteria

- The PlanToDelivery skill documents the Vue overlay capability.
- The two MVP templates exist in the project-orchestrator skill template directory.
- The JSON template is valid JSON.
- The Vue template is self-contained and does not require external UI libraries.
- The component handles missing/failed JSON safely.
- Documentation explains where to copy the two files in target projects.
- The project verifies with git diff review and template syntax sanity checks.
