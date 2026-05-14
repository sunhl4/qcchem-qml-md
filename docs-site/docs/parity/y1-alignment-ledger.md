# InQuanto 公开面 Y1 对标台账（非云、非硬件）

**作用**：执行「一年计划」时的**维护台账**（锚定日期、季度 OKR、度量、文档索引）。**不**替代 [inquanto_public_parity_matrix.md](/parity/public-matrix) 与 [与InQuanto能力差距与实施计划.md](/parity/gap-implementation-plan)。

**终局口径（与年度计划一致）**

- **L1+**：除刻意 `n/a` 外，矩阵每行有 gap 锚点 / caveat / 证据链（模块 + 机读键 + 测试或脚本）；残余 `partial` 须有 SLA 或收束为 `yes`。
- **L3（可选）**：`integrations.l3_algorithm_benchmark.L3_PYTEST_YAMLS` 门禁代表（当前 **7**），`QCHEM_RUN_L3=1` + `pytest -m l3`；更全见 `algorithm_benchmark_bundle_v1`。**非**闭源 wheel 数值等价。
- **排除**：真 Nexus/`qnexus`/HQC/OAuth/配额；硬件校准、原生门集专优、拓扑；Qermit/cuTensorNet **商业二进制**等价。

---

## 1. 钉扎与月度 diff

