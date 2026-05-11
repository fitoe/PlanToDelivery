# Vue Progress Overlay

Use this reference when a Vue, Vite, or uni-app H5 target project should show PlanToDelivery progress inside the running app.

## Purpose

The Vue Progress Overlay is a lightweight development-time visibility adapter. It shows the current PlanToDelivery progress as a floating DevTools-like button in the target app.

PlanToDelivery remains the source of truth. The overlay only renders `project-progress.json`.

The overlay is development-only. It must not become production product behavior.

## MVP Files

The plantodelivery skill ships two templates:

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
  <DeliveryProgressOverlay v-if="import.meta.env.DEV" />
</template>
```

For uni-app H5, place the component in the root page or shell page that remains mounted during development.

The component also has `devOnly` enabled by default. When production can be detected, it does not render, poll, or navigate.

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
- current development focus route changes
- validation/check status changes

## Data Contract

The JSON should stay small and human-readable.

Required base fields:

```json
{
  "schemaVersion": "1.1",
  "updatedAt": "2026-05-11T00:00:00+08:00",
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
  "focus": {
    "route": "/orders/create?tab=items",
    "pageName": "Order Create",
    "activity": "Refining form validation interaction",
    "reason": "Current work affects the order create page",
    "status": "ready",
    "version": 1,
    "updatedAt": "2026-05-11T10:00:00+08:00"
  },
  "checks": {
    "lastRun": "focused route smoke",
    "status": "deferred",
    "reason": "Full checks deferred until checkpoint",
    "updatedAt": "2026-05-11T10:00:00+08:00"
  },
  "tasks": [],
  "debts": [],
  "blockers": [],
  "recent": []
}
```

Schema `1.1` is backward-compatible with `1.0`. The overlay must tolerate missing `focus`, `checks`, `tasks`, and `debts`.

## Focus And Follow

Use `focus` to tell the browser which page is currently useful to watch while the agent is working.

- `focus.route`: internal route to inspect, including query/hash when useful.
- `focus.pageName`: human-readable page name.
- `focus.activity`: what the agent is changing now.
- `focus.reason`: why this page is the right page to watch.
- `focus.status`: `ready`, `pending`, or `blocked`.
- `focus.version`: increment when the focus target changes or the same route needs a fresh one-shot follow.

The expanded overlay shows a `Follow` control:

- off by default
- browser-local only; never written back to JSON
- one-shot: selecting it jumps once to `focus.route`
- after the one-shot jump, follow is automatically turned off
- if the user manually leaves the focus route before the next poll, follow is also turned off
- unavailable when `focus.status` is not `ready`, project status is `blocked`/`paused`, or the route is unsafe

Safe follow routes:

- allowed: `/path`, `/path?query=value`, `/path#hash`
- blocked: external URLs, protocol URLs, `javascript:`, protocol-relative URLs, empty routes

For Vue Router projects, pass a router-like object when desired:

```vue
<DeliveryProgressOverlay v-if="import.meta.env.DEV" :router="router" />
```

Without a router prop, the component uses `window.history.pushState` and dispatches `popstate`.

## Checks, Tasks, And Debt

Use `checks` for the latest validation posture:

- `deferred`: broad checks intentionally delayed until a meaningful checkpoint
- `running`: a check is in progress
- `passed`: latest relevant check passed
- `failed`: latest relevant check failed

Use `tasks` for a short, flat list of top work items. Do not model nested task trees in the overlay.

Use `debts` for non-blocking quality debt. Do not mix debt with blockers.

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
- production-visible progress UI

## Verification

After copying into a target Vue project:

1. Confirm `public/orchestrator/project-progress.json` is reachable in the browser.
2. Mount `<DeliveryProgressOverlay />` in the app shell.
3. Start the dev server.
4. Edit the JSON file.
5. Confirm the overlay updates within the polling interval.
6. Confirm stale indicator appears if the JSON path is temporarily unavailable.
7. Set `focus.status` to `ready` and `focus.route` to a safe internal route.
8. Enable `Follow` and confirm the dev browser navigates once.
9. Manually navigate away and confirm `Follow` turns off.
10. Confirm the component is gated behind `import.meta.env.DEV` and does not render in production.
