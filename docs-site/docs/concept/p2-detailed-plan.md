---
title: P2 详细实施计划
description: 研究深度 · 大体系 · 产品化前置 — WBS、里程碑、闸门与非目标（路线图 P2）
---

# P2 详细实施计划（研究深度 · 大体系 · 产品化前置）

::: tip 母稿与镜像
**正文修订以仓库母稿为准**：`qchem_qml_md/docs/与InQuanto能力差距与实施计划.md`（**附录 A**）。合并 PR 时请先改母稿再同步本页，或同一 PR 内双改保持一致。
:::

## InQuanto-PySCF × Tangelo 总计划（新增实施入口）

已新增仓库主文档：`docs/实施总计划_InQuanto_PySCF_Tangelo.md`，作为本主题的单一实施入口，统一沉淀：

- InQuanto `inquanto-pyscf` API 能力拆解（公开可核验范围）
- Tangelo 源码借鉴点（`IntegralSolver` 抽象、solver 选择、`SecondQuantizedMolecule` 数据模型）
- `qchem_stack` 当前实现差距矩阵（逐项状态、风险、借鉴动作）
- 双轨实施计划（12 周周历 + 任务级清单，含 DoD、回滚与风险控制）

建议阅读顺序：

1. 本页（P2 路线与边界）
2. `docs/实施总计划_InQuanto_PySCF_Tangelo.md`（详细实施）
3. [差距与实施计划](/parity/gap-implementation-plan)（年度台账与附录锚点）

::: info
本页继续承载路线图语义与里程碑框架；模块级动作与任务分解统一维护在总计划文档，避免双写漂移。
:::

**文档角色**：在 [竞争定位与路线图](/concept/competitive-positioning) §6、§141 残余与 [差距与实施计划](/parity/gap-implementation-plan) 之上，给出 **P2 阶段** 的可执行分解（WBS、里程碑、闸门、非目标）。  
**术语**：本文 **路线图 P2** = 竞品文档中的「研究深度与大体系」阶段；**不等于**「主线结构增强」历史批次（QPE 演示轨接入、Computable 薄层、TKET CI 等——已交付并收进 [差距与实施计划](/parity/gap-implementation-plan) **§3 摘要表**）。

---

## 1. 与 P1 的边界

**P1（广义已闭合）**：L1 公开契约下，`repro` / `parity_snapshot` / export / CI 与矩阵 **`n/a` 诚实降级**（含 TN、BK/SCBK UCCSD Trotter）对齐；UCCSD Trotter（JW）、ZNE 机读合一、Schmidt bath 侧车、ONIOM 玩具层、CASSCF 审计轨道一步、教程与双 parity 等已落地（见 [竞争定位](/concept/competitive-positioning) §6「已闭合批次」与仓库 `docs/与InQuanto能力差距与实施计划.md`（**附录 E**））。

**P2 增量**：在 **不冒充闭源 L0**、**不伪造 Nexus/H 系** 前提下，把仍为 **`partial`** 或 **研究级** 的能力推进到「可写 Methods + 可回归 YAML + 文档叙事闭合」，优先：

1. **QPE / 容错叙事 × 资源与编译**：`run_summary` / `protocol_counts` / TKET 探针的联合叙事与固定键；超出 demo 的 resource estimation 可选分支（不先行宣称化学精度优势）。
2. **分解与大体系**：DMET bath 自洽深化（在用户钩子与开放算法边界内）；**产品向** ONIOM/QM-MM/MI-FNO 或预计算 fragment 输入插件的一条可跑通主线（多于玩具层字段）。
3. **经典电子结构深度**：AVAS / InQuanto 级 CASSCF **不与闭源逐键等价**，但可增加 **文档化 partial 路径** 或社区可替换 driver 钩子。
4. **缓解组合**：在 `qermit_analog` 之外，可选 shadows / 进阶 ZNE 电路放大等 **workflow block**（仍非商业 Qermit）。
5. **映射与 ansatz 广度**：BK/SCBK 上的 UCCSD Trotter 若在矩阵保持 **`n/a`**，则 P2 仅交付 **registry 元数据 + 文档**；若战略升格为 partial 路线，则单独开包与矩阵修订。
6. **MD/ML 产品化**：`QMEFDataset`、主动学习、势函数训练与 `repro` 的稳定字段衔接（竞争定位中的差异化长板）。
7. **社区面**：examples 分离、`docs-site` 教程矩阵扩展、插件模板（对齐竞争定位 **P3** 时可提早启动部分条目）。

