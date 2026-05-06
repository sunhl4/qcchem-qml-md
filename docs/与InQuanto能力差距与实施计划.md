# 与 InQuanto（公开资料）能力差距与实施计划

**目的**：在 [公开 parity 矩阵](inquanto_public_parity_matrix.md) 与 [竞争定位](竞争定位与路线图_对标Quantinuum产品与技术路线.md) 之外，给出一份**可维护**的「差什么 → 怎么补」清单，并注明**不追求**与闭源或商业云 1:1。实现层机读入口：`qchem_stack.protocols.inquanto_contract`（`classify_pauli_expectation_path`、`inquanto_gap_categories`）。

**按序闭合（B→J，L1 对拍）**：[InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md)

**P2 双月周历（8 周排期）**：[P2_详细实施计划.md](P2_详细实施计划.md) **§8**（与 §6 执行序、§5 闸门配套）。

---

## 1. 差距总表（相对 InQuanto 公开栈）

| 领域 | InQuanto 公开侧 | `qchem_stack` 现状 | 差距性质 |
|------|-----------------|-------------------|----------|
| **云与计费** | Nexus、`qnexus`、HQC | 本地 SQLite + `jobs/cost` + YAML **`nexus_analog`** 单位账；可选 **`nexus_cloud`**（HTTP/ mock 侧车，无厂商 SDK） | **刻意不对齐**真云/真 HQC/合同与配额 |
| **硬件** | H1/H2 等、校准与原生门集叙事 | `BackendSpec` + Qiskit / IonStack mock | 多后端**灵活**、非离子阱专优 |
| **编译** | TKET 默认、chemistry-aware | 可选 [pytket 桥接](技术文档_CircuitIR与TKET桥接及作业契约.md) | **partial**：非默认全链 |
| **对象模型** | `Computable`、丰富 `FermionSpace` 算子图 | `PauliAveragingProtocol` + 流水线函数；**薄层** `protocols/computable.py`（`ComputableRef`、`list_computables_for_config`）与 `workflow-preview` / `repro` round-trip | **partial**：无闭源级独立 `Computable` **产品类**；开放栈以 DAG 预览 + 机读 dict 闭合 L1 |
| **经典化学** | 多 driver（COSMO、PBC、k 点、CASSCF/AVAS 等） | PySCF 主路径；**ddCOSMO**；**PBC**（RHF@Γ 或 **KRHF**+`pbc_kpoint_mesh`；CASCI 用 `pbc_active_space_kpoint_index`；样例 `configs/example_h2_pbc_gamma.yaml`）；**嵌入**：Schmidt 生产 + **`schmidt_bath_sidecar_json_path`**（用户 JSON→`embedding_workflow`）+ **`oniom_layers_v1`** 玩具层（`configs/example_oniom_toy.yaml`）+ `whole_active_system` / DMET / plugin；**projection** L1 轨迹（`configs/example_h2_projection_trace.yaml` 等）；可选 **`chemistry_extended.casscf_orbital_optimization_audit`**（`configs/example_h2_casscf_audit.yaml`，审计能量入 `hamiltonian_meta.pyscf_driver`） | **partial**：无 AVAS/全 CASSCF **产品**深度；PBC+溶剂受 PySCF 版本约束；DMET 非闭源 bath **算法**拟合（已有用户侧车钩子） |
| **Ansatz** | UCC/化学激发池、多化学 ansatz 名 | HEA、ADAPT、**IQEB**（`configs/example_h2_iqeb.yaml`）；**JW UCCSD**（`configs/example_h2_uccsd.yaml`）；**JW UCCSD 一阶 Trotter 层**（`quantum.uccsd_trotter_steps`，`configs/example_h2_uccsd_trotter.yaml`） | **partial**：BK/SCBK 上映射的 UCCSD（含 Trotter）为 **`n/a`**（矩阵 §2）；化学池广度仍不及闭源默认 |
| **缓解** | Qermit `MitRes`/`MitEx` 图与产品运行时 | PMSV/ZNE/SPAM 存根 + **`qermit_analog` DAG 报告** + **`qermit_runtime` 线性执行迹**（`mitigation_dag_execution`）；`MitigationSpec.zne_scales` 与协议 ZNE 对齐；启用 ZNE+Qiskit Pauli 时 **`parity_snapshot.zne_qiskit_unification_v1`**（见 `mitigation_PMSV_ZNE_Qermit_mapping.md`） | **partial**：非 Qermit 商业二进制/调度 |
| **张量网** | `CuTensorNetProtocol` / `inquanto-cutensornet` | **`cutensornet_protocol_stub`** + 引擎探测键（`opt_einsum` / cupy / cuquantum 等）；矩阵与 gap **`tensornet`** 标明 **`n/a`**：不宣称厂商化学尺度收缩 | **`n/a`（开放栈诚实降级）**：保留 stub/钩子供 Methods 对读，**不**验收与 `inquanto-cutensornet` 产品二分等价 |
| **协议 run** | 云侧 shot + DataFrame 一体 | 五阶段 + `protocol_counts` + 三能量路径 | **已较强**：现含 **精确 / statevector 采样 / Qiskit 比特串**（见 [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md)） |
| **激发态 / 谱** | 完整产品线叙事 | VQD/QSE/SCEOM/QPE 模块均为 **partial** | 算法深度与 InQuanto 闭源未逐条对齐 |
| **MD/ML** | 非主宣传 | `md_bridge`、`QMEFDataset` | **本栈长板**（差异化） |

