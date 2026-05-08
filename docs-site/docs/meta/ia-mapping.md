---
title: IA slug 映射
description: 四柱命名、URL 与仓库 docs/*.md 的 canonical 对照
---

# 文档站信息架构：四柱 slug 与源文件映射

本文件为 **IA 定稿**：四柱中英文命名、URL slug（ASCII）、与仓库 `qchem_qml_md/docs/` 内 Markdown 的对应关系。站内路由以英文 slug 为准；导航标签可同时展示中文。尽调延伸：[安全与数据](/meta/security-and-data)。

**定稿说明**：四柱 slug 与对标文档站计划中「显式第四维：作业与可复现」一致；与首页四柱卡片、指南总览一一对应。线框见 [首页与指南线框](/meta/wireframe-home-and-guides)；技术选型见 [SSG 与搜索策略](/meta/ssg-search-strategy)；Diátaxis 归类索引见 [文档类型索引](/meta/diataxis-index)。

## 四柱（Pillars）

| ID | 中文名 | English label | URL slug | 中文站路径 | English site path | 对应 InQuanto 枢纽 |
|----|--------|-----------------|----------|------------|-------------------|-------------------|
| P1 | 化学与嵌入 | Chemistry & embedding | `chemistry-and-embedding` | `/guide/chemistry-and-embedding/` | `/en/guide/chemistry-and-embedding/` | Chemical Specification；drivers / DMET / projection |
| P2 | 算法与协议 | Algorithms & protocols | `algorithms-and-protocols` | `/guide/algorithms-and-protocols/` | `/en/guide/algorithms-and-protocols/` | Program Construction；Algorithm* / Protocols / Computables |
| P3 | 执行与分析 | Execution & analysis | `execution-and-analysis` | `/guide/execution-and-analysis/` | `/en/guide/execution-and-analysis/` | Execution and Analysis；circuit execution / resource / mitigation |
| P4 | 作业与可复现 | Jobs & reproducibility | `jobs-and-reproducibility` | `/guide/jobs-and-reproducibility/` | `/en/guide/jobs-and-reproducibility/` | 对标站分散在 Nexus + 手册；本站聚合 runs API / `repro` / parity |

## Diátaxis 文档类型 × URL 前缀

| 类型 | slug 前缀 | 用途 |
|------|-----------|------|
| Concept | `/concept/` | 心智模型与分层边界 |
| Tutorial | `/tutorial/` | 可运行的最短路径 |
| Reference | `/reference/` | API、契约表、字段白名单 |
| Parity | `/parity/` | 对标矩阵、签 off、SLA 残余 |

## 产品与落地页（非 Diátaxis 单列）

| slug | 说明 |
|------|------|
| `/product/features` | **产品功能**：用户向能力分层、用户接口表、学习顺序（对外主入口） |
| `/product/` | **定位与路线**：边界、路线图、内部研发对标 InQuanto 索引 |
| `/product/roadmap` | 路线图：P0–P2 节拍图、Y1 Q3 L3 摘要、Parity 延伸阅读索引 |
| `/en/product/features` | 同上（English · Product features） |
| `/en/product/` | 同上（English · Positioning） |
| `/en/product/roadmap` | 同上（English） |

## 源文件 → 站内路径（canonical mapping）

| 仓库相对路径 `qchem_qml_md/docs/` | 站内路径 | 备注 |
|-----------------------------------|----------|------|
| `README.md` | — | **仅仓库内**：入口与三母稿索引；不镜像到 VitePress |
| （新建） | `/tutorial/quickstart` | 摘自 README 编排与 YAML 示例 |
| （新建） | `/tutorial/workflow-overview` | 工作流与 YAML 与四柱对应（教程） |
| （新建） | `/guide/principles-and-reading` | 原理与阅读建议（指南） |
| `ENGINEERING_ARCHITECTURE.md` | `/concept/engineering-architecture` | 全文迁入 |
| `架构_InQuanto闭源能力闭合与可复现边界.md`（已删） | `/concept/engineering-memory-quantinuum` §0；`/concept/architecture-boundaries` | 正文并入 `工程记忆…` §0；旧路由页可保留为快照 |
| `技术文档_HTTP_API与SQLite作业队列及可观测性契约.md` | `/reference/http-api-sqlite-jobs` | 全文迁入 |
| `技术文档_CircuitIR与TKET桥接及作业契约.md` | `/reference/circuitir-tket-jobs` | 全文迁入 |
| `技术文档_设备比特串与Qiskit采样路径.md` | `/reference/qiskit-shot-counts` | 全文迁入 |
| `技术文档_DMET与parity_snapshot开放契约.md` | `/reference/dmet-parity-snapshot` | 全文迁入 |
| `launch_retrieve_nexus_analog.md` | `/concept/launch-retrieve-nexus-analog` | 全文迁入 |
| `mitigation_PMSV_ZNE_Qermit_mapping.md` | `/concept/mitigation-mapping` | 全文迁入 |
| `inquanto_public_parity_matrix.md` | `/parity/public-matrix` | 全文迁入 |
| `L1_InQuanto_alignment_signoff.md`（已删） | `/parity/gap-implementation-plan#appendix-c`；`/parity/l1-signoff` | 正文并入 `与InQuanto…` 附录 C；本站 L1 页为摘要/镜像 |
| `InQuanto_Y1_public_alignment_ledger.md`（已删） | `/parity/gap-implementation-plan#appendix-b`；`/parity/y1-alignment-ledger` | 正文并入 `与InQuanto…` 附录 B；本站 Y1 页为摘要/镜像 |
| `Y1_residual_partial_SLA_template.md`（已删） | `/parity/y1-alignment-ledger#y1-residual-partial-sla-template` | 全文并入台账 **§6**；`/parity/y1-residual-sla-template` 为跳转 stub |
| `与InQuanto能力差距与实施计划.md` | `/parity/gap-implementation-plan` | 全文迁入 |
| `竞争定位与路线图_对标Quantinuum产品与技术路线.md` | `/concept/competitive-positioning` | 全文迁入 |
| `工程记忆_Quantinuum对标与数据流技术文档.md` | `/concept/engineering-memory-quantinuum` | 全文迁入 |
| `L3_benchmark_suite_roadmap.md`（已删） | `/parity/y1-alignment-ledger#l3-benchmark-suite-roadmap` | 全文并入台账 **§7**；`/parity/l3-benchmark-roadmap` 为跳转 stub |
| `记忆_开放栈对标完成度与待闭合项.md`（已删） | `/concept/engineering-memory-quantinuum#13-…` | 合并入仓库 `工程记忆…` §13；`/parity/open-stack-memory` 为别名页 |
| `记忆_HTTP_API与作业队列_工程记忆.md`（已删） | `/reference/http-api-sqlite-jobs#9-…` | 合并入仓库 HTTP 技术文档 §9；`/concept/http-api-worker-memory` 为别名页 |
| `不排期项_转排期与实现说明.md`（已删） | `/parity/gap-implementation-plan#appendix-f`；`/parity/backlog-to-schedule` | 正文并入 `与InQuanto…` 附录 F；本站 backlog 页为摘要/镜像 |
PandM 文献索引等仍位于仓库 `Yaozheng/PandM/`；静态部署时相对链接可能不可用，请在检出完整 monorepo 时使用。

**与 InQuanto 公开站模块一一对照、便于以后逐项改写的母版**：[InQuanto 模块复现骨架](/meta/inquanto-module-scaffold)。
