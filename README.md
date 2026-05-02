# PlanToDelivery

[![GitHub Repo](https://img.shields.io/badge/GitHub-fitoe%2FPlanToDelivery-181717?logo=github)](https://github.com/fitoe/PlanToDelivery)
[![Codex Skill](https://img.shields.io/badge/Codex-Local%20Skill-10a37f)](./.agents/skills/project-orchestrator/SKILL.md)
[![Docs](https://img.shields.io/badge/docs-orchestrator-blue)](./docs/orchestrator/)
[![README](https://img.shields.io/badge/README-English-lightgrey)](./README.en.md)

[English](./README.en.md) | [中文别名页](./README.zh-CN.md)

PlanToDelivery 是一个面向 Codex / agent 工作流的项目总控 skill 产品。

它的目标不是“帮你补几段代码”，而是把一个软件项目从需求澄清、规划、设计、实施、测试、验证，到交付收尾，收束成一套可持续推进的标准流程。它强调：

- 前期充分规划，后期尽量少打断
- milestone 驱动，而不是一口气失控推进
- 文档落盘，而不是只依赖当前会话记忆
- 测试、验证、handoff 内建，而不是事后补救
- 可以跨会话恢复，可以接管半成品项目

## 产品定位

PlanToDelivery 更像：

- 项目总管家
- 强约束状态机
- skill 编排器
- 文档驱动恢复层
- 测试与验证守门员

它不是：

- 普通 prompt 集合
- 单次对话脚本
- 只会写 spec 的模板包
- “全自动完成所有决策”的黑盒代理

## 解决的问题

PlanToDelivery 主要解决这些常见失控点：

- 前期规划不充分，开发时不断跑偏
- 测试零散，做到一半才发现无法验证
- 会话一长就失控，换新会话后难以继续
- 项目中途不断插入新需求，执行节奏被打断
- 项目状态散落在聊天上下文里，无法可靠恢复

## 核心能力

### 1. 项目接管

- 接管全新项目
- 接管已有规划文档
- 从半成品代码反推 current state
- 产出 gap analysis，决定继续、补规划还是重规划

### 2. 全流程规划

- product spec
- feature breakdown
- decision log
- roadmap
- milestone spec
- implementation plan

### 3. UI 规划

- 结构化 UI 规划
- 风格方向提案
- 页面级 / 组件级 / 交互规则级规格
- UI implementation contract

### 4. 测试与验证治理

- 风险矩阵
- milestone test plan
- regression plan
- verification report
- fresh verification gate

### 5. 执行与恢复

- 强阶段门禁
- scope freeze
- process management
- session brief
- final handoff

### 6. 可控扩展

- 注册额外 skill
- 按阶段按需启用
- 渐进加载，避免一次性塞满上下文

## 工作流阶段

PlanToDelivery 以阶段状态机为核心：

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
- 再检查是否满足门禁
- 再决定该加载哪些 reference、template、skill

## 技能包内容

本仓库目前落地的是本地 skill 包 `project-orchestrator`。

核心入口：

- [`.agents/skills/project-orchestrator/SKILL.md`](./.agents/skills/project-orchestrator/SKILL.md)

核心组成：

- `references/`
  - 流程约束、阶段门禁、routing、intake、testing、security、performance、integration 等专题 guidance
- `templates/`
  - spec、plan、test、verification、recovery、UI、security、observability 等模板
- `agents/openai.yaml`
  - skill 元数据

## 仓库级 durable docs

PlanToDelivery 的一个重要设计点，是把项目状态从“会话记忆”变成“仓库产物”。

当前协议位于：

- [`docs/orchestrator/`](./docs/orchestrator/)

关键文件包括：

- `session-brief.md`
- `current-state.md`
- `gap-analysis.md`
- `product-spec.md`
- `feature-breakdown.md`
- `decision-log.md`
- `roadmap.md`
- `milestones/*`
- `final-handoff.md`

## 适用场景

特别适合：

- 需要深规划的 greenfield 项目
- 已开发一半、需要补 intake 和 gap analysis 的项目
- 需要 milestone 推进的中长期项目
- 希望跨会话可靠续作的 agent 驱动开发
- 希望把 spec、plan、test、handoff 标准化的个人或团队

## 能力边界

PlanToDelivery 能做的是：

- 组织规划
- 固化流程
- 编排 skill
- 维护 durable docs
- 驱动执行、验证和恢复

它不保证：

- 零人工参与完成所有高影响决策
- 在需求持续变化时依然零代价稳定推进
- 不经过 trial-use 就天然适配所有项目

一句话：

**它追求的是高自治、强流程、可恢复，不是无边界全自动。**

## 快速开始

### 方式一：直接作为本地 skill 使用

1. 打开本仓库
2. 从 [`.agents/skills/project-orchestrator/SKILL.md`](./.agents/skills/project-orchestrator/SKILL.md) 进入
3. 根据当前项目阶段，按需加载 `references/` 与 `templates/`
4. 将 durable state 写入 `docs/orchestrator/`

### 方式二：迁移到你的项目仓库

可复制以下结构到你的目标项目：

- `.agents/skills/project-orchestrator/`
- `docs/orchestrator/`

再从 `intake` 或 `discovery` 开始。

## 推荐阅读顺序

如果你第一次接触这个 skill，建议按这个顺序看：

1. [SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
2. [workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)
3. [stage-gates.md](./.agents/skills/project-orchestrator/references/stage-gates.md)
4. [skill-routing.md](./.agents/skills/project-orchestrator/references/skill-routing.md)
5. [session-brief.md](./docs/orchestrator/session-brief.md)

## GitHub 协作信息

当前仓库已经补齐基础公开协作信息：

- [Issue Templates](./.github/ISSUE_TEMPLATE/)
- [Pull Request Template](./.github/PULL_REQUEST_TEMPLATE.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Changelog](./CHANGELOG.md)

如果你要参与改进，建议先看：

1. [CONTRIBUTING.md](./CONTRIBUTING.md)
2. 当前 `docs/orchestrator/session-brief.md`
3. 对应阶段的 reference / template

## 当前状态

当前仓库已经完成：

- 第一版本地 skill 落盘
- 核心 references 落盘
- 核心 templates 落盘
- 仓库级 durable docs 骨架落盘
- GitHub 基础公开协作面补齐

下一阶段重点：

- `M1`: 用真实或模拟场景试跑
- 根据 trial-use 结果修订 stage gates、routing、template 粒度和 durable docs 协议

## 路线图

近期路线：

- 完成 trial-use
- 修补真实使用中暴露的流程缺口
- 收敛模板噪音，强化高价值模板
- 形成更稳定的 release / versioning 习惯

中期路线：

- 提炼更稳定的安装方式
- 明确版本兼容策略
- 补更清晰的试跑示例和最佳实践

## 英文摘要

PlanToDelivery is a local Codex skill product for disciplined software project delivery.

It provides:

- milestone-based planning and execution
- durable repository state for cross-session recovery
- strong stage gates and scope control
- built-in testing, verification, and handoff discipline
- controlled skill routing instead of unbounded orchestration

For a shorter English overview, see [README.en.md](./README.en.md).
