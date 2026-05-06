---
title: 与 InQuanto 的对标框架
description: qchem-stack 对标 InQuanto 的能力映射方法，覆盖三柱主线与工程化 P4 扩展。
keywords:
  - InQuanto
  - parity
  - benchmark
  - roadmap
---

# 与 InQuanto 的对标框架

本页用于内部产品规划和能力缺口讨论，不是用户使用手册。

## 对标主轴

我们参考 InQuanto 文档公开结构，统一用三柱做能力映射：

- Chemical Specification
- Program Construction
- Execution and Analysis

参考站点：

- [InQuanto 官方文档](https://docs.quantinuum.com/inquanto/)

## 当前站点的映射方式

- `Chemical Specification` -> [P1 化学与嵌入](../guide/chemistry-and-embedding)
- `Program Construction` -> [P2 程序构建](../guide/program-construction)
- `Execution and Analysis` -> [P3 执行与分析](../guide/execution-and-analysis)
- 工程化补充 -> [P4 作业与可复现](../guide/jobs-and-reproducibility)

## 建议对标维度

- **文档信息架构**：首页、导航、教程、手册、API 是否清晰分层
- **接口可用性**：YAML/Python/HTTP/CLI 是否覆盖核心场景
- **工程可复现性**：结果结构、日志与追踪信息是否可审计
- **平台化程度**：作业队列、状态查询、扩展后端能力

## 边界说明

- 不以闭源组件等价为目标
- 以开放可验证的工程路径为主
- 通过文档和契约先形成稳定对外面
