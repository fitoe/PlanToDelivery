# Kanban 状态人性化重命名规划

> **For Hermes:** Planning-only artifact. Do not implement until user confirms the naming direction.

**Goal:** 将 PlanToDelivery / 贾维斯 kanban 的底层状态、列分组和展示文案调整为更贴近真实工作流的人类语言，同时保持机器可执行的状态枚举稳定、可审计、可测试。

**Architecture:** 不先动业务代码。本计划建议把“机器状态”和“人类展示阶段”分层：`kanban_status` 继续做执行状态机，新增/强化 display layer 表示用户看到的工作流阶段。这样既不会破坏 Hermes Kanban 生命周期，也能让看板从“待办/已调度/就绪”变成“待拆解/待开工/执行中/待确认/已完成”等更自然的列。

**Tech Stack:** Python runtime `plantodelivery/kanban_runtime.py`，pytest，JSON artifact overlay `project-state/kanban/kanban-state.json`，Hermes Kanban CLI adapter。

---

## 当前观察

代码里当前 display 映射在：

- `plantodelivery/kanban_runtime.py:23-34`
  - `backlog`: `待办`
  - `ready`: `待派发`
  - `dispatched`: `已派发`
  - `running`: `进行中`
  - `review`: `待审查`
  - `blocked`: `已阻塞`
  - `partial`: `部分完成`
  - `completed`: `已完成`
  - `failed`: `失败`
  - `cancelled`: `已取消`

问题不是状态机本身错，而是面向用户时太偏底层实现：

- `dispatched / 已派发` 对用户不够直观，像系统动作，不像工作阶段。
- `ready / 待派发` 和 `backlog / 待办` 边界不清。
- `review / 待审查` 可以更贴合用户确认语境，例如“待确认/待验收”。
- “带分类”如果来自 board grouping/category，应该和执行状态分开，不应混入 lifecycle。
- 现在刚去掉 gate 语义，不能再引入另一套含糊控制面；展示更友好，但执行规则仍应是 kanban lifecycle。

---

## 推荐方案：机器状态稳定 + 用户阶段人性化

### 1. 保留机器状态枚举，不直接重命名 schema 字段

继续保留：

```text
backlog, ready, dispatched, running, review, blocked, partial, completed, failed, cancelled
```

原因：

- 这些状态已经被 runtime、测试、Hermes backend、结果 ingest、review approval 使用。
- 直接改 enum 会带来迁移成本和兼容风险。
- 用户痛点主要是看板展示/列名不人性化，而不是机器状态不可用。

### 2. 修改中文展示标签

建议第一版改为：

| machine status | 当前展示 | 建议展示 | 语义 |
|---|---|---|---|
| `backlog` | 待办 | 待梳理 | 需求/想法进来了，但还没拆成可执行任务 |
| `ready` | 待派发 | 待开工 | 依赖满足，已经可以开始做 |
| `dispatched` | 已派发 | 已分配 | 已创建任务/已交给执行者，等待 claim/start |
| `running` | 进行中 | 执行中 | 正在处理 |
| `review` | 待审查 | 待确认 | 产物已出，需要人/主编排确认 |
| `blocked` | 已阻塞 | 卡住了 | 缺输入、权限、方向确认或外部依赖 |
| `partial` | 部分完成 | 部分完成 | 有可用产物，但还有剩余任务 |
| `completed` | 已完成 | 已完成 | 可验收完成 |
| `failed` | 失败 | 未通过 | 执行失败或验收失败 |
| `cancelled` | 已取消 | 已取消 | 不再继续 |

这个版本相对克制，不改变执行状态，只让看板更像人话。

### 3. 可选：增加 `display_stage`，避免中文名承载太多逻辑

如果后续希望更贴合完整交付流，可以在 card/index 里新增 display-only 字段：

```json
{
  "kanban_status": "dispatched",
  "display_status": "已分配",
  "display_stage": "准备执行"
}
```

建议阶段：

| display_stage | 覆盖状态/条件 |
|---|---|
| `需求池` | backlog |
| `准备执行` | ready / dispatched |
| `执行中` | running |
| `等待确认` | review |
| `卡住` | blocked |
| `收尾` | partial |
| `完成` | completed |
| `关闭` | failed / cancelled |

但第一轮可以不加字段，只改展示文案和测试，风险更低。

---

## 不建议的方案

### 不建议 1：把状态改成完整业务阶段

例如直接把 enum 改成：

