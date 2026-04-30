# InQuanto 对拍闭合计划（B→J 顺序，`inquanto_public_parity_matrix` / 差距总表）

**权威差距叙述**：[inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)、[与InQuanto能力差距与实施计划.md](与Inquanto能力差距与实施计划.md)。**机读 gap**：`qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`。

---

## 0. 「完美对拍」的严格定义（本计划唯一验收哲学）

本仓库**不**验收与 **InQuanto 闭源 wheel / 内部默认启发式 / 商业 Qermit-cuTensorNet 二进制**的逐比特或逐数值等价（**L0**）。  
**本条计划的「对拍完成」= L1+**（与 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)、[架构_InQuanto闭源能力闭合与可复现边界.md](架构_InQuanto闭源能力闭合与可复现边界.md) 一致）：

| 层级 | 含义 |
|------|------|
| **L1 闭合** | 针对该项：[Quantinuum 公开文档](https://docs.quantinuum.com/inquanto/) 中**可指明的条目**；本仓 **机读 JSON**（`repro` / `parity_snapshot` / `run_summary` / `export_parity_criteria_table` / `GET .../capability-surface`）中 **键与语义固定**；**pytest 或脚本**回归；矩阵行从 `partial` 收束为 **`yes`（诚实 caveat）** 或保持 `partial` 但 **[Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md) 有季度 SLA** |
| **排除** | **A 段（云/HQC/OAuth/配额）**、**硬件专优**：不进入「对拍完成」，维持 `n/a` / 刻意不对齐文案 |
| **不可公开检证** | 任一项无法只用公开资料定义判据的：允许 **长期 `partial`**，但必须 **SLA + epistemic 固定文案** |

**PR 规则**：改行为 → **双改** [parity 矩阵](inquanto_public_parity_matrix.md) 或 gap；动 `parity_snapshot` 顶键 → 更新 `PARITY_SNAPSHOT_DOCUMENTED_KEYS`。

**执行顺序**：下文 **严格按序号 1→N**（对应前答 **B→J** 分项）；每一序号为**可并行子 PR 的一个里程碑**，但**台账上建议按序钉扎**，避免未闭合契约就堆算法特例。

---

## 阶段 B — Protocols 与工作流（矩阵 §1）

| 序 | 对应分项 | 闭源 L0 是否可达 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|------------------|---------|--------|-------------|
| **1** | B1 五阶段 Protocol | 否 | 五阶段语义、三能量路径、异步边界文档与机读一致 | 矩阵 B1 行 caveat 收束；`protocol_counts` / `repro` 时间线字段（若需）与 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md) 一致 | `pytest` 覆盖五阶段 + 至少一条 Qiskit shots 路径 smoke；export 样例无未文档化键 |
| **2** | B2 `dataframe_circuit_shot` | — | **签认 yes** | 矩阵明示 yes；资源行与 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) § 一致 | 现有资源单测 + export `excited_resource` 不回归 |
| **3** | B3 Computable / Methods | 否 | **语义 DAG + YAML 预览 + `computables_rich`（可选）** 与公开「Computable+Protocol」叙事对表；若 API 形态永异：SLA | `computable_graph_v2` 边策略文档化；`POST computables-preview` / `workflow-preview` schema 冻结；缺口写入 gap `composable_computable` | API 单测 + golden export；矩阵 §1 Computable 行更新 |
| **4** | B4 HTTP 作业网关 | 否（非真 Nexus） | **本地类比**能力与限制写死 | [launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md) + ENGINEERING §9 + gap `http_submit_poll_workspace` 同步 | `test_api_runs.py` 覆盖 submit/list/summary/repro；矩阵 **partial** + caveat「无厂商配额」 |
| **5** | B5 Qermit MitRes/MitEx | 否 | **开放 DAG + 线性迹 + `mitigation_execution_model`** 与 [errmit 手册](https://docs.quantinuum.com/inquanto/manual/errmit.html) 公开节对表；MitEx 批量 → SLA | [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) 与 `capability-surface` 同源；ZNE/PMSV 键完整 | gap `qermit_graph` status 与单测；**不宣称**商业 Qermit |
| **6** | B6 CuTensorNet | 否 | **stub + 引擎解析 + `tensornet_engine_resolved`**；化学尺度收缩 → SLA 或 L3 | [L3_benchmark_suite_roadmap.md](L3_benchmark_suite_roadmap.md) 挂钩；矩阵 TN 行与 `tensornet/` 一致 | pytest stub + 可选引擎探测；gap `tensornet` |

---

## 阶段 C — Algorithms（矩阵 §2）

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **7** | C1 VQE | **签认 yes** | 矩阵与签字表维护 | `vqe` 管线 + export |
| **8** | C2 ADAPT | pool / `adapt_meta` 与公开叙事可对表 | [tutorial_inquanto_chain_h2.yaml](../configs/tutorial_inquanto_chain_h2.yaml) 或等价 CI 配置 + 矩阵 caveat | ADAPT 单测 + export 含 `adapt_meta` |
| **9** | C3 IQEB | **非默认**写进矩阵与 YAML 示例 | gap `ucc_chem_ansatz` 旁 IQEB 指针；export `iqeb_implementation_path` | IQEB 单测（已有则签认） |
| **10** | C4 VQD | `run_summary` + `three_protocol`（已部分落地） | [工程记忆 §3.1](工程记忆_Quantinuum对标与数据流技术文档.md) + 矩阵 | `test_orchestration_pipeline` + extended 单测 |
| **11** | C5 QSE | `qse_shot_mode` 与 Pauli 过渡噪声语义机读（已部分落地） | 矩阵 + export `qse_shot_mode_from_run` | pipeline + export merge 单测 |
| **12** | C6 SCEOM | `shot_noise_model` + M 矩阵叙事 | 矩阵 + sceom meta | sceom 单测 + pipeline |
| **13** | C7 QPE | `qpe_demo_track` 与 `run_summary.qpe_demo_track_ran` | `configs/example_h2_qpe_track.yaml` + 竞争定位 P2 | QPE demo pytest |
| **14** | C8 Bayesian/Phayes | stub **公开命名 + repro 键**；深度 → SLA | `qpe_qec_demo` README 片段 + 矩阵 | stub 单测或文档签认 partial |

---

## 阶段 D — 经典化学与嵌入（矩阵 §3）

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **15** | D1 PySCF/JW | **签认 yes** | — | 既有单测 |
| **16** | D2 DMET 框架 | Schmidt 密度反馈 + `cycles_executed` / 钩子 | [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md) + gap `dmet_scf_loop` | Schmidt 生产单测 |
| **17** | D3 Projection | `projection` + YAML 示例 + 矩阵行 | `configs/` 示例 + 嵌入 export | 集成测或文档签认 |
| **18** | D4 Driver 表面 | `inquanto_driver_surface` 与矩阵 **逐项** yes/partial+约束 | 差距表 §「driver 审计」闭环 | driver 表 + PySCF min 版本注释 |
| **19** | D5 Schmidt 多轮叙事 | 与 D2 合并验收；多碎片 sweep | 矩阵 §3 + `embedding_workflow_from_run` | `test_schmidt_embedding_production` |

---

## 阶段 E — 编译 / TKET（矩阵 §4）

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **20** | E1–E3 TKET 链 | `CompilerSpec` + **tket_first 探针**与 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §2–4 **一致**；Ion 专有 routing → **n/a 叙事** | gap `compiler_pass_bundle`；可选默认 `pytket` CI job | `test_tket_compiler_narrative` + `test_pytket_bridge` |

---

## 阶段 F — 对象模型与 Ansatz

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **21** | F1 Computable 薄层 | `ComputableSpec` 或与 `ComputableRef` **双向转换**（§4 三周日历 D1–D2）；**不**承诺闭源融合顺序 | `protocols/computable.py` + workflow-preview 可选 `computables_rich` | 单测 + 矩阵 **`composable_computable` 状态升级** |
| **22** | F2 UCC / 化学池 | `ChemicallyAwareUCCPolicy` + `ucc_reference` 在 **`open_gap_closure_reference` 可见** | [gap_closure_bundle.py](../src/qchem_stack/integrations/gap_closure_bundle.py) + 矩阵 §2 | UCC 计数/导出单测；gap `ucc_chem_ansatz` 备注更新 |

---

## 阶段 G — 协议 run 语义

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **23** | G1 三能量路径 + DataFrame 叙事 | 在 [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md) 与 export 中 **对齐「云侧 shot 叙事」的开放等价物**（非真云） | 矩阵 Protocol 行收束 caveat | `classify_pauli_expectation_path` + parity_export CI |

---

## 阶段 H / I — 激发态产品线自述 + MD/ML

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **24** | H1 激发态谱系 | C10–C14 **汇总签字**；残余算法 → SLA | L1 签字表 §2 全钩 | 一节「激发态总回归」CI（或 nightly） |
| **25** | I1 MD/ML 长板 | **签认差异化** | [竞争定位](竞争定位与路线图_对标Quantinuum产品与技术路线.md) + README | `md_bridge` smoke（若有）或文档签认 |

---

## 阶段 J — `inquanto_gap_categories` 行（与非云软件相关）

在 **序 1–25** 推进中 **同步**更新 gap：**`http_submit_poll_workspace`、`qermit_graph`、`composable_computable`、`evaluate_support_set`、`compiler_pass_bundle`、`ucc_chem_ansatz`、`dmet_scf_loop`、`tensornet`、`integrations_closure_layer`、`drivers_cosmo_pbc`**。  
`qpu_shot_histogram` 已为 **`yes_qiskit`**：序 23 中 **签认**与矩阵 §1–2 一致。

**序 26（总闸）**：`GET /v1/meta/capability-surface` 与 `inquanto_gap_categories()` **逐字段同源**（已有 `test_capability_surface_matches_inquanto_contract`）；**月度**跑 `scripts/check_parity_export_sample.py` + 全 `pytest`。

---

## 台账与季度签 off

- 进度钉扎：[InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md) §3 度量表每月一行；**序 1–26** 完成度映射到「无 unexplained `partial`」。
- 闭源不可达项：一律在 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md) 落表。

---

## 依赖解除声明

若业务方坚持的「完美对拍」= **L0 与 InQuanto 闭包数值/对象同构**，则 **超出本开源仓范围**，须单列商务与法务项；本计划 **不作此类验收**。

---

*版本：与对话中 **B–J 分项** 1:1 对应；维护人按序更新矩阵/gap/SLA。*
