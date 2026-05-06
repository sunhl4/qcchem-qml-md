# 文档站信息架构：四柱 slug 与源文件映射

本文件为 **IA 定稿**：四柱中英文命名、URL slug（ASCII）、与仓库 [`../docs/`](../docs/) 内 Markdown 的对应关系。站内路由以英文 slug 为准；导航标签可同时展示中文。

## 四柱（Pillars）

| ID | 中文名 | English label | URL slug | 对应 InQuanto 枢纽 |
|----|--------|-----------------|----------|-------------------|
| P1 | 化学与嵌入 | Chemistry & embedding | `chemistry-and-embedding` | Chemical Specification；drivers / DMET / projection |
| P2 | 算法与协议 | Algorithms & protocols | `algorithms-and-protocols` | Program Construction；Algorithm* / Protocols / Computables |
| P3 | 执行与分析 | Execution & analysis | `execution-and-analysis` | Execution and Analysis；circuit execution / resource / mitigation |
| P4 | 作业与可复现 | Jobs & reproducibility | `jobs-and-reproducibility` | 对标站分散在 Nexus + 手册；本站聚合 runs API / `repro` / parity |

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
| `/product/` | 产品与方案：价值主张、三条差异化支柱、端到端管线快照、下一步入口 |
| `/product/roadmap` | 路线图：P0–P2 节拍图、Y1 Q3 L3 摘要、Parity 延伸阅读索引 |
| `/en/product/` | 同上（English） |
| `/en/product/roadmap` | 同上（English） |

## 源文件 → 站内路径（canonical mapping）

| 仓库相对路径 `qchem_qml_md/docs/` | 站内路径 | 备注 |
|-----------------------------------|----------|------|
| （新建） | `/tutorial/quickstart` | 摘自 README 编排与 YAML 示例 |
| `ENGINEERING_ARCHITECTURE.md` | `/concept/engineering-architecture` | 全文迁入 |
| `架构_InQuanto闭源能力闭合与可复现边界.md` | `/concept/architecture-boundaries` | 全文迁入 |
| `技术文档_HTTP_API与SQLite作业队列及可观测性契约.md` | `/reference/http-api-sqlite-jobs` | 全文迁入 |
| `技术文档_CircuitIR与TKET桥接及作业契约.md` | `/reference/circuitir-tket-jobs` | 全文迁入 |
| `技术文档_设备比特串与Qiskit采样路径.md` | `/reference/qiskit-shot-counts` | 全文迁入 |
| `技术文档_DMET与parity_snapshot开放契约.md` | `/reference/dmet-parity-snapshot` | 全文迁入 |
| `launch_retrieve_nexus_analog.md` | `/concept/launch-retrieve-nexus-analog` | 全文迁入 |
| `mitigation_PMSV_ZNE_Qermit_mapping.md` | `/concept/mitigation-mapping` | 全文迁入 |
| `inquanto_public_parity_matrix.md` | `/parity/public-matrix` | 全文迁入；站内链接需改写 |
| `L1_InQuanto_alignment_signoff.md` | `/parity/l1-signoff` | 全文迁入 |
| `InQuanto_Y1_public_alignment_ledger.md` | `/parity/y1-alignment-ledger` | 全文迁入 |
| `Y1_residual_partial_SLA_template.md` | `/parity/y1-residual-sla-template` | 全文迁入 |
| `与InQuanto能力差距与实施计划.md` | `/parity/gap-implementation-plan` | 全文迁入 |
| `竞争定位与路线图_对标Quantinuum产品与技术路线.md` | `/concept/competitive-positioning` | 全文迁入 |
| `工程记忆_Quantinuum对标与数据流技术文档.md` | `/concept/engineering-memory-quantinuum` | 全文迁入 |
| `L3_benchmark_suite_roadmap.md` | `/parity/l3-benchmark-roadmap` | 全文迁入 |
| `记忆_开放栈…`（已删） | `/concept/engineering-memory-quantinuum#13-…` | 合并入工程记忆 §13；`/parity/open-stack-memory` 别名 |
| `记忆_HTTP…`（已删） | `/reference/http-api-sqlite-jobs#9-…` | 合并入 HTTP 契约 §9；`/concept/http-api-worker-memory` 别名 |
| `不排期项_转排期与实现说明.md` | `/parity/backlog-to-schedule` | 全文迁入 |

未列入的短文可归并到 Parity 或 Concept 子索引（后续迭代）。

## 四柱索引页（导航枢纽）

| slug | 说明 |
|------|------|
| `/guide/chemistry-and-embedding/` | P1 摘要 + 链到 concept/reference |
| `/guide/algorithms-and-protocols/` | P2 摘要 + 链到 README 算法表 |
| `/guide/execution-and-analysis/` | P3 摘要 + mitigation / backends |
| `/guide/jobs-and-reproducibility/` | P4 摘要 + HTTP API / launch-retrieve |