### P1 演示轨 vs P2 深度（QPE / export）

- **P1**：`qpe_demo_track`、`methods_resource_unified_v1`、可选 TKET 探针（`configs/example_h2_qpe_track_parity_integrations.yaml`）。  
- **P2**：`export_parity_criteria_table` 顶键 **`resource_estimation_preview_v1`**（`parity_integrations.resource_estimation_preview: true`）；实现见仓库 `src/qchem_stack/integrations/resource_estimation_preview.py` 与 `qpe_qec_demo/README.md`。**不**宣称云计价或闭源资源估计 L0。

---

## 2. 显式非目标（P2 仍不包含）

- Quantinuum **真** Nexus / `qnexus` / HQC / OAuth / 配额 / 合同 SLA。
- **任何** 指定量子硬件的校准、原生门集专优、拓扑级编译承诺。
- InQuanto **闭源 wheel**、商业 **Qermit**、**`inquanto-cutensornet`** 二进制 **数值或 API** L0 等价。
- 无公开依据或无机读键的「营销级」精度 / 资源宣称。

---

## 3. 工作分解结构（WBS）

| ID | 工作包 | 交付物 | 验收（闸门要素） |
|----|--------|--------|------------------|
| **P2-W1** | QPE/FT × 资源 × 编译联合叙事 | `run_summary`/`protocol_counts` 与 `CompilerSpec`/TKET 探针字段对齐表；1–2 个 YAML；export 键更新 | `pytest` 相关测；`check_parity_export_sample.py` 抽样覆盖；矩阵/差距表 §1 备注同步 |
| **P2-W2** | 分解：DMET / ONIOM / QM-MM | 除玩具层外可跑的 **最小** 分解 demo（插件或配置驱动）；`repro.embedding_config` 全量可追溯 | 端到端 `run_pipeline_sync` + export；Schmidt/侧车文档更新 |
| **P2-W3** | 经典：CASSCF/AVAS 路径 | 设计文档 + `partial` 机读 caveat；可选 PySCF 扩展钩子 | driver 表面审计单测或脚本；矩阵 §3 行与 gap id 一致 |
| **P2-W4** | 缓解进阶块 | 可选 DAG 节点或协议阶段；`parity_snapshot` 键 | 与 [缓解映射（PMSV / ZNE / Qermit）](/concept/mitigation-mapping) 映射一节同步 |
| **P2-W5** | 映射/ansatz registry 深化 | 文档化 Tangelo 对齐表；BK/SCBK Trotter 决策记录在矩阵 | `test_backend_conformance.py` 或 registry 单测扩展 |
| **P2-W6** | MD/ML | 数据集 YAML + trainer smoke；`repro` 字段冻结 | `pytest -m l1_md_ml` 扩展 |
| **P2-W7** | 教程与 examples | `docs-site` + `examples/` 对齐 CI 钩子 | 贡献指南中列出新入门路径 |

**P2-W1 最小闭环（已钉）**：代表 YAML `configs/example_h2_qpe_track_parity_integrations.yaml`；`export_parity_criteria_table.py --results` → `methods_resource_unified_v1`；回归 `tests/test_methods_resource_unified_export.py::test_methods_resource_unified_qpe_plus_tket_probe_schema`（需 PySCF + pytket）。母稿说明见仓库 `docs/与InQuanto能力差距与实施计划.md`（附录 A） 同段。

