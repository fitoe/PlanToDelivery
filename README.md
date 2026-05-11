# PlanToDelivery

[![GitHub Repo](https://img.shields.io/badge/GitHub-fitoe%2FPlanToDelivery-181717?logo=github)](https://github.com/fitoe/PlanToDelivery)
[![Codex Skill](https://img.shields.io/badge/Codex-Local%20Skill-10a37f)](./.agents/skills/plantodelivery/SKILL.md)
[![Docs](https://img.shields.io/badge/docs-orchestrator-blue)](./docs/orchestrator/)
[![README](https://img.shields.io/badge/README-English-lightgrey)](./README.en.md)

[English](./README.en.md)

PlanToDelivery 是一个面向 skill 用户的 Codex 项目总控产品。

它不是普通的提示词集合，也不是单次对话脚本，而是一套可复用的项目交付系统。  
它帮助你把一个软件项目从需求澄清、规划、设计、实施、测试、验证，到交付收尾，稳定地推进成可恢复、可审计、可持续迭代的流程。

## 为什么需要它

当你在做真实项目时，最常见的问题不是“不会写代码”，而是：

- 前期规划不够，开发过程中不断跑偏
- UI、测试、验证和收尾没有统一节奏
- 会话太长，换新会话后难以继续
- 中途临时加需求，执行节奏被打断
- 状态只存在聊天里，无法可靠恢复

PlanToDelivery 的目标，就是把这些问题收束成一套标准流程。

## 它适合谁

适合你如果正在做：

- 需要深规划的 greenfield 项目
- 已经做了一半、需要继续推进的半成品项目
- 希望跨会话持续推进的中长期项目
- 需要把 spec、plan、test、handoff 标准化的个人或团队
- 希望 UI 设计、浏览器验证、代码实现、交付收尾能够串起来的人

## 它提供什么

### 1. 项目总控

- 接管新项目
- 接管已有规划文档
- 从半成品代码反推当前状态
- 输出 gap analysis，决定继续、补规划还是重规划

### 2. 全流程规划

- product spec
- feature breakdown
- decision log
- roadmap
- milestone spec
- implementation plan

### 3. UI 路由与视觉生成

- 先规划路由和页面功能
- 再做风格图 / 效果预览
- 冻结风格后批量复用
- 大页面按 section 切分
- 由 section 逐块生成代码并拼装

### 4. 浏览器验证

- 用 Playwright 做关键页面验证
- 复现浏览器 bug
- 采集控制台、网络、截图证据
- 为 milestone 验收提供证据链

### 5. 交付治理

- 风险矩阵
- milestone test plan
- regression plan
- verification report
- session brief
- final handoff

### 6. 可控扩展

- 支持按阶段加载额外 skill
- 支持 `idea-to-design`、`design-to-code`、`imagegen`、`Playwright`
- 支持渐进加载，不一次性塞满上下文
- 依赖产物和门禁证据，不强依赖某个 skill 的具体实现

## 核心工作流

PlanToDelivery 以阶段状态机为核心：

1. `intake`
2. `discovery`
3. `product-definition`
4. `ui-definition`
5. `system-definition`
6. `decision-closure`
7. `roadmap`
8. `milestone-spec`
9. `milestone-plan`
10. `execution`
11. `debugging`
12. `verification`
13. `handoff`
14. `done`

默认原则：

- 先判断当前阶段
- 再检查门禁
- 优先读取 `quick-start.md` 和项目状态
- 需要编排判断时再读取 `orchestration-core.md`
- 需要写模板时先查 `templates/index.md`
- 再加载对应的 reference / template / skill

## 三 Skill 协作方式

PlanToDelivery 可以作为总控，推荐这样协作：

- `idea-to-design`：负责把想法整理成产品结构、页面规划、设计说明和视觉稿
- `design-to-code`：负责把已批准设计源转成高还原代码，并处理缺图补足
- `PlanToDelivery`：负责阶段、门禁、状态、验收和交付闭环

三者不是硬耦合关系。PlanToDelivery 接受等价产物：

- `Design-Spec.md` 或等价产品/设计文档
- `state.json` 或等价可恢复设计状态
- 已批准设计图，或等价持久化视觉来源
- `Pre-Implementation Brief`，或等价代码实现 brief

这意味着 `idea-to-design` 和 `design-to-code` 可以独立使用；在端到端项目里再由 PlanToDelivery 编排。

## 轻量启动与省 Token

当前版本默认采用轻量启动：

- 先读 `quick-start.md`
- 再读 `docs/orchestrator/project-state.json` 或 session brief
- 只在门禁、路由或交接不清楚时读取 `orchestration-core.md`
- 不默认加载全部 references 和 templates

目标是保留完整交付能力，同时让新会话恢复更快、上下文更小。

## 技能包结构

```text
.agents/skills/plantodelivery/
  SKILL.md
  quick-start.md
  agents/openai.yaml
  references/
    orchestration-core.md
  templates/
    index.md

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

## 通过 skills CLI 安装

如果你使用的是支持 Agent Skills 生态的工具链，可以直接通过 `skills` CLI 安装本仓库：

```bash
# 查看可发现的 skills
npx skills add https://github.com/fitoe/PlanToDelivery --list

# 安装指定 skill
npx skills add https://github.com/fitoe/PlanToDelivery --skill PlanToDelivery

# 从本地仓库安装
npx skills add .
```

说明：

- 当前 skill 名称是 `PlanToDelivery`
- 物理目录位于 `.agents/skills/plantodelivery/`
- `skills` CLI 会搜索 `.agents/skills/`
- `agents/openai.yaml` 是 Codex 侧的增强元数据，不是最低要求

## 建议的使用顺序

1. 先读 [quick-start.md](./.agents/skills/plantodelivery/quick-start.md)
2. 再读 [SKILL.md](./.agents/skills/plantodelivery/SKILL.md)
3. 编排判断优先读 [orchestration-core.md](./.agents/skills/plantodelivery/references/orchestration-core.md)
4. 需要具体阶段细节时再读对应 reference
5. 需要创建文档时先读 [templates/index.md](./.agents/skills/plantodelivery/templates/index.md)
6. 把状态写回 `docs/orchestrator/`

## 当前状态

这个仓库已经完成第一版落盘：

- 本地 skill 包已建立
- 核心 references / templates 已建立
- durable docs 协议已建立
- GitHub 协作文件已补齐
- `idea-to-design`、`design-to-code`、Playwright、imagegen 的路由已接入
- 轻量启动、artifact 契约和模板索引已补齐

下一步最重要的是：

- 用真实或模拟项目试跑
- 根据 trial-use 结果继续压缩、补洞、校准流程

## English Summary

See [README.en.md](./README.en.md) for a compact English overview.
