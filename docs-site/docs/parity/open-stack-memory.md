# 记忆文档：开放栈 vs InQuanto 对标 — 已落地与待闭合项

**文档性质**：给维护者与未来自己的**决策记忆**（非产品对外白皮书）。口径与 [架构_InQuanto闭源能力闭合与可复现边界.md](/concept/architecture-boundaries) 一致：追求 **L1 公开契约可审计**，不追求 **L0 闭源二进制等价**。

**关联技术说明**：

- [技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot)（DMET 字段、single-fragment 演示、YAML）
- [工程记忆_Quantinuum对标与数据流技术文档.md](/concept/engineering-memory-quantinuum)（模块级数据流）
- [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)（可选 FastAPI、`SqliteJobStore`、`run_context` / `pipeline_profile`）
- [记忆_HTTP_API与作业队列_工程记忆.md](/concept/http-api-worker-memory)（上述层的维护清单与非目标）
- 机读差距：`qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`
- **聚合开放参考单包**：`parity_snapshot.open_gap_closure_reference`（见 `integrations/gap_closure_bundle.py`）

---

## 1. 我们「自己设计」的原则（闭源看不见时）

| 原则 | 含义 |
|------|------|
| 阶段对齐 | SCF → 嵌入标签/意图 → 变分 → Pauli/编译/缓解 → 台账，与公开教程叙事同构 |
| 合同优先 | 用 JSON schema 式字段（`parity_snapshot`、`embedding_workflow`）固定语义，便于审稿与 CI |
| 参考实现可替换 | Protocol/钩子保留；stub 仅用于无 PySCF/无账户的 CI |
| 诚实标注 | `epistemic_binding`、`caveat`、`dmet_solver_mode` 写明假设与不可冒充边界 |

---

## 2. 已在仓库落地的「开源侧」能力（**≠** 对方闭源默认逐比特一致）

以下视为 **开放参考层已全部接通**：每项均有模块、默认或 opt-in 进 `repro.parity_snapshot`，并配有单测或教程 YAML（除非仅文档矩阵）。

| 原「缺口」叙事项 | 开源侧落地 | 说明 |
|------------------|-----------|------|
| Chemically aware UCC | `SinglesBeforeDoublesLexicographic`、`GreedyCommutingFermionicLayers`（OpenFermion commutator 分层）、`ChemicallyAwareUCCPolicy` 仍保留 | 文献可解释重组，**非** InQuanto 内部启发式 |
| TKET 全链 / 编译 | `circuit_ir_tket_peephole_optimize_stats_or_none`（`FullPeepholeOptimise` before/after）、原 `circuit_ir_to_tket_stats_or_none` | **无** 商业离子阱私有 pass |
| Nexus / HQC 工作流 | `nexus_public_workflow_blueprint`、既有 `nexus_cloud` / `nexus_analog` / `qnexus_probe`；**本地**可选 HTTP + `SqliteJobStore`（`api/app.py`，见 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)） | **无** 真计费/队列二进制；HTTP 仅为类比网关，非对方生产 API |
| Qermit | `qermit_mitigation_execution_overlays`、`mitigation_graph_report.execution_class_manifest` | **非** CQCL MitEx/MitRes |
| cuTensorNet / TN 期望 | `tensornet.dense_expectation_reference`（小体系稠密 ⟨ψ|H|ψ⟩）、stub + cuQuantum 探测保持 | **无** 大规模化学 TN 拓扑自动生成 |
| 多片段 DMET | `DMETSelfConsistencyLoop` + **`run_uniform_hamiltonian_multifragment_toy`**（`EmbeddingSpec.dmet_uniform_multifragment_toy=True`） | **非物理** bath：每片段同一全局 H，仅验证多片段循环 |
| Schmidt 嵌入 + 外层 SCF | **`run_schmidt_density_feedback_cycles`**、**`run_schmidt_multifragment_density_cycles`**（`schmidt_multi_fragment_atom_groups`、Gauss–Seidel 扫片）+ 单片段 `schmidt_atomic_production` | **工程**对标 InQuanto DMET *工作流形态*；**非**闭源 bath correlation potential 拟合 |
| L3 统计 | `l3_statistics_reference.energy_bootstrap_ci_stub` | 可重复 bootstrap **示意**，非某台机器标定 |
| COSMO/PBC 驱动 | `open_driver_coverage_matrix` | **声明式**覆盖表 + PySCF 已实现路径 |

**默认进快照的大包**：`ParityIntegrationsSpec.gap_closure_reference_bundle`（默认 `True`）→ `open_gap_closure_reference`（schema `open_gap_closure_reference_v1`）。

此外仍保留：`whole_active_system` 单片段真杂质 VQE、`ParityIntegrationsSpec` 下其余探针、教程链等（见前文档版本）。

---

## 3. **原则上无法由本仓库「做完」的部分（L0 / 商业域）***

下列项在**任何**诚实开源仓库中都不能用「声称完成」来收场，只能合同对齐或测量对标：

- 与 **InQuantuum 闭源 wheel / 未公开 API** 的二进制或秘传超参一致（L0）。
- **真实 HQC 账单、Nexus 生产 SLA、专用服务器侧 MitEx 调度延迟**。
- **与某台 H 系列硬件** 在无人值班条件下的逐 shot 复现（L2/L3 需共同实验协议与原始数据）。

\*若将来对方公开可检证接口，优先增厚 `integrations.*` 与 `parity_snapshot`，而非猜测闭包内行为。

---

## 4. 维护动作备忘

- 能力变化时同步：`inquanto_gap_categories()`、[inquanto_public_parity_matrix.md](/parity/public-matrix)（若行级矩阵变更）。
- 新增 `parity_snapshot` 顶层键时：更新本文 §2、[技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot)（若 DMET 相关）。
- 变更 **HTTP 路由** / **作业表 `meta`** / **`run_context` 头** / **`pipeline_profile`** 时：同步 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs) 与 [记忆_HTTP_API与作业队列_工程记忆.md](/concept/http-api-worker-memory)，并跑 `tests/test_api_runs.py`、`tests/test_job_store_list.py` 等。

---

*最后更新：Schmidt 多轮密度反馈（`schmidt_dmet_density_feedback_v1`）、开放缺口聚合包 `open_gap_closure_reference`、UCC 分层策略、pytket peephole、Nexus 蓝图、Qermit overlay、稠密 TN 期望 API、多片段 toy DMET、L3 bootstrap、驱动矩阵；HTTP/SQLite 队列契约与交叉索引。*