依赖：**W1** 可并行 **W5**；**W2** 依赖 P1 嵌入基底；**W3** 依赖 PySCF 可选链；**W6** 可与 **W2** 并行；**W7** 贯穿各波次文档交付。

---

## 4. 建议里程碑（可按组织季度重钉）

| 里程碑 | 目标时段（示意） | 内容 |
|--------|------------------|------|
| **M-P2-a** | Q1 | W1 闭合 + W5 文档/registry；月度台账刷新 |
| **M-P2-b** | Q2 | W2 最小 demo + W4 选一.depth |
| **M-P2-c** | Q3 | W3 路径 + W6 smoke |
| **M-P2-d** | Q4 | W7 打包；残余 `partial` 填入 [Y1 对标台账 §6](/parity/y1-alignment-ledger#y1-residual-partial-sla-template) 或升级 Y3 项 |

（若与 **Y1 台账** Q3/Q4 重叠，以台账 [Y1 对标台账](/parity/y1-alignment-ledger) 季度 OKR 为准，本文 WBS 作二级拆分。）

---

## 5. 出口闸门（每里程碑必选）

1. **`python -m pytest`**（含 parity/export 相关测）全绿。  
2. **`python scripts/check_parity_export_sample.py`** 通过；新增 YAML 加入脚本列表。  
3. **[公开契约矩阵](/parity/public-matrix)** 与 **`inquanto_gap_categories`** 无矛盾；禁止未文档化的 `parity_snapshot` 顶键。  
4. **双站**：仓库 `docs/` 与 `docs-site` 关键入口（路线图、差距计划、L1 signoff）交叉链接更新。  
5. **公开站钉扎**：重大改版记录在 L1 signoff 或台账 §1。

---

## 6. 建议执行顺序（P1 签字后）

与仓库母稿 **`docs/与InQuanto能力差距与实施计划.md`（附录 A） §6** 同表（W1→W7 与 B→J 序 21）；本站不双写，避免漂移。

---

## 7. 相关索引

- 战略总表：[竞争定位与路线图](/concept/competitive-positioning) §5–§6。  
- 差距总表与维护约定：[差距与实施计划](/parity/gap-implementation-plan)。  
- **本站路由**：`/concept/p2-detailed-plan`（VitePress）；修订请以仓库 `docs/与InQuanto能力差距与实施计划.md`（附录 A） 为母稿同步。  
- 维护角色占位：仓库 `CONTRIBUTING.md`（维护角色）。  
- 295 节点 backlog：仓库 `docs/inquanto-node-backlog.generated.json`（波次筛选见 [Y1 对标台账](/parity/y1-alignment-ledger) §3.5）。
- 执行归档：仓库 `docs/execution/`（含 Day12/W2、Day25/45/65/80/90 阶段收口页）。

---

<a id="adr-p2-w2-decomposition-scope"></a>
<a id="p2-w3-avas-casscf-boundary"></a>
<a id="p2-w5-algorithm-registry-alignment"></a>

## 8. 附录 §9–§11（ADR · W3 · W5；正文以仓库母稿为准）

**ADR（P2-W2 分解范围钉扎）、P2-W3（AVAS / CASSCF `partial` 边界）、P2-W5（算法 / ansatz / fermion 映射 registry 三表）** 的**完整技术正文**已并入仓库母稿 **`docs/与InQuanto能力差距与实施计划.md`（附录 A）** 的 **§9、§10、§11**（与 [公开矩阵](/parity/public-matrix) §2–§3 强交叉维护）。本站为防双写漂移**不重复粘贴**长表；请在本地打开该 Markdown 阅读或 PR 修改。

本页保留上述 **三个锚点 id**，供 `fix-internal-links` 与历史链接跳转到「附录入口」；与母稿锚点同名，便于全仓 `grep`。