```text
intake, planning, design_source, implementation, verification, acceptance, done
```

问题：

- 这些是“工作流阶段”，不是任务执行状态。
- 会和 capability 流程混淆：同一个任务可以是 `visual_implementation`，但状态仍可能是 `running/review/blocked`。
- 容易重蹈 gate 的问题：多一套控制面。

### 不建议 2：把 category 当 status

“带分类”应理解为泳道/标签/任务类型，例如：

- 产品规划
- 视觉源
- 技术方案
- 实施
- 验证
- 发布/交付

它应该是 `category / capability / swimlane`，不是 lifecycle status。

---

## 实施计划（待确认后执行）

### Task 1: 更新展示文案映射

**Objective:** 只修改用户可见中文 display，不改变 kanban 状态枚举。

**Files:**
- Modify: `plantodelivery/kanban_runtime.py:23-34`
- Test: `tests/test_kanban_runtime.py`

**Change:**

```python
DISPLAY_KANBAN_STATUSES = {
    "backlog": "待梳理",
    "ready": "待开工",
    "dispatched": "已分配",
    "running": "执行中",
    "review": "待确认",
    "blocked": "卡住了",
    "partial": "部分完成",
    "completed": "已完成",
    "failed": "未通过",
    "cancelled": "已取消",
}
```

**Verification:**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest -q tests/test_kanban_runtime.py
```

Expected:

- 相关 display_status 测试更新后通过。

### Task 2: 更新 display 相关测试断言

**Objective:** 保证测试明确锁定新的人类展示文案。

**Files:**
- Modify: `tests/test_kanban_runtime.py`

**Likely assertions to update:**

- `已派发` -> `已分配`
- `待审查` -> `待确认`
- `已阻塞` -> `卡住了`
- `进行中` 如果有断言则改 `执行中`
- `失败` 如果有断言则改 `未通过`

**Verification:**

Run:

```bash
python3 -m py_compile plantodelivery/kanban_runtime.py tests/test_kanban_runtime.py
PYTHONPATH=. uv run --with pytest pytest -q tests/test_kanban_runtime.py tests/test_provenance.py tests/test_provider_guard.py
```

Expected:

- 全部相关测试通过。

### Task 3: 补一个 display mapping 单测

**Objective:** 防止以后又退回系统口吻。

**Files:**
- Modify: `tests/test_kanban_runtime.py`

**Suggested test:**

```python
def test_display_kanban_status_uses_human_workflow_labels() -> None:
    assert display_kanban_status("backlog") == "待梳理"
    assert display_kanban_status("ready") == "待开工"
    assert display_kanban_status("dispatched") == "已分配"
    assert display_kanban_status("running") == "执行中"
    assert display_kanban_status("review") == "待确认"
    assert display_kanban_status("blocked") == "卡住了"
    assert display_kanban_status("failed") == "未通过"
```

### Task 4: 可选更新文档/技能术语

**Objective:** 如果用户确认新命名，应把 PlanToDelivery 技能和 docs 中的旧 display 文案同步，避免以后继续写“gate / 待派发 / 待审查”。

**Files likely:**
- `/home/imjzq/.hermes/skills/PlanToDelivery/SKILL.md`
- `docs/architecture/kanban-skill-v2-redesign.md`
- `docs/contracts/kanban-capability-envelope-v1.md` or related contract docs if they mention display labels

**Note:** 这一步可以单独做，因为技能文档里仍有较多 gate 旧词；建议后面作为一个 docs cleanup checkpoint。

---

## 决策点

我建议先采用这个低风险命名：

```text
backlog    -> 待梳理
ready      -> 待开工
dispatched -> 已分配
running    -> 执行中
review     -> 待确认
blocked    -> 卡住了
partial    -> 部分完成
completed  -> 已完成
failed     -> 未通过
cancelled  -> 已取消
```

如果你希望更“项目管理/交付流”一点，也可以选这个版本：

```text
backlog    -> 待整理
ready      -> 可开工
dispatched -> 已安排
running    -> 处理中
review     -> 待验收
blocked    -> 有阻塞
partial    -> 待补齐
completed  -> 已完成
failed     -> 未通过
cancelled  -> 已关闭
```

---

## 执行状态

用户已确认采用推荐命名，本轮已实施低风险方案：

1. 已改 runtime display mapping
2. 已补/更新测试
3. 已运行 py_compile + pytest
4. 待形成 commit checkpoint
