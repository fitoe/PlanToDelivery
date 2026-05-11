# Progress Overlay Follow Design

**Date:** 2026-05-11
**Status:** Approved for implementation
**Project:** PlanToDelivery

## Goal

Improve the PlanToDelivery Vue progress overlay so development progress is more useful inside a running app, and add an explicit `Follow` control that can jump the dev browser to the page currently being worked on.

## Scope

Extend the existing Vue progress overlay MVP:

- schema `1.1` for `project-progress.json`
- richer progress fields: `focus`, `checks`, `tasks`, and `debts`
- expanded overlay UI for current focus page, validation state, top tasks, and non-blocking debt
- one-shot `Follow` behavior for development routes
- dev-only guard so the overlay does not render, poll, or navigate in production
- documentation updates for PlanToDelivery JSON update rules

## Non-Goals

This change does not add:

- WebSocket, SSE, or Vite plugins
- npm package distribution
- React or vanilla adapters
- complex nested task trees
- server-side state mutation from the browser
- production runtime behavior

## Data Contract

The overlay remains JSON-driven. PlanToDelivery is the source of truth; the browser only renders the JSON.

Schema `1.1` adds optional fields:

```json
{
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
    "reason": "full checks deferred until checkpoint",
    "updatedAt": "2026-05-11T10:00:00+08:00"
  },
  "tasks": [
    {
      "id": "T1",
      "title": "Finish order create visual shell",
      "status": "in-progress",
      "layer": "visual"
    }
  ],
  "debts": [
    {
      "title": "Replace mock order data",
      "severity": "medium",
      "revisitStage": "functional-wiring"
    }
  ]
}
```

All new fields are optional. The component must remain compatible with schema `1.0`.

## Follow Behavior

`Follow` is explicit, one-shot, and local to the browser.

- Default off.
- User enables it from the expanded overlay.
- If `focus.status` is `ready` and `focus.route` is safe, the component navigates once.
- After the one-shot navigation completes, follow is automatically turned off.
- If the user manually leaves the focus route before the next poll, follow is also turned off.
- Follow state is not written back to JSON.
- Follow is not persisted by default.

Safe routes:

- allowed: `/path`, `/path?query=value`, `/path#hash`
- blocked: external URLs, protocol URLs, `javascript:`, protocol-relative URLs, empty routes

Navigation strategy:

- Prefer an injected `router.push` compatible object when provided.
- Otherwise fall back to `window.history.pushState` plus `popstate`.
- No hard reload unless a downstream project deliberately customizes the template.

## Dev-Only Behavior

The overlay is a development tool and must not ship as production behavior.

Recommended mount:

```vue
<DeliveryProgressOverlay v-if="import.meta.env.DEV" />
```

The component also exposes `devOnly`, default `true`. When production can be detected, the component returns no UI, does not poll, and does not navigate.

## PlanToDelivery Update Rules

When the overlay is enabled:

- update `public/orchestrator/project-progress.json` before each meaningful checkpoint report
- update `focus.route`, `focus.pageName`, `focus.activity`, and `focus.reason` when a concrete page is the current work target
- increment `focus.version` when the focus target changes or the same route needs a new one-shot follow
- set `focus.status` to `pending` or `blocked` when the page is not ready to view
- record deferred verification in `checks.status` and `checks.reason`
- keep `tasks` flat and limited to the current top work items
- use `debts` for non-blocking quality debt; do not mix debt with blockers
- do not inflate `functional` progress for mock, demo, pending, or placeholder work

## Acceptance Criteria

- JSON template is valid schema `1.1` and includes `focus`, `checks`, `tasks`, and `debts`.
- Vue overlay displays focus page, activity, checks, tasks, blockers, debts, layers, and recent events.
- `Follow` jumps once to a safe ready focus route.
- Follow turns off after one-shot navigation or manual navigation away from the focus route.
- Unsafe routes do not navigate.
- Component is dev-only by default and does not poll or navigate when production is detected.
- Documentation explains mounting with `import.meta.env.DEV`, JSON update rules, and follow safety rules.