---

## 2. 已机读化字段（本迭代）

- `repro.parity_snapshot` 与 `repro.run_summary` 增加：  
  - `run_qiskit_shots_pauli_protocol`  
  - **`pauli_protocol_expectation_path`**（稳定 token）：`pauli_protocol_disabled` | `exact_executor` | `statevector_grouped_shot_simulation` | `qiskit_get_counts_bitstrings`  
  - 缓解 / 云 / 张量网：`mitigation_zne_scales`（snapshot）、`nexus_cloud` 入 snapshot；管线可写 **`mitigation_dag_execution`**、**`nexus_cloud_repro`**、**`tensornet_protocol_stub`**（见 `orchestration/pipeline.py` 与 `collect_repro_metadata`；导出见 `export_parity_criteria_table.py` 键集）  
  - **HTTP**：`GET /v1/meta/capability-surface` 含 **`open_stack_differentiators`**（`open_stack_differentiators_v1`），钉扎*非云、非专有硬件*下相对公开文档包的可检证长板（与 [parity 矩阵 §0](inquanto_public_parity_matrix.md) 一致）。  
- `export_parity_criteria_table.py` 导出同名字段，便于 Methods 与竞品表对齐。

---

## 3. 分阶段实施计划（与仓库路线图一致）

### P0 维持（可证伪 + CI）— **已落地（持续维护）**

- 判据表导出 **schema v2**：`parity_export_schema_version`、`inquanto_gap_categories`、`computable_abstract`（见 `scripts/export_parity_criteria_table.py`）。  
- CI：pytest、ruff、smoke、sampled、QPE demo、**parity v2 键断言**、**pytket 桥单测**、**`--qiskit-shots` smoke**（`.github/workflows/ci.yml`）。  
- `repro`：`embedding_config` 全量嵌入块 + `parity_snapshot` 扁平字段；**本文**与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 同步。

### P1 中程（提升 partial → 可发表）— **已落地（迭代点见文内差距表）**

1. **嵌入**：`repro.embedding_config` = 全 YAML `EmbeddingSpec`；单测 `test_repro_includes_embedding_config_block`。  
2. **激发态报告**：`excited_resource_summary` / `resource_summary` 含 **`excited_methods_unified`**（schema v1）；export 含 **`excited_resource_from_config`**（仅 YAML，无跑库）。  
3. **PMSV**：`MitigationSpec.pmsv_report_extension` / `pmsv_extra` + `mitigation.pmsv.finalize_pmsv_report` 合并进 `protocol_counts['pmsv_report']`。

