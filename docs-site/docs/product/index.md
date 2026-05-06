---
title: 定位与路线
description: 产品边界、路线图与内部研发对标索引（面向规划与验收；日常使用见「产品功能」与教程）
---

**使用产品**请优先：[产品功能](/product/features) → [教程](/tutorial/quickstart) → [指南](/guide/) → [命令行与脚本](/reference/cli-and-scripts)。

本页说明**边界、路线与内部计划**：与公开 InQuanto 文档的对标是**研发目标与验收依据**，不是终端用户必读。

## 产品边界（摘要）

开放编排：YAML、多后端、strict repro。不宣称闭源 wheel、Nexus 真云或商业真机对等。展开见 [竞争定位](/concept/competitive-positioning) 与 [工程分层](/concept/engineering-architecture)。

## 路线图

产品节拍与开放能力规划见 **[路线图](/product/roadmap)**。

## 内部研发目标：与 InQuanto 公开文档的对标（工程）

以下条目服务**内部计划、差距闭合与尽调**，按需阅读：

与 [公开 InQuanto 站](https://docs.quantinuum.com/inquanto/) 三柱对照；本站另立 **P4（作业与可复现）**。

| InQuanto 柱 | 本站工程入口 |
|-------------|----------------|
| Chemical Specification | [P1](/guide/chemistry-and-embedding/) · [DMET](/reference/dmet-parity-snapshot) · [Mirror Manual](/mirror/manual/) |
| Program Construction | [P2](/guide/algorithms-and-protocols/) · [CircuitIR](/reference/circuitir-tket-jobs) · [Mirror API](/mirror/api/algorithms/) |
| Execution and Analysis | [P3](/guide/execution-and-analysis/) · [P4](/guide/jobs-and-reproducibility/) · [云](/cloud/) |

**契约与台账**：[契约矩阵](/parity/public-matrix) · [Y1 台账](/parity/y1-alignment-ledger) · [/mirror/](/mirror/) · [安全与数据](/meta/security-and-data)。机读 backlog：`docs/inquanto-node-backlog.generated.json`（`npm run report:inquanto-backlog`）。
