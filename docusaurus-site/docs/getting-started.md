---
title: 快速开始
description: qchem-stack 文档站与工程仓库的统一入口，先理解你该从哪条路径开始。
keywords:
  - qchem-stack
  - docusaurus
  - 快速开始
  - 文档站
---

# 快速开始

这个站点是 `qchem_qml_md` 的主文档入口，目标不是展示“概念海报”，而是帮助你快速完成三件事：

- 跑通一条最小量子化学管线
- 找到你要改的配置、脚本和接口
- 在团队场景下稳定运行并可复现

## 你现在该点哪里

| 你的目标 | 建议入口 |
|---|---|
| 先跑通结果 | [15 分钟上手](./tutorial/quickstart) 或 [三条路径索引](./tutorial/tutorial-index-three-paths) |
| 先理解配置怎么组织 | [工作流与 YAML 概览](./tutorial/workflow) |
| 我是维护者，要看全局结构 | [指南总览（P1-P4）](./guide/) |
| 我要接 HTTP / 队列 | [命令行与脚本](./reference/cli-and-scripts) + [HTTP API](./reference/http-api-sqlite-jobs) |
| 我要做规划与验收 | [产品路线图](./product/roadmap) + [工程架构](./concept/engineering-architecture) |

## 站点结构（维护视角）

- `docs/product`：产品能力、边界和路线
- `docs/guide`：P1-P4 主线（化学 -> 程序 -> 执行 -> 作业）
- `docs/tutorial`：可运行教程，强调“做什么 + 怎么验证”
- `docs/reference`：CLI、HTTP、CircuitIR、DMET 等契约页
- `docs/cloud`：本地/私有部署的云化治理实践
- `docs/product` / `docs/concept`：产品路线、架构边界和验收口径

## 维护原则（建议）

- 教程必须“可运行 + 可验证”，不要只写概念描述
- 参考页保持契约稳定，优先补字段和状态机，而不是口号
- 规划页保持诚实口径：能力范围、边界与证据可追溯
- 首页与导航的链接只指向可维护、长期稳定的入口页

## 外部参考（按需）

- [项目仓库 README](https://github.com/sunhl4/qcchem-qml-md)