**P1 全量核对报告**（竞争定位 P1 行 × L1 × 差距 P1 × parity 摘要 × 建议队列）：[P1_completion_audit.md](P1_completion_audit.md)。

### 主线结构增强（差距文档 §3 批次，已交付）

> 注：此处 **不是** 竞品文档中的路线图 **P2（研究深度）**；路线图 P2 的 WBS 与里程碑见 [P2_详细实施计划.md](P2_详细实施计划.md)。

1. **QPE/容错 与 主 pipeline**：`quantum.qpe_demo_track_after_variational` **或** `quantum.qpe_pipeline_integration` → 输出 `qpe_demo_track`（`qpe_qec_demo.pipeline_track`）；双轨 runnable：`configs/qpe_dual_track_demo.yaml`；传统 Pauli 链上样例仍用 `configs/example_h2_qpe_track.yaml`；`repro.run_summary.qpe_demo_track_ran`。  
2. **Computable 薄层**：`qchem_stack.protocols.computable`（`ComputableRef`、`list_computables_for_config`、`computables_export_dict`），与 `inquanto_contract` 映射联动。  
3. **TKET**：CI 单跑 `tests/test_pytket_bridge.py`（`[dev]` 含 `pytket`）。

### 原「不排期」四项（已转排期并实现 v1 类比）

详见 [不排期项_转排期与实现说明.md](不排期项_转排期与实现说明.md)（**仍非** 商业云与闭源同构；仅本地可审计类比）。

---

## 4. 三周日历：非云、非硬件的「严格对齐」（L1 公开契约）

**范围（本计划明确包含）**：与 InQuanto **公开文档与 API 叙事**在下列维度上做到 **字段级 / 判据级可对表**——Protocol 五阶段、Algorithms 谱系、`repro`/`parity_snapshot`/导出脚本、编译与资源表、缓解（开放类比）、张量网（stub+引擎钩子）、经典化学 driver 表面、激发态与 QPE 演示轨、HTTP/作业队列的产品类比（仍为 **本地**）。

**范围（本计划明确排除 —— 不对齐、不验收）**：Nexus / `qnexus` / HQC 真计费与配额、厂商 OAuth、**任何** 指定量子硬件（H1/H2/Reimei/Helios）的**校准/原生门集/拓扑**行级一致、闭源 wheel 二进制等价（L0）。

**对齐口径（验收哲学）**：

- **L1（本三周的「严格」）**：每个目标项具备 **(a)** 公开文档可追溯的命名或阶段；(b) 本仓 **机读 JSON**（`repro` / export / `inquanto_gap_categories`）中 **键与 schema 固定**；(c) **CI 或脚本** 对已_claim 行做回归；**不**要求与闭源数值或内部启发式一致。  
- **诚实标注**：凡依赖 PySCF 能力边界或开放 stub 处，`parity_snapshot` / `caveat` / `epistemic_binding` 与矩阵 **同步写明**。

### 第 1 周：契约底盘闭合（文档 ↔ 代码 ↔ CI）

