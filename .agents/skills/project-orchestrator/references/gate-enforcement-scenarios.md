# Gate Enforcement Scenarios

Use these scenarios to verify that `PlanToDelivery` blocks premature implementation.

Main rule:
- if a required artifact or confirmation is missing, output a gate check and block the transition

---

## Scenario 1: User asks to start coding after idea only

User says:
- "先直接实现吧"
- "页面你自己发挥"
- "不用设计图，先写代码"

Required response:
- current stage: `discovery` or `product-definition`
- gate decision: `blocked`
- owning skill: `idea-to-design`
- next action: produce or repair product/design artifacts

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
- current stage: `ui-definition`
- gate decision: `blocked` for page implementation
- owning skill: `idea-to-design`
- next action: generate/approve design assets or explicitly mark visual design out of scope

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
- current stage: `ui-definition` or `decision-closure`
- gate decision: `blocked`
- owning skill: `design-to-code`
- next action: produce brief, then wait for confirmation

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
- gate decision: `blocked`
- next action: persist approved asset under repository docs

Must not:
- treat chat-only or temp-only image as durable evidence
- proceed using memory of the image

---

## Scenario 5: New session has stale state

State:
- `session-brief.md` contradicts milestone task state
- no latest gate check exists

Required response:
- current stage: `intake`
- gate decision: `blocked`
- next action: repair durable state before new work

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
- only lower-order decisions may default
- first-order decisions still require explicit confirmation
- gate decision remains `blocked` if user confirmation is required

Must not:
- treat implied consent as approval for UI direction, implementation brief, stack, or final acceptance

---

## Minimal Gate Response Shape

When blocked, respond in this shape:

```md
Gate Check: [from] -> [to]
- [requirement]: pass/fail/n/a ([evidence])

Decision: blocked
Owning skill: [idea-to-design/design-to-code/PlanToDelivery]
Next action: [single next step]
```

Keep it short. Do not dump the full workflow.
