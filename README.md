# PlanToDelivery

[![GitHub Repo](https://img.shields.io/badge/GitHub-fitoe%2FPlanToDelivery-181717?logo=github)](https://github.com/fitoe/PlanToDelivery)
[![Codex Skill](https://img.shields.io/badge/Codex-Local%20Skill-10a37f)](./.agents/skills/project-orchestrator/SKILL.md)
[![Docs](https://img.shields.io/badge/docs-orchestrator-blue)](./docs/orchestrator/)
[![README](https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87%E4%B8%BA%E4%B8%BB-informational)](./README.en.md)

[English](README.en.md) | [历史中文入口](README.zh-CN.md)

PlanToDelivery 是一个面向 Codex / agent 工作流的**项目总控 skill 产品**。  
它的目标不是“辅助写几段代码”，而是把一个软件项目从想法、规划、设计、实施、测试、验证，到最终交付，收束成一套**可执行、可恢复、可审计、可持续迭代**的标准流程。

它主要解决这些问题：

- 前期规划不充分，开发时不断跑偏
- 测试零散，做到一半才发现无法验证
- 会话一长就失控，换新会话后难以继续
- 项目中途频繁插入新需求，执行节奏被打断
- 项目状态散落在聊天上下文里，无法可靠恢复

## 目录

- [产品定位](#产品定位)
- [核心价值](#核心价值)
- [适用场景](#适用场景)
- [能力边界](#能力边界)
- [核心能力](#核心能力)
- [工作流阶段](#工作流阶段)
- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [在 Codex 中如何使用](#在-codex-中如何使用)
- [核心产物](#核心产物)
- [GitHub 协作信息](#github-协作信息)
- [当前状态](#当前状态)
- [路线图](#路线图)
- [英文摘要](#英文摘要)

## 产品定位

PlanToDelivery 的定位是：

- 一个项目总管家
- 一个强约束状态机
- 一个 skill 编排器
- 一个文档驱动恢复系统
- 一个执行与验证守门员

它不是：

- 单纯的 prompt 集合
- 普通代码补全助手
- 只会写 spec 的文档工具
- 只会生成模板、不约束流程的空壳 skill

## 核心价值

### 1. 规划先行

在真正进入实现前，把高影响决策尽量前置做深：

- 项目目标
- 功能细化
- 技术栈
- UI 方向
- 测试重点
- 验收标准
- 数据、权限、安全、部署、观测、性能、集成规则

### 2. 执行受控

进入 `milestone-plan` 和 `execution` 后默认冻结范围，减少边做边改、边做边想。

### 3. 状态落盘

项目状态写进仓库文档，而不是只存在会话上下文里。  
这样即使：

- 会话崩溃
- 上下文超长
- 多会话协作
- 中断数天后恢复

也能继续推进。

### 4. 测试与验证内建

不是“写完代码再想测试”，而是：

- milestone 先有测试计划
- 风险和分层双维度组织测试
- 验证证据优先于主观判断

### 5. 可演进

PlanToDelivery 不是固定死的单回合工具，而是一套可继续迭代、扩展、校正的 skill 产品。

## 适用场景

特别适合：

- 需要深规划的 greenfield 项目
- 已做一半、需要补 intake 和 gap analysis 的半成品项目
- 多阶段 milestone 推进的中长周期项目
- 希望跨会话可靠续作的 agent 驱动开发
- 希望把 spec、plan、test、handoff 标准化的团队或个人

## 能力边界

PlanToDelivery 能做的是：

- 接管新项目、半成品项目、已有规划项目
- 组织深度规划
- 生成和维护 durable docs
- 编排已有 skill 和流程
- 约束实现、调试、验证和收尾

它不能保证的是：

- 完全零人工参与完成所有高影响决策
- 在需求持续变化时仍然无代价保持稳定
- 不经 trial-use 就天然适配所有项目风格

一句话：  
**它追求的是高自治、强流程、可恢复，不是无边界全自动。**

## 核心能力

### 项目接管

- intake 新项目
- 接管已有规划文档
- 从半成品代码反推 current state
- 输出 gap analysis

### 规划治理

- product spec
- feature breakdown
- decision log
- roadmap
- milestone spec
- milestone plan

### UI 规划

- 结构化 UI 规划
- 风格方向方案
- 页面级 / 组件级 / 交互规则级输出
- UI 实现约束

### 测试治理

- 风险矩阵
- milestone test plan
- regression plan
- verification report

### 执行与恢复

- 强制阶段门禁
- scope freeze
- process management
- session brief
- handoff / recovery

### 扩展能力

- 可注册额外 skill
- 按阶段受控启用
- 避免一次全塞进上下文

## 工作流阶段

PlanToDelivery 以阶段机为核心：

1. `intake`
2. `discovery`
3. `full-definition`
4. `ui-definition`
5. `decision-closure`
6. `roadmap`
7. `milestone-spec`
8. `milestone-plan`
9. `execution`
10. `debugging`
11. `verification`
12. `handoff`
13. `done`

默认原则：

- 先判断当前阶段
- 再判断是否满足门禁
- 再决定应该加载哪些 references / templates / skills

## 仓库结构

```text
.agents/skills/project-orchestrator/
  SKILL.md
  agents/openai.yaml
  references/
  templates/

docs/orchestrator/
  session-brief.md
  current-state.md
  gap-analysis.md
  product-spec.md
  feature-breakdown.md
  decision-log.md
  roadmap.md
  milestones/
```

### 关键目录说明

#### `.agents/skills/project-orchestrator/`

本地 skill 包主体：

- `SKILL.md`：主入口
- `references/`：专题 guidance
- `templates/`：可复用文档模板
- `agents/openai.yaml`：UI 元数据

#### `docs/orchestrator/`

仓库级 durable state：

- 当前阶段
- 当前 milestone
- 当前任务
- 当前状态
- gap analysis
- decision log
- roadmap
- handoff / verification 产物

## 快速开始

### 方式一：把它当本地 skill 使用

1. 在 Codex 中打开这个仓库
2. 加载本地 skill：`.agents/skills/project-orchestrator/`
3. 从 `SKILL.md` 进入
4. 根据当前阶段，按需加载 `references/` 和 `templates/`
5. 持续把状态写入 `docs/orchestrator/`

### 方式二：把它迁移到你的项目中

你可以把以下内容复制到自己的项目仓库：

- `.agents/skills/project-orchestrator/`
- `docs/orchestrator/` 协议结构

然后根据你的项目目标开始 `intake` 或 `discovery`。

## 在 Codex 中如何使用

最小使用流程：

1. 读取 [SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
2. 判断项目当前阶段
3. 只加载当前阶段相关的 `references/`
4. 使用对应 `templates/` 生成或更新文档
5. 持续维护 `docs/orchestrator/`

推荐入口：

- 主入口：[SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
- 总流程：[references/workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)
- 阶段门禁：[references/stage-gates.md](./.agents/skills/project-orchestrator/references/stage-gates.md)
- 路由规则：[references/skill-routing.md](./.agents/skills/project-orchestrator/references/skill-routing.md)
- 恢复入口：[docs/orchestrator/session-brief.md](./docs/orchestrator/session-brief.md)

## 核心产物

PlanToDelivery 的一个重要设计点，是把项目从“上下文记忆”转成“仓库产物”。

常见产物包括：

- `product-spec.md`
- `feature-breakdown.md`
- `decision-log.md`
- `roadmap.md`
- `ui-*`
- `milestone-*`
- `verification-report`
- `session-brief.md`
- `final-handoff.md`

## GitHub 协作信息

仓库当前已补齐基础协作信息：

- GitHub About / description
- topics
- 英文 README
- 中文 README

后续如继续产品化，建议逐步补充：

- issue templates
- PR template
- CONTRIBUTING
- SECURITY
- license 策略

## 当前状态

当前仓库已经完成：

- 第一版本地 skill 落盘
- 核心 references 建立
- 核心 templates 建立
- 仓库级 durable docs 骨架建立
- GitHub 发布初始化

当前还没有完成的是：

- 在真实或模拟项目上试跑
- 基于真实使用结果迭代 tightening

## 路线图

当前下一阶段是：

### `M1 - Skill Consistency and Trial Use`

目标：

- 选一个真实或模拟场景
- 用 PlanToDelivery 跑通至少一轮 `intake -> planning`
- 记录缺口
- 收紧流程和模板

## 英文摘要

PlanToDelivery is a Codex skill product for disciplined project delivery.

It combines:

- milestone-based planning
- stage gates
- durable repository state
- testing and verification discipline
- cross-session recovery
- controlled skill routing

Chinese is the primary documentation language in this repository.  
For an English summary, see [README.en.md](README.en.md).
