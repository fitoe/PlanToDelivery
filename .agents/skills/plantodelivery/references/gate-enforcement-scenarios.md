# Kanban Constraint Scenarios

Use these scenarios to verify that `PlanToDelivery` blocks premature implementation through Hermes Kanban, not through a separate Gate system.

Main rule:
- if a required artifact, confirmation, card dependency, or result/review evidence is missing, record/return a blocked or review Kanban state and do not transition the card forward.

---

## Scenario 1: User asks to start coding after idea only

User says:
- "先直接实现吧"
- "页面你自己发挥"
- "不用设计图，先写代码"

Required response:
- Kanban constraint: implementation card is `blocked` or not yet created because prerequisite discovery/product/design cards are missing
- owner capability/provider: `idea-to-design`
- next action: create/claim product/design planning card and produce or repair product/design artifacts

Must not:
- create page code
- create implementation plan from vague idea only
- treat user urgency as approval

---

## Scenario 2: UI exists as text plan only

State:
- route list exists
- page descriptions exist
- no approved design image exists

Required response:
- Kanban constraint: page implementation card is `blocked` by missing visual source evidence
- owner capability/provider: `idea-to-design`
- next action: generate/approve design assets or explicitly record visual design as out of scope

Must not:
- route to `design-to-code`
- start page implementation
- claim text brief is visual source of truth

---

## Scenario 3: Design image exists but no implementation brief

State:
- approved design image exists
- no `Pre-Implementation Brief`
- no user confirmation of implementation brief

Required response:
- Kanban constraint: implementation card remains `blocked` or prerequisite brief card remains incomplete
- owner capability/provider: `design-to-code` or `PlanToDelivery` depending on card metadata
- next action: produce brief, then record review/approval evidence before unblocking implementation

Must not:
- generate code directly from image
- infer missing section plan silently

---

## Scenario 4: Brief exists but source image not persisted

State:
- chat contains image
- repository has no approved persisted image path
- `.codex/` or temp path is the only image path

Required response:
- Kanban constraint: card is `blocked`
- next action: persist approved asset under repository docs and reference it from the card/manifest

Must not:
- treat chat-only or temp-only image as durable evidence
- proceed using memory of the image

---

## Scenario 5: New session has stale state

State:
- `session-brief.md` contradicts Kanban card state
- latest result/review/block evidence is missing or inconsistent

Required response:
- Kanban constraint: `unknown` until inspected, then repair card metadata/evidence or mark the affected card `blocked`
- next action: repair Hermes Kanban state/evidence before new work

Must not:
- choose the most convenient state from memory
- start implementation before contradiction is resolved

---

## Scenario 6: User says confirmation is implied

User says:
- "你看着办"
- "默认通过"
- "不用问我，继续"

Required response:
- lower-order decisions may default when reversible
- first-order decisions still require explicit confirmation/evidence when the Kanban card depends on it
- card remains `blocked` or `review` if explicit confirmation is required

Must not:
- treat implied consent as approval for UI direction, implementation brief, stack, or final acceptance

---

## Minimal Kanban Response Shape

When blocked or waiting for review, respond in this shape:

```md
Kanban Constraint
- Board/Card: [board/card id or missing]
- State: [blocked/review/unknown]
- Evidence: [missing or existing evidence path]
- Owner: [idea-to-design/design-to-code/PlanToDelivery]
- Next Kanban-allowed action: [single next step]
```

Keep it short. Do not dump the full workflow.
