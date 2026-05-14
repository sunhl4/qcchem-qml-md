---
title: 按角色导航
description: 按研究者、平台工程师、维护者三类角色给出推荐阅读和执行路径。
---

# 按角色导航

如果你不确定先读哪一页，按你的角色从下面入口开始。

## 量子化学研究者

**目标**：快速建立实验配置并得到可解释结果。

推荐路径：

1. [15 分钟上手](/tutorial/quickstart)
2. [工作流与 YAML 概览](/tutorial/workflow)
3. [P1 化学与嵌入](/guide/chemistry-and-embedding)
4. [P2 程序构建](/guide/program-construction)
5. [案例：H2 家族链式改配](/tutorial/case-study-h2-family)

## 平台工程师（API / 作业 / 集成）

**目标**：把 pipeline 接入服务化链路并稳定运行。

推荐路径：

1. [P4 作业与可复现](/guide/jobs-and-reproducibility)
2. [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)
3. [命令行与脚本](/reference/cli-and-scripts)
4. [HTTP 异步运行教程](/tutorial/async-run-via-http)
5. [云与运维概览](/cloud/overview)

## 维护者（对标 / 验收 / 规划）

**目标**：维护文档契约、控制能力边界、推进差距收敛。

推荐路径：

1. [产品功能](/product/features)
2. [定位与路线](/product/positioning)
3. [公开契约矩阵](/parity/public-matrix)
4. [差距与实施计划](/parity/gap-implementation-plan)
5. [路线图](/product/roadmap)

## 通用建议

- 先跑最小样例，再扩配置复杂度
- 每次改动保留结果摘要和 `repro`
- 对 `partial` 能力保持证据链和计划链
