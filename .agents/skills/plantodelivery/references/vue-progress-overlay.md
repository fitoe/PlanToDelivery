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

## Auto-Enable On First Use

When PlanToDelivery first enters execution for an eligible Vue/Vite/uni-app H5 project, enable the overlay automatically unless the user has disabled it.

Eligibility:

- `package.json` exists.
- The project appears to use Vue, Vite, or uni-app H5.
- A public/static directory exists or can be safely created.
- A stable root shell exists, such as `src/App.vue` or an equivalent uni-app H5 shell.
- No existing custom progress overlay conflicts with the template.

Disable conditions:

- user says not to enable the overlay
- repository state records `progress_overlay: disabled`
- target project is not a browser UI project
- production/user-data risk exists

Auto-enable actions:

1. Copy `templates/progress-overlay/project-progress.template.json` to `public/orchestrator/project-progress.json` if missing.
2. Copy `templates/progress-overlay/vue/DeliveryProgressOverlay.vue` to `src/components/DeliveryProgressOverlay.vue` if missing.
3. Write initial progress values from the active PlanToDelivery state.
4. Patch the app shell only when the import and dev-only mount point are unambiguous.
5. If the shell is ambiguous, leave source code unchanged and record the manual mount instruction.

Safe shell patch requirements:

- import can be added without colliding with existing names
- root template has an obvious app shell or root layout
- mount uses dev-only gating, normally `<DeliveryProgressOverlay v-if="import.meta.env.DEV" />`
- patch does not alter production routes, product UI, or app state

If any requirement is unclear, install the files only and report the manual mount step.

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

The template uses VueUse (`@vueuse/core`) for dragging, viewport size, and saved position. If the target project does not already depend on VueUse, add it or replace those composables before mounting.

For uni-app H5, place the component in the root page or shell page that remains mounted during development. `src/App.vue` may be lifecycle-only and may not render the overlay; verify the actual mounted shell. In some uni-app H5 dev servers, `public/orchestrator/project-progress.json` is reachable as `/public/orchestrator/project-progress.json` rather than `/orchestrator/project-progress.json`; probe the URL and override the `src` prop if needed.

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
- `focus.reason`: why this page is the right page to watch. This is JSON metadata; the compact overlay does not show it by default.
- `focus.status`: `ready`, `pending`, or `blocked`.
- `focus.version`: increment when the focus target changes or when the same route should be followed again.

The expanded overlay shows a compact `跟随页面` control:

- off by default
- browser-local only; never written back to JSON
- selecting it immediately navigates to `focus.route`
- after selecting it, follow stays enabled instead of auto-canceling
- while enabled, changes to `focus.route` or `focus.version` navigate again automatically
- if the user manually leaves the last followed route, follow turns off
- unavailable when the route is unsafe or missing

Safe follow routes:

- allowed: `/path`, `/path?query=value`, `/path#hash`
- blocked: external URLs, protocol URLs, `javascript:`, protocol-relative URLs, empty routes

For Vue Router projects, pass a router-like object when desired:

```vue
<DeliveryProgressOverlay v-if="import.meta.env.DEV" :router="router" />
```

Without a router prop, the component uses `window.history.pushState` and dispatches `popstate`.

## Overlay UI Behavior

The shipped component is intentionally compact. The collapsed button shows only the milestone percentage. The expanded panel emphasizes:

1. milestone progress and current task
2. current focus page and follow control
3. next action
4. blockers, only when present
5. compact check status and updated time

Do not add project-wide dashboards, nested task lists, layer-by-layer percentages, recent logs, debt lists, route debug text, or verbose reasons to the default expanded panel. Those fields may remain in JSON for automation, but the default UI should keep important work-state information obvious.

The button is draggable via VueUse (`useDraggable`) and persists its position in localStorage. Clamp the position into the viewport on mount, resize, and open/close so a stale saved position cannot hide the button.

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
8. Enable `跟随页面` and confirm the dev browser navigates and the switch remains on.
9. Increment `focus.version` or change `focus.route`; confirm it follows again while enabled.
10. Manually navigate away and confirm follow turns off.
11. Drag the collapsed progress button, refresh, and confirm it remains visible in the viewport.
12. Confirm the expanded panel stays compact and highlights only progress, current page, next action, and blockers.
13. Confirm the component is gated behind `import.meta.env.DEV` and does not render in production.