| 字段 | 值 / 动作 |
|------|-----------|
| Quantinuum 公开站 | `https://docs.quantinuum.com/inquanto/` |
| 本次台账起始钉扎 | 2026-04-28（与 [附录 C（L1 签字）](/parity/gap-implementation-plan#appendix-c) 一致） |
| 月度 | 维护人记录当月公开站**是否改版**；若改版 → 更新矩阵/差距表 §5，不自动记为功能回归 |
| **W2 进度（激发态 `run_summary`）** | 已完成：`vqd_three_protocol_present`、`qse_shot_mode`、`qse_shot_noise_model`（条件）、`sceom_*` 写入 `repro.run_summary`；`out["qse"].meta` 含 `qse_shot_mode`；验收见 [工程记忆 §3.1](/concept/engineering-memory-quantinuum) 与 `tests/test_orchestration_pipeline.py` |
| **IQEB / projection L1** | `quantum.algorithm=iqeb`、`configs/example_h2_iqeb.yaml`；`embedding.mode=projection`、`configs/example_h2_projection_trace.yaml`；CI：`smoke_pipeline.py --iqeb` / `--projection-trace` |
| **非云「超越」机读钉扎** | `GET /v1/meta/capability-surface` → **`open_stack_differentiators`**（`open_stack_differentiators_v1`）；矩阵 [§0](/parity/public-matrix) |

---

## 2. 季度 OKR（滚动）

### Q1（月 1–3）：L1 + 算法 export + 嵌入叙事

| 周区间 | 核心交付 | 验收 |
|--------|----------|------|
| W1–W4 | 台账 + `gaps`/`object_map` 与 `GET /v1/meta/capability-surface` 同源；export 黄金样例 | `test_capability_surface_matches_inquanto_contract`；`scripts/check_parity_export_sample.py` |
| W5–W8 | Schmidt / DMET / projection：`run_summary`、export `--results`；矩阵 §3 | `tests/test_schmidt_embedding_production.py` 等 |
| W9–W12 | Protocol resource + computable 表面；矩阵 §1 Computable | workflow-preview API 单测；export 图字段 |

### Q2（月 4–6）：缓解 + TKET 编译路径

- PMSV/ZNE 机读与 [mitigation_PMSV_ZNE_Qermit_mapping.md](/concept/mitigation-mapping) 对 errmit 小节。
- `qermit_analog` / `mitigation_dag_execution` 场景扩充（叙事 + JSON，非商业运行时）。
- `CompilerSpec` + TKET 技术文档与矩阵 `compiler_pass_bundle` 同步。

### Q3（月 7–9）：张量网 + 经典化学深度 + L3 套件

- TN：矩阵与 gap **`tensornet`** 诚实 **`n/a`**（开放 stub）；可选 L3 路线图仍见 **[§7](#l3-benchmark-suite-roadmap)**（原独立 `L3_benchmark_suite_roadmap.md` 已并入）。
- 经典化学：driver/PBC + **最小 CASSCF 审计**（`configs/example_h2_casscf_audit.yaml`）；AVAS/产品 CASSCF **仍为 partial**。

### Q4（月 10–12）：QPE/容错叙事 + 残余清零 + 年度签off

- QPE 与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](/concept/competitive-positioning) P2；`qpe_qec_demo` 与主线 pipeline 配置；`run_summary`/export 全链。
- **[§6 残余 SLA 模板](#y1-residual-partial-sla-template)** 填满或升下年项（原独立 `Y1_residual_partial_SLA_template.md` 已并入）。

---

## 3. 度量（每月末更新）

在下方复制一行并填写：

| 月份 | yes 行数（估算） | partial | n/a | 无 gap 解释的 partial（目标 0） | 备注 |
|------|------------------|---------|-----|----------------------------------|------|
| Y1-M01 | | | | | |
| Y1-M04 | **3** | **14** | **2** | 0 | 广义 P1 闭合；主表计数脚本：`qchem_qml_md/scripts/count_parity_matrix_main_tables.py`；**P2**：[P2 详细实施计划](/concept/p2-detailed-plan)（母稿：`docs/与InQuanto能力差距与实施计划.md`（附录 A）） |

*说明：行数统计以 [parity 矩阵](/parity/public-matrix) 主表 §1–§3 为准；脚本辅助计数，最终以 gap 语义为准。*

---

## 3.5 节点级 backlog（295 manifest 节点）

机读文件位于 **仓库** `qchem_qml_md/docs/`（与本站源码并列，非 VitePress 站内 URL）：`inquanto-node-backlog.generated.json`。再生成：`cd docs-site && npm run report:inquanto-backlog`；门禁：`npm run check:node-backlog`。

- **与矩阵**：矩阵管能力行；backlog 管文档站 IA 节点 — 见仓库内 `docs/与InQuanto能力差距与实施计划.md`（附录 B） §3.5 的 wave / `jq` 示例。
- **深度拆解**：仓库 `docs/architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md`（与 backlog 同源 manifest）。

---

## 4. 每日节奏（全年）

周一：公开文档锚点 + 矩阵当周行；周二：repro/export 契约；周三：实现；周四：单测 + fixture；周五：文档双改 + `pytest` + `scripts/check_parity_export_sample.py`。

---

## 5. 相关路径

- **295 节点机读 backlog**（仓库 `docs/inquanto-node-backlog.generated.json`；`npm run report:inquanto-backlog`）
- 架构边界：[工程记忆 §0](/concept/engineering-memory-quantinuum)（闭源边界）；历史快照：[架构边界页](/concept/architecture-boundaries)
- 竞争策略：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](/concept/competitive-positioning)
- 路线图 P2：[P2 详细实施计划](/concept/p2-detailed-plan)
- **P1 全量核对报告**（仓库）：`qchem_qml_md/docs/与InQuanto能力差距与实施计划.md（附录 E）`
- 签字清单：[附录 C](/parity/gap-implementation-plan#appendix-c)；维护角色：仓库根目录 `CONTRIBUTING.md`

---

<a id="y1-residual-partial-sla-template"></a>

## 6. Y1 残余 `partial` 与 SLA 模板（Q4 / 年度签off）

**用途**：矩阵或差距表中仍为 `partial` 且**本年内未收束为 yes** 的项，必须有一行 SLA，避免「口头对齐」。筛选候选时可用机读 backlog：`jq '.nodes[] | select(.status=="partial")'` 见仓库 `docs/inquanto-node-backlog.generated.json`。

**负责人**：流程角色见仓库 `CONTRIBUTING.md`（维护角色）；表格内可留空或填职能角色。

**合并说明**：原独立文件 `Y1_residual_partial_SLA_template.md` 已并入本节，下表 **全文保留**（含 gap 行、季度与依赖列）。

| gap.id 或矩阵节 | 残余能力摘要 | 目标状态（yes / 仍 partial） | 目标季度 | 负责人 | 依赖（PySCF / GPU / …） |
|------------------|--------------|------------------------------|----------|--------|-------------------------|
| `ucc_chem_ansatz` | 化学 UCC 池与闭源默认非逐条对齐 | partial + JW UCCSD/Trotter YAML | Y1-Q4 | 见 CONTRIBUTING | |
| `tensornet` | TN 化学尺度收缩 | **n/a**（开放栈 stub；不宣称 `inquanto-cutensornet`） | Y2-Q2 | 见 CONTRIBUTING | 见矩阵 [§1](/parity/public-matrix) |
| `drivers_cosmo_pbc` | 全 driver 表面 / 多 k / 溶剂边界 | partial_kmesh | Y1-Q4 | 见 CONTRIBUTING | PySCF 版本；变更 `PYSCF_MIN_VERSION_RECOMMENDED` 时同步矩阵 §3 + `test_inquanto_driver_surface_l1` |
| `composable_computable` | 与闭源 Computable 融合顺序 | rich_optional（workflow-preview） | Y1-Q4 | 见 CONTRIBUTING | |
| `integrations_closure_layer` | 产品默认闭包 | reference_v1 | 长期 | 见 CONTRIBUTING | 仅 L1 |
| `dmet_scf_loop` | 化学意义上完整 DMET bath / 闭源 bath 拟合 | partial + 文档钩子 | Y2-Q1 | 见 CONTRIBUTING | 用户钩子 + Schmidt 生产路径 |
| `qermit_graph`（ZNE×Qiskit） | `circuit_scale_fold` 与 `run_qiskit_shots_pauli_protocol` 合一 | partial + **`zne_qiskit_unification_v1`** 机读块 | Y1-Q4 | 见 CONTRIBUTING | 见 [缓解映射](/concept/mitigation-mapping) |
| `AlgorithmBayesianQPE` / Phayes | 非 Phayes 产品深度 | partial + stub 键 | 长期 | 见 CONTRIBUTING | 公开站 diff 复核 |
| **矩阵 §2 `AlgorithmAdaptVQE`** | pool / 日程与 InQuanto/Tangelo 公开「化学激发池」非逐条对齐 | partial + 文档对照节（parity §2 下「ADAPT 与公开 pool」） | Y2-Q1 | 见 CONTRIBUTING | `tutorial_inquanto_chain_h2.yaml`；`adapt.py` |
| **矩阵 §2 `AlgorithmIQEB`** | IQEB 可选路径；内层 VQE 深度 | partial + 既有 export 键 | Y1-Q4 | 见 CONTRIBUTING | `example_h2_iqeb.yaml` |
| **矩阵 §2 `AlgorithmVQD`** | 三通道报告 vs 闭源多目标叙事 | partial + `l1_excited` CI | Y1-Q4 | 见 CONTRIBUTING | PySCF；`test_qse_sceom_vqd_extended.py` |
| **矩阵 §2 `AlgorithmQSE` / `AlgorithmSCEOM`** | shot 语义与矩阵元噪声 | partial + `l1_excited` CI | Y1-Q4 | 见 CONTRIBUTING | PySCF |
| **矩阵 §2 `Algorithm*QPE`** | 演示轨 + Methods 合一（浅层） | partial；**深度资源估计** → [P2 详细实施计划](/concept/p2-detailed-plan) P2-W1 | Y2-Q1 | 见 CONTRIBUTING | `example_h2_qpe_track.yaml`、`example_h2_qpe_track_parity_integrations.yaml`（pytket） |
| **`http_submit_poll_workspace`** | 本地 FastAPI 类比 vs Nexus UX | partial + caveat 固定 | Y1-Q4 | 见 CONTRIBUTING | `test_api_runs.py` |
| **`compiler_pass_bundle`** | 默认 `CompilerSpec`+CircuitIR；**非**默认全链 TKET | partial + 矩阵 §4「默认 / 可选 pytket」叙事 | Y1-Q4 | 见 CONTRIBUTING | 可选 `pytket`；`test_pytket_bridge.py` |
| **`computables_rich` 入 repro** | `parity_integrations.include_computables_rich_in_repro` | partial；golden 可选 | Y2-Q1 | 见 CONTRIBUTING | `test_workflow_preview_repro_alignment.py` |
| **矩阵 §3 分解插件** | `embedding.mode: plugin` 玩具 demo 与教程互链 | partial + 文档索引 | Y1-Q4 | 见 CONTRIBUTING | `example_decomposition_plugin_toy.yaml`；[case-study-h2-family](/tutorial/case-study-h2-family) |
| **`l1_md_ml` / QMEFDataset** | 长板字段与 `repro` 对齐清单 | partial + CONTRIBUTING 指针 | Y2-Q1 | 见 CONTRIBUTING | `md_bridge/`、`tests/test_md_bridge.py`；见 CONTRIBUTING「CI markers」 |

**签off 规则**

- **云/硬件**：不进入本表（刻意不对齐）。
- **闭源不可检证**：允许长期 `partial`，但须每季度复核公开文档是否新增可检证项。

**年度结束时**：未达标行 → 复制至下年路线图或降级为文档级 `n/a` 并说明原因。

**实施索引**（P1 全量核对后）：队列来源见仓库 `docs/与InQuanto能力差距与实施计划.md`（附录 E） §5。

---

<a id="l3-benchmark-suite-roadmap"></a>

## 7. L3 小体系基准套件（Y1 Q3 交付物 — 路线图）

**目的**：在 **排除云/硬件** 前提下，为「公开面最大对齐」提供 **可重复数值门槛**（不等价 InQuanto 闭源默认）。**合并说明**：原独立文件 `L3_benchmark_suite_roadmap.md` 已并入本节，条文 **全文保留**。

### 7.1 规划项（实施顺序）

1. **基准 1**：H₂ sto-3g，活性 (2e,2o)，VQE+Pauli 协议 — 固定 `random_seed`、`energy_after_variational`、`energy_pauli_protocol` 阈值（见后续 `configs/l3_*.yaml`）。
2. **基准 2**：同上 + `run_sampled_pauli_protocol` 或 Qiskit shots 路径 — 方差/shots 门槛。
3. **基准 3（可选）**：极小 Schmidt 单轮 — `schmidt_dmet_cycles_executed` 与能量一致性与文档断言。

### 7.2 CI 策略

- **主 CI**：仅 schema / config 校验 + **skip** 重型断言。
- **夜间 / 可选 job**：`pytest -m l3`（`QCHEM_RUN_L3=1`，跑 **`L3_PYTEST_YAMLS`**，当前 **7**）跑全量；paper JSON：`scripts/l3_algorithm_benchmark_report.py`。

### 7.3 与 export

跑完后 `export_parity_criteria_table --results out.json` 必须包含文档用键（与 `scripts/export_parity_criteria_table.py` 一致）。

### 7.4 占位单测

见 `tests/test_l3_benchmark_smoke.py`、`integrations/l3_algorithm_benchmark.py`（`L3_PYTEST_YAMLS`）（默认 skip，指针回本节 **[§7](#l3-benchmark-suite-roadmap)**）。