| 日段 | 交付物 | 验收标准（DoD） |
|------|--------|----------------|
| D1–D2 | **矩阵与机读表一致** | [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 与 `inquanto_contract.inquanto_gap_categories()`、`INQUANTO_TO_QCHEM_OBJECT_MAP` **两两无矛盾**；任一行 `partial` 须在 gap 或矩阵备注中指明**缺失键或行为**。 |
| D2–D3 | **判据导出 v2 闭环** | `scripts/export_parity_criteria_table.py` 输出字段覆盖 §2 所列 + workflow 新增项（`computable_graph` 声明覆盖、`pipeline_stage` 时间线若导出）；增加或更新 **单测** 防止回归。 |
| D3–D4 | **编译 / TKET 公开叙事** | [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) 与 `parity_integrations.tket_first_circuit_stats` 行为一致；CI 中 pytket 路径 **保持绿**；矩阵「编译」行备注与 `compiler_pass_bundle` gap **一致**。 |
| D4–D5 | **driver 表面审计** | `chem/inquanto_driver_surface` 与矩阵 §3「全量 driver 方法名表」**逐项对勾**：已实现路径标 `yes`，PySCF 受限标 `partial + 约束说明`，**不** 暗示与闭源 inquanto-pyscf 行级等价。 |

**周出口里程碑 M1**：`python -m pytest` 全绿；**parity 矩阵 + gap JSON + export 样例** 三者同源；**无** 未文档化的 `parity_snapshot` 顶键。

### 第 2 周：算法与经典化学「Methods 同构」

| 日段 | 交付物 | 验收标准（DoD） |
|------|--------|----------------|
| D1–D3 | **Algorithms 行级对齐** | 矩阵 §2 每一 `Algorithm*`：`repro.run_summary` 或算法块内具备 **可写入论文** 的 `algorithm`/`meta` 字段集；VQD **三通道**、QSE **shot 模式**、SCEOM **矩阵元噪声语义** 与 [工程记忆](工程记忆_Quantinuum对标与数据流技术文档.md) 一致；**缺项**仅允许以 `caveat` 固定文案出现。 |
| D2–D4 | **ADAPT / IQEB / UCC** | `adapt_meta` / IQEB 导出与公开「变分阶」叙事可对表；UCC：`ChemicallyAwareUCCPolicy` + `integrations/ucc_reference` 在 `open_gap_closure_reference` 或独立 snapshot 行 **显式可见**（非默默存在）。 |
| D4–D5 | **嵌入-first** | DMET / Schmidt / `projection`：`embedding_workflow` + `repro.embedding_config` **覆盖 YAML 全部影响量子子问题的字段**；多轮 Schmidt 密度反馈的 `cycles_executed`/`converged` 等与矩阵叙述一致。 |
| D5 | **PMSV / ZNE 机读** | `protocol_counts['pmsv_report']`、`MitigationSpec.zne_scales`、`mitigation_dag_execution`（若启用）与 [噪声缓解公开叙事](https://docs.quantinuum.com/inquanto/manual/errmit.html) **可对照**（**非** Qermit 二进制）。 |

**周出口里程碑 M2**：任取 **1 个 VQE + 1 个 ADAPT + 1 个含激发态** 的 `configs/`，跑一次完整 `run_pipeline_sync`，`export_parity_criteria_table` **无警告级缺键**（允许的 `caveat` 除外）。

### 第 3 周：Computable / 缓解图式 / 张量网 / QPE 轨 & 总验收

| 日段 | 交付物 | 验收标准（DoD） |
|------|--------|----------------|
| D1–D2 | **Computable 对象薄层（可选 import）** | 提供 **Protocol 或冻结 dataclass**（如 `ComputableSpec`），与 `ComputableRef` / `computable_graph_v2` **双向可转**；`workflow-preview` 可选返回 `computables_rich`（不破坏原 schema）；**不** 承诺执行图与闭源融合顺序一致。 |
| D2–D3 | **Qermit 类比「作业类」清单** | `qermit_analog` + `qermit_runtime`：在 `capability_surface` 或 gap 条目中 **标明** `sync_graph` vs `async_batch` 与 InQuanto MitRes/MitEx **文档对应关系**；缺失项写入矩阵 `partial`。 |
| D3–D4 | **张量网期望** | `tensornet_protocol_stub` + 引擎探测：`parity_snapshot` / `run_summary` 中 **引擎选择与 fallback 原因** 固定键；矩阵 §1 TN 行更新为与实现一致。 |
| D4–D5 | **QPE / Bayesian stub 双轨** | `qpe_demo_track` + `configs/` 样例与 [竞争定位 §5 P2](竞争定位与路线图_对标Quantinuum产品与技术路线.md) 一致；`run_summary` 中 **可检索** QPE 轨是否跑过。 |
| D5 | **总回归与签字** | 跑通：**全 pytest** + **export 脚本全 configs 抽样**（或 CI 已覆盖子集）+ 更新 **本文 §1 表** 中仍标 `partial` 的 **唯一来源** 为 gap id；**云/硬件** 行保持 `n/a` 或「刻意不对齐」不动。 |

**周出口里程碑 M3**：一份 **《三周对齐签字清单》**（可为本节表格勾选版）附在 PR 或内部记录：**排除项外**无「口头对齐、文档未写」的灰色地带。

### 风险与缓冲

- **PySCF / 可选依赖**：CI 主链保持 `skip` 策略清晰；对齐验收以 **schema 与文档** 为主，**不** 强制所有环境跑全化学。  
- **闭源不可见**：任何「严格」仅指 **公开资料可追溯**；若公开文档升级，**维护约定**（§5）触发单轮矩阵修订——不计入三周返工额度，但作为 **版本钉扎**（matrix + `__version__`）。  
- **若三周满了仍有 residual `partial`**：必须 **升格为 gap 条目的 `status` + 预计季度**，禁止长期停在「差不多」。

---

## 5. 维护约定

- 新增长板或关闭差距时：更新 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 相应行、本文 §1、以及 `inquanto_contract.inquanto_gap_categories()`。  
- 论文 Methods：优先引用 `repro.run_summary`、`pauli_protocol_expectation_path`、`protocol_expectation_source`。
- **公开 InQuanto 手册锚定**：维护时记录对照 `https://docs.quantinuum.com/inquanto/` 的日期（与 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md) 钉扎字段一致）；改版后做一次矩阵/机读表 diff 登记。
- **Y1 「非云非硬件」公开面对标执行台账**（季度 OKR、月度度量、文档索引）：[InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md)；L3 数值套件路线：[L3_benchmark_suite_roadmap.md](L3_benchmark_suite_roadmap.md)；年度残余 `partial` SLA：[Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)；**路线图 P2**：[P2_详细实施计划.md](P2_详细实施计划.md)。
- **InQuanto 手册 How-to**：与公开 [How to use](https://docs.quantinuum.com/inquanto/manual/howto.html) 的模块级对齐见 [InQuanto_manual_howto_与_qchem_stack_映射.md](InQuanto_manual_howto_与_qchem_stack_映射.md)。

---

## 6. 路线图 §141 残余项（P2，禁止冒充 P1 `yes`）

与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §141「仍需推进」一致；矩阵未升格前不关闭为 `yes`。**执行细化（WBS、闸门、非目标）** 以 [P2_详细实施计划.md](P2_详细实施计划.md) 为准。

### P2-W3：AVAS / 产品 CASSCF 与「最小审计」分界

- **差距表 §1「经典化学」行**仍标 **`partial`**：无 AVAS；无 InQuanto 级全 CASSCF **产品**深度。  
- **已有机读**：`casscf_orbital_optimization_audit` 仅审计轨道一步（见 `configs/example_h2_casscf_audit.yaml`）。  
- **设计母页**：[P2_W3_classical_avas_casscf_boundary.md](P2_W3_classical_avas_casscf_boundary.md)（与矩阵 §3 同步维护）。

| 阶段（示意） | 主题 | 交付物方向 |
|--------------|------|------------|
| P2 初波 | QPE/FT × 资源 × 编译 | `run_summary` / `protocol_counts` 与 TKET 探针联合叙事；超越 demo 的资源估计可选 |
| P2 初波 | 分解与大体系 | DMET bath 自洽深化；ONIOM/QM-MM **最小可跑** demo（较 §3 已交付玩具层字段更进一步） |
| P2 持续 | 经典深度 / 缓解 / MDML | AVAS/CASSCF 文档化 partial；进阶 mitigation block；`QMEFDataset` 与 trainer smoke |
| 并行 | 教程与 examples | `docs-site`、`examples/`、CI 钩子 |

---

*版本：含 parity export v2、Qiskit shots、原不排期项迭代（Nexus 类比、Qermit 图+运行时、张量网 stub+引擎、PBC/k 点侧）、**§4 三周日历（非云非硬件 L1 严格对齐）**、**§6 P2 backlog（索引至 P2 详细计划）**、与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 表同步。*
