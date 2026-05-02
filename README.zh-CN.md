# Project Orchestrator

[![Repository](https://img.shields.io/badge/GitHub-fitoe%2FPlanToDelivery-181717?logo=github)](https://github.com/fitoe/PlanToDelivery)
[![Skill](https://img.shields.io/badge/Codex-Local%20Skill-10a37f)](./.agents/skills/project-orchestrator/SKILL.md)
[![Docs](https://img.shields.io/badge/docs-orchestrator-blue)](./docs/orchestrator/)

[English README](README.md)

`project-orchestrator` 是一个本地 Codex skill 包，用来让软件项目以更强约束、更可恢复、更适合长周期协作的方式推进。

它主要解决这些常见问题：

- 前期规划不充分，开发时不断跑偏
- 测试零散，做到一半才发现无法验证
- 会话一长就失控，换新会话后难以继续
- 项目中途不断插入新想法，导致执行节奏崩掉
- 文档、代码、状态分散在聊天上下文里，难以恢复

## 仓库里有什么

当前仓库主要包含三部分：

- 本地 skill 包：`.agents/skills/project-orchestrator/`
- 仓库级持久状态文档：`docs/orchestrator/`
- 大量规划、执行、测试、恢复、交付模板

## 目录

- [仓库里有什么](#仓库里有什么)
- [它的定位](#它的定位)
- [核心流程](#核心流程)
- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [怎么使用这个 skill](#怎么使用这个-skill)
- [适合什么项目](#适合什么项目)
- [当前状态](#当前状态)
- [下一步](#下一步)

## 它的定位

这个 skill 不是单纯“帮你写代码”的工具，更像一个项目总管家。

它负责：

- 判断项目当前阶段
- 强制执行阶段门禁
- 编排该调用哪些 skill
- 把项目状态落到仓库文档里
- 控制变更、测试、恢复、交付节奏

它希望让 Codex 更像：

- 项目经理
- 技术负责人
- 执行调度器
- 质量守门员

而不是普通补全型助手。

## 核心流程

整个 skill 以阶段机为核心：

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

核心原则包括：

- 前期把重要决策定深定清
- 实施期默认冻结范围，减少中途漂移
- 优先复用已有代码和依赖，不重复造轮子
- 项目状态优先落盘，不依赖聊天记忆
- 没有 fresh verification 不宣称完成

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
  roadmap.md
  decision-log.md
  milestones/
```

## 快速开始

1. 在 Codex 中打开这个仓库。
2. 加载本地 skill：`.agents/skills/project-orchestrator/`
3. 如果仓库已有状态文档，先从 `docs/orchestrator/session-brief.md` 开始。
4. 如果是新项目或半成品项目，先从 `intake` 阶段进入。

## 怎么使用这个 skill

最小使用流程：

1. 先读 `.agents/skills/project-orchestrator/SKILL.md`
2. 判断当前项目所处阶段
3. 只加载当前阶段需要的 `references/`
4. 用对应的 `templates/` 生成或补齐文档
5. 持续把状态更新到 `docs/orchestrator/`

推荐入口：

- Skill 主入口：[SKILL.md](./.agents/skills/project-orchestrator/SKILL.md)
- 总流程说明：[references/workflow.md](./.agents/skills/project-orchestrator/references/workflow.md)
- Skill 路由说明：[references/skill-routing.md](./.agents/skills/project-orchestrator/references/skill-routing.md)
- 恢复入口：[docs/orchestrator/session-brief.md](./docs/orchestrator/session-brief.md)

## 适合什么项目

比较适合：

- 从 0 开始、但不想边做边乱改的项目
- 已做一半、需要补 intake 和 gap analysis 的项目
- 跨多会话推进、需要稳定恢复能力的项目
- 希望把规划、测试、验证、handoff 都标准化的项目

## 当前状态

这个仓库当前已经完成第一版 skill 落盘，包含：

- 主 `SKILL.md`
- 阶段路由和门禁规则
- UI、测试、安全、观测、性能、集成等专题 guidance
- 一整套可复用模板
- 仓库级状态文档骨架

仍然需要继续做的：

- 在真实或模拟项目上试跑
- 根据实战结果补齐缺口
- 持续收紧流程细节

## 下一步

当前下一阶段是拿一个真实或模拟场景，试跑这套 skill，验证它在实际项目中的表现，再迭代优化。
