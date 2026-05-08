---
title: 原理与阅读建议
description: "底层机制与算法 — 建议的站内阅读顺序与深度材料入口（非教程步骤）"
---

本页不是「操作步骤」，而是**在已能跑示例之后**，按主题加深理解时的建议路径。细节仍以源码与 [Reference 各篇](/reference/http-api-sqlite-jobs)（从 HTTP API 起可串到 CircuitIR、Qiskit、DMET 等）为准。

## 经典–量子接口与化学嵌入

1. [工程分层架构](/concept/engineering-architecture) — 化学 / 量子核 / 协议 / 作业的分层。  
2. [P1 化学与嵌入](/guide/chemistry-and-embedding/) — 驱动、哈密顿量、活性空间、嵌入模式。  
3. [DMET · parity_snapshot](/reference/dmet-parity-snapshot) — 与 `repro` 对齐的契约字段（实现面）。

## 算法、协议与电路

1. [P2 算法与协议](/guide/algorithms-and-protocols/) — 变分与激发叙事、五阶段 Protocol。  
2. [CircuitIR · TKET · 作业契约](/reference/circuitir-tket-jobs) — 编译、资源与作业侧字段。  
3. [Qiskit 比特串采样](/reference/qiskit-shot-counts) — shots 路径与公开叙事对齐说明。

## 执行、缓解与「云类比」

1. [P3 执行与分析](/guide/execution-and-analysis/) — 后端、采样、资源。  
2. [缓解映射（PMSV / ZNE / Qermit）](/concept/mitigation-mapping) — 缓解语义与机读报告。  
3. [Launch / Retrieve（Nexus 类比）](/concept/launch-retrieve-nexus-analog) — 仅类比，非商业云实现。

## 作业、HTTP 与可复现

1. [P4 作业与可复现](/guide/jobs-and-reproducibility/) — 队列、FastAPI、`repro`。  
2. [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs) — 端点与状态机。  
3. [HTTP API 维护记忆](/concept/http-api-worker-memory) — 设计取舍与排错线索。

## 与竞品公开文档的关系（内部研发视角）

若你负责**对标与验收**，再读 [竞争定位](/concept/competitive-positioning)、[工程记忆（Quantinuum）](/concept/engineering-memory-quantinuum) 及 [Parity 分区](/parity/public-matrix) 下各篇；它们服务**内部计划与目标**，不必作为终端用户的第一阅读材料。

## 外部教材与论文（建议）

- 变分量子本征求解、激发态方法：以你所在课题组教材与最新综述为准；本站指南给出**与本栈配置字段的对应关系**，不替代系统学习。  
- 密度泛函与经典嵌入：同上；PySCF 官方文档与论文 Methods 与 [P1](/guide/chemistry-and-embedding/) 交叉阅读效果更好。

## 仓库母稿 `docs/` 索引（纯路径）

下列路径相对于 **`qchem_qml_md` 仓库根**，为站内 Concept / Parity / Reference 的**中文或中英母稿**；在本地 IDE 打开即可（本站不链到 VitePress 树外文件，以免死链）。

- `docs/README.md`（**按主题导览**；与 `README.md` / `CONTRIBUTING.md` 与 `docs/技术文档_*.md` §2 分组一致）
- `docs/ENGINEERING_ARCHITECTURE.md`
- `docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`
- `docs/技术文档_CircuitIR与TKET桥接及作业契约.md`
- `docs/技术文档_设备比特串与Qiskit采样路径.md`
- `docs/技术文档_DMET与parity_snapshot开放契约.md`
- `docs/P1_化学与嵌入_InQuanto镜像与qchem_stack复现程度对照.md`
- `docs/inquanto_public_parity_matrix.md`
- `docs/与InQuanto能力差距与实施计划.md`
- `docs/与InQuanto能力差距与实施计划.md`（附录 C）
- `docs/与InQuanto能力差距与实施计划.md`（附录 B）
- `docs/与InQuanto能力差距与实施计划.md`（附录 B）（**§6** SLA、**§7** L3；原独立模板已并入）
- `docs/工程记忆_Quantinuum对标与数据流技术文档.md` §13（原 `记忆_开放栈…` 已合并）
- `docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md`
- `docs/architecture-report-quantinuum-inquanto-web/INDEX.md`（多卷报告入口；含 vol-03 教程思路等）
- `docs/inquanto-node-backlog.generated.json`（295 节点机读 backlog）
