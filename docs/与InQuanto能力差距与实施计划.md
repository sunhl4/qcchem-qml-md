# 与 InQuanto（公开资料）能力差距与实施计划

**目的**：在 [公开 parity 矩阵](inquanto_public_parity_matrix.md) 与 [竞争定位](竞争定位与路线图_对标Quantinuum产品与技术路线.md) 之外，给出一份**可维护**的「差什么 → 怎么补」清单，并注明**不追求**与闭源或商业云 1:1。实现层机读入口：`qchem_stack.protocols.inquanto_contract`（`classify_pauli_expectation_path`、`inquanto_gap_categories`）。

**合并说明**：原独立 `InQuanto_B_J_…`、`P2_详细实施计划`、`L1_…`、`InQuanto_Y1_…`、`P1_completion_audit`、`不排期项` 的正文已并入**本文附录 A–F**；机读锚点 **`#y1-residual-partial-sla-template`**、**`#l3-benchmark-suite-roadmap`**、**`#adr-p2-w2-decomposition-scope`** 等保留在附录内。

**B→J 对拍清单**：**附录 D**。**P2 八周周历**：**附录 A** 内 `### 8.`（闸门见附录 A `### 5.`）。

---

## 1. 差距总表（相对 InQuanto 公开栈）

| 领域 | InQuanto 公开侧 | `qchem_stack` 现状 | 差距性质 |
|------|-----------------|-------------------|----------|
| **云与计费** | Nexus、`qnexus`、HQC | 本地 SQLite + `jobs/cost` + YAML **`nexus_analog`** 单位账；可选 **`nexus_cloud`**（HTTP/ mock 侧车，无厂商 SDK） | **刻意不对齐**真云/真 HQC/合同与配额 |
| **硬件** | H1/H2 等、校准与原生门集叙事 | `BackendSpec` + Qiskit / IonStack mock | 多后端**灵活**、非离子阱专优 |
| **编译** | TKET 默认、chemistry-aware | 可选 [pytket 桥接](技术文档_CircuitIR与TKET桥接及作业契约.md) | **partial**：非默认全链 |
| **对象模型** | `Computable`、丰富 `FermionSpace` 算子图 | `PauliAveragingProtocol` + 流水线函数；**薄层** `protocols/computable.py`（`ComputableRef`、`list_computables_for_config`）与 `workflow-preview` / `repro` round-trip | **partial**：无闭源级独立 `Computable` **产品类**；开放栈以 DAG 预览 + 机读 dict 闭合 L1 |
| **经典化学** | 多 driver（COSMO、PBC、k 点、CASSCF/AVAS 等） | **现阶段端到端数值以 PySCF 收口**（`scf.driver=pyscf`）：**ddCOSMO**；**PBC**（RHF@Γ 或 **KRHF**+`pbc_kpoint_mesh`；CASCI 用 `pbc_active_space_kpoint_index`；样例 `configs/example_h2_pbc_gamma.yaml`）；**多原子** CAS(4,4) 算例 `configs/example_h2o_sto3g_cas44.yaml`、`configs/example_n2_sto3g_cas44.yaml`（仍为 CASCI 型主路径；教程「UCCSD ≤ SCF」见 `examples/tutorial_04_uccsd_below_scf.py` + `configs/example_h2_uccsd.yaml`）；**嵌入**：Schmidt 生产 + **`schmidt_dmet_max_cycles>1`** 时 **Schmidt–DMET 密度反馈**（`integrations/schmidt_dmet_self_consistent` → `repro`/`schmidt_dmet_self_consistency`）+ 通用 **`DMETSelfConsistencyLoop`**（`integrations/dmet_self_consistent`，多轮 bath 仍靠用户钩子）+ **`schmidt_bath_sidecar_json_path`**（用户 JSON→`embedding_workflow`）+ **`oniom_layers_v1`** 玩具层（`configs/example_oniom_toy.yaml`）+ `whole_active_system` / DMET / plugin；**projection** L1 轨迹（`configs/example_h2_projection_trace.yaml` 等）；**活性空间**：**`strategy=avas`**（PySCF **`mcscf.avas.AVAS`**，`configs/example_h2_avas.yaml`，`driver_meta.qchem_active_space_resolution_v1`）；**CASSCF 轨道**：`casscf_orbital_optimization_audit` + **`casscf_orbital_optimization_for_integrals`**（共用单次 **`mcscf.CASSCF` kernel**，`configs/example_h2_casscf_audit.yaml`）。**扩展契约**：`ChemIntegralSolver`/`create_solver`、`ClassicalMeanFieldReference`、`SolverCapabilities`、活性空间 **`mean_field_meta`**、经典基准 registry —— **独立于 PySCF 类名**，便于接入其它程序（路线图陈述见 [竞争定位 §5.1](竞争定位与路线图_对标Quantinuum产品与技术路线.md)）；Psi4 等为 scaffold。 | **partial**：**InQuanto 级默认 AVAS/CASSCF 产品全流程**仍未逐键等价；PySCF **AVAS 阈值投影**与 **CASSCF→活性积分路径**已在主链路可检证接线；PBC+溶剂受 PySCF 版本约束；闭源级 DMET bath **算法** L0 仍不宣称（密度反馈与侧车为工程可检证子集）；多 driver **数值**深度仍以 PySCF 为先 |
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
  - Active-space：`active_space.strategy=cas|manual|avas_stub|avas`（**`strategy=avas`** 仅 `scf.driver=pyscf`，需非空 **`chemistry_extended.avas_ao_labels`**；**`strategy=avas` 以外的** `avas_ao_labels` 仍可 **仅日志**）。**`avas_stub`** 的诚实字段由 **`qchem_stack.chem.active_space.mean_field_meta`** 写入（CAS 同款尺寸语义，**无**阈值投影）。**`strategy=avas`**：管线 **`chem.active_space.pyscf_active_space_hooks`**，`driver_meta` 键 **`qchem_active_space_resolution_v1`**，并回填 YAML `active_space` 尺寸。以上均透传 **`hamiltonian_meta.pyscf_driver`**。  
  - 可选经典 benchmark：`chemistry_extended.classical_benchmark_enabled: true` 时，管线附加 `classical_benchmarks`（schema **`qchem_classical_post_hf_benchmarks_v1`**；**`classical_benchmark_backend`**：`auto|stub|pyscf|psi4`）与 `classical_benchmark_summary`（`classical_benchmark_summary_v1`，含推荐基线策略 `prefer_ccsd_else_mp2_else_hf`），并在 `repro.run_summary` 写入 `classical_bench_*` 与 `classical_benchmark_*` 镜像键。  
  - 分子几何与经典 SCF 扩展：**`MoleculeSpec`**：`ecp`、`zmatrix`（与 `coordinates`/Cartesian **互斥**）；**`SCFSpec`**：`density_fit`、`density_fit_auxbasis` → `driver_meta` 中 `scf_density_fit*`；管线在 `_SCF` 后将非空 **`active_space.frozen_orbitals`** 写入 **`driver_meta.active_space_frozen_orbitals`**，供 CASCI 活性提取使用；**`chemistry_extended.mo_coeff_transform_hook`**（及 `mo_coeff_transform_kwargs`）在 AVAS/CASSCF 细化之后执行，审计块 **`mo_coeff_transform_hook_v1`**。物性/一电子算符为 **PySCF driver 侧 API**（`compute_one_electron_operator_*`），**不等价**闭源同名方法全集；导出键随 `MoleculeSpec`/`ChemistryExtendedSpec` **`model_dump()`** 进入 `export_parity_criteria_table`（见 `parity_export_example_h2_config_only.json` 等 fixtures）。Psi4：**已可**在安装绑定返回 **RHF 总能量占位** MF 结果（仍 **`supports_restricted_active_space_qubit_hamiltonian=False`**）；无 Psi4 时 `compute_mean_field` 报清晰 **import** 原因。  
  - **HTTP**：`GET /v1/meta/capability-surface` 含 **`open_stack_differentiators`**（`open_stack_differentiators_v1`），钉扎*非云、非专有硬件*下相对公开文档包的可检证长板（与 [parity 矩阵 §0](inquanto_public_parity_matrix.md) 一致）；源码证据链在 `protocols/inquanto_contract.py` 的 `open_stack_differentiators_public()`（含 **`mitigation_dag_trace_l1`**、**`iqeb_and_projection_l1_wiring`** 等 `beyond_public_doc_bundle` 条目）。  
- **Export（可选 P2-W1 切片）**：`parity_integrations.resource_estimation_preview: true` 时，`export_parity_criteria_table.py` 顶键 **`resource_estimation_preview_v1`**（`integrations/resource_estimation_preview.py`；config-only 与 `--results` 两模式；**非**云计价 / 非闭源 resource estimator L0）。  
- `export_parity_criteria_table.py` 导出同名字段，便于 Methods 与竞品表对齐。
- 统一经典化学入口维持 **adapter-first**：`create_solver` / registry 是化学后端唯一工厂，编排层分支由 `SolverCapabilities` 判定，不再以 `scf.driver` 品牌字符串硬编码。

---

## 3. 已闭合批次摘要（与仓库路线图一致）

以下批次**不再在本节重复证据链**；维护者只更新 **§1 差距表**、**§2 机读键**、[inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 与本表**状态**，避免与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md)、[工程记忆_Quantinuum对标与数据流技术文档.md](工程记忆_Quantinuum对标与数据流技术文档.md) 三处重复长清单。

| 批次 | 范围（摘要） | 权威证据 / 备注 |
|------|-------------|----------------|
| **P0 维持** | parity export v2、CI、`repro`/`parity_snapshot` 与矩阵同步 | 持续维护；证据交叉见 **附录 E** |
| **P1 中程** | 全量 `embedding_config`、激发态资源统一、PMSV finalize 进 `protocol_counts` | **附录 E**（§2 三条） |
| **主线结构增强** | QPE 演示轨进主 pipeline、Computable 薄层、TKET CI | **附录 E**；**命名上不等于** 竞品路线图 **P2（研究深度）**——WBS/闸门/**附录 A 全文** |
| **原「不排期」四项 v1** | Nexus 类比、Qermit DAG+运行时、张量网 stub、PBC/k 侧等 | **附录 F**（**仍非** 商业云 / 闭源 L0） |

**本轮状态（2026Q2 收口）**：Day12–Day90 连续计划已完成本轮执行与总闸（见 `docs/execution/day90_final_closeout_2026Q2.md`）；路线图 **P2** 仍按 §141 残余项继续推进（WBS/闸门见 **附录 A**），**Y1 台账 / L3 / 年度残余 SLA** 继续按 **附录 B** 维护。
**执行周报（2026Q2）**：`docs/execution/day01_gap_inventory_2026Q2.md` 起持续维护（含 Day8–Day12 连续增量与 Day25/45/65/80/90 里程碑收口页，按日/阶段证据链归档）；下一阶段见 `docs/execution/day91_next_phase_plan_2026Q3.md` 与 `docs/execution/day91_day120_daily_breakdown_2026Q3.md`（Day91-Day97 模板：`day91_template_2026Q3.md`～`day97_template_2026Q3.md`）。

### 3.1 下一步（Day91+，P2 下一阶段）

- **P2-W1 深化**：在 `resource_estimation_preview_v1` 基础上补深度资源估计字段（仍保持非云计价、非闭源 L0 口径）。  
- **P2-W3/W4 组合**：保持 **产品级 AVAS/CASSCF**叙事 **`partial`** 边界表述；补一条可回归的 mitigation 进阶块（优先 ZNE 变体）。  
- **P2-W7→P3 过渡**：教程/examples 索引继续扩充，并维持 docs/docs-site 双站同源更新。  
- **闸门纪律**：继续执行 `pytest` + `check_parity_export_sample.py` + 矩阵/contract/文档三方对齐。  

---

## 4. L1 三周日历（已归档）

原「非云、非硬件、L1 严格对齐」的**按日 DoD 日历**已随 **附录 C** 收口，**不再作为活跃排期表**维护。哲学要点：**L1** = 公开文档可追溯 + 机读键固定 + CI/脚本回归；**排除** Nexus/H 真机与闭源 L0。公开手册改版时按 **§5** 做一次矩阵/机读表 diff 钉扎，而非重开「三周」叙事。

---

## 5. 维护约定

- 新增长板或关闭差距时：更新 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 相应行、本文 §1、以及 `inquanto_contract.inquanto_gap_categories()`。  
- **P1 全量核对**（竞争定位 P1 行 × L1 × parity）：**附录 E**。  
- 论文 Methods：优先引用 `repro.run_summary`、`pauli_protocol_expectation_path`、`protocol_expectation_source`。
- **公开 InQuanto 手册锚定**：维护时记录对照 `https://docs.quantinuum.com/inquanto/` 的日期（与 **附录 C** 钉扎字段一致）；改版后做一次矩阵/机读表 diff 登记。
- **Y1 台账**（季度 OKR、月度度量；**L3**、**残余 `partial` SLA**）：**附录 B**（`#l3-benchmark-suite-roadmap`、`#y1-residual-partial-sla-template`）；**路线图 P2 WBS / ADR**：**附录 A**（`#adr-p2-w2-decomposition-scope` 等）。
- **InQuanto 手册 How-to**：与公开 [How to use](https://docs.quantinuum.com/inquanto/manual/howto.html) 的模块级对齐见 [工程记忆 §14](工程记忆_Quantinuum对标与数据流技术文档.md)。

---

## 6. 路线图 §141 残余项（P2，禁止冒充 P1 `yes`）

与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §141「仍需推进」一致；矩阵未升格前不关闭为 `yes`。**执行细化（WBS、闸门、非目标）** 以 **附录 A** 为准。

### P2-W3：AVAS / 产品 CASSCF 与「最小审计」分界

- **差距表 §1「经典化学」行**仍为 **`partial`**：**InQuanto 级全套「产品默认」AVAS/CASSCF UX**不等于已交付；阈值 **AVAS（PySCF）**与 **单次 CASSCF→积分（可选 audit）**已机读闭环。  
- **已有机读**：`casscf_orbital_optimization_audit`、`casscf_orbital_optimization_for_integrals`（见 `configs/example_h2_casscf_audit.yaml`）；AVAS：`configs/example_h2_avas.yaml` + `parity_snapshot`/export 链路。  
- **设计母页**：**附录 A** 内锚点 [`#p2-w3-avas-casscf-boundary`](与InQuanto能力差距与实施计划.md#p2-w3-avas-casscf-boundary)（与矩阵 §3 同步维护）。

| 阶段（示意） | 主题 | 交付物方向 |
|--------------|------|------------|
| P2 初波 | QPE/FT × 资源 × 编译 | `run_summary` / `protocol_counts` 与 TKET 探针联合叙事；超越 demo 的资源估计可选 |
| P2 初波 | 分解与大体系 | **已接管线**：Schmidt–DMET **密度反馈**（`schmidt_dmet_max_cycles>1` + `schmidt_dmet_self_consistent`）与通用 `DMETSelfConsistencyLoop` 钩子；P2 仍推进 **化学意义上** bath/ONIOM/QM-MM **最小可跑** demo（较 §3 玩具层更进一步） |
| P2 持续 | 经典深度 / 缓解 / MDML | AVAS/CASSCF 文档化 partial；进阶 mitigation block；`QMEFDataset` 与 trainer smoke |
| 并行 | 教程与 examples | `docs-site`、`examples/`、CI 钩子 |

---

<a id="appendix-a"></a>

## 附录 A：P2 详细实施计划（合并收录；原 `P2_详细实施计划.md`）

**文档角色**：在 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §6、§141 残余与 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) 之上，给出 **P2 阶段** 的可执行分解（WBS、里程碑、闸门、非目标）。  
**术语**：本文 **路线图 P2** = 竞品文档中的「研究深度与大体系」阶段；**不等于**「主线结构增强」历史批次（QPE 演示轨接入、Computable 薄层、TKET CI 等——已交付并收进 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) **§3 摘要表**）。

---

### 1. 与 P1 的边界

**P1（广义已闭合）**：L1 公开契约下，`repro` / `parity_snapshot` / export / CI 与矩阵 **`n/a` 诚实降级**（含 TN、BK/SCBK UCCSD Trotter）对齐；UCCSD Trotter（JW）、ZNE 机读合一、Schmidt bath 侧车、ONIOM 玩具层、CASSCF 审计轨道一步、教程与双 parity 等已落地（见竞争定位 §6「已闭合批次」与 [附录 E](与InQuanto能力差距与实施计划.md#appendix-e)）。

**P2 增量**：在 **不冒充闭源 L0**、**不伪造 Nexus/H 系** 前提下，把仍为 **`partial`** 或 **研究级** 的能力推进到「可写 Methods + 可回归 YAML + 文档叙事闭合」，优先：

1. **QPE / 容错叙事 × 资源与编译**：`run_summary` / `protocol_counts` / TKET 探针的联合叙事与固定键；超出 demo 的 resource estimation 可选分支（不先行宣称化学精度优势）。
2. **分解与大体系**：在已有 **Schmidt 密度反馈 + `DMETSelfConsistencyLoop` 钩子** 上深化可发表叙事与最小 demo；**产品向** ONIOM/QM-MM/MI-FNO 或预计算 fragment 输入插件的一条可跑通主线（多于玩具层字段）。
3. **经典电子结构深度**：AVAS / InQuanto 级 CASSCF **不与闭源逐键等价**，但可增加 **文档化 partial 路径** 或社区可替换 driver 钩子。
4. **缓解组合**：在 `qermit_analog` 之外，可选 shadows / 进阶 ZNE 电路放大等 **workflow block**（仍非商业 Qermit）。
5. **映射与 ansatz 广度**：BK/SCBK 上的 UCCSD Trotter 若在矩阵保持 **`n/a`**，则 P2 仅交付 **registry 元数据 + 文档**；若战略升格为 partial 路线，则单独开包与矩阵修订。
6. **MD/ML 产品化**：`QMEFDataset`、主动学习、势函数训练与 `repro` 的稳定字段衔接（竞争定位中的差异化长板）。
7. **社区面**：examples 分离、`docs-site` 教程矩阵扩展、插件模板（对齐竞争定位 **P3** 时可提早启动部分条目）。

---

### 2. 显式非目标（P2 仍不包含）

- Quantinuum **真** Nexus / `qnexus` / HQC / OAuth / 配额 / 合同 SLA。
- **任何** 指定量子硬件的校准、原生门集专优、拓扑级编译承诺。
- InQuanto **闭源 wheel**、商业 **Qermit**、**`inquanto-cutensornet`** 二进制 **数值或 API** L0 等价。
- 无公开依据或无机读键的「营销级」精度 / 资源宣称。

---

### 3. 工作分解结构（WBS）

| ID | 工作包 | 交付物 | 验收（闸门要素） |
|----|--------|--------|------------------|
| **P2-W1** | QPE/FT × 资源 × 编译联合叙事 | `run_summary`/`protocol_counts` 与 `CompilerSpec`/TKET 探针字段对齐表；1–2 个 YAML；export 键更新 | `pytest` 相关测；`check_parity_export_sample.py` 抽样覆盖；矩阵/差距表 §1 备注同步 |
| **P2-W2** | 分解：DMET / ONIOM / QM-MM | 除玩具层外可跑的 **最小** 分解 demo（插件或配置驱动）；`repro.embedding_config` 全量可追溯 | 端到端 `run_pipeline_sync` + export；Schmidt/侧车文档更新 |
| **P2-W3** | 经典：CASSCF/AVAS 路径 | 设计文档 + `partial` 机读 caveat；可选 PySCF 扩展钩子 | driver 表面审计单测或脚本；矩阵 §3 行与 gap id 一致 |
| **P2-W4** | 缓解进阶块 | 可选 DAG 节点或协议阶段；`parity_snapshot` 键 | 与 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) 映射一节同步 |
| **P2-W5** | 映射/ansatz registry 深化 | 文档化 Tangelo 对齐表；BK/SCBK Trotter 决策记录在矩阵 | `test_backend_conformance.py` 或 registry 单测扩展 |
| **P2-W6** | MD/ML | 数据集 YAML + trainer smoke；`repro` 字段冻结 | `pytest -m l1_md_ml` 扩展 |
| **P2-W7** | 教程与 examples | `docs-site` + `examples/` 对齐 CI 钩子 | 贡献指南中列出新入门路径 |

**P2-W1 最小闭环（已钉）**：代表 YAML `configs/example_h2_qpe_track_parity_integrations.yaml`（Pauli 资源 + QPE 轨 + `parity_integrations.tket_first_circuit_stats` + **`parity_integrations.resource_estimation_preview: true`** → export 顶键 **`resource_estimation_preview_v1`**）；`scripts/export_parity_criteria_table.py --results` → `methods_resource_unified_v1`；回归 `tests/test_methods_resource_unified_export.py::test_methods_resource_unified_qpe_plus_tket_probe_schema` 与 **`test_resource_estimation_preview_v1_config_only_export`**（需安装 PySCF 与 pytket 的分支否则 skip）。**说明**：`resource_estimation_preview_v1` 为浅层 Methods 切片；§6 序 1「resource estimation 可选分支**扩展**」指更深指标/叙事，而非从零新增该顶键。

依赖：**W1** 可并行 **W5**；**W2** 依赖 P1 嵌入基底；**W3** 依赖 PySCF 可选链；**W6** 可与 **W2** 并行；**W7** 贯穿各波次文档交付。

---

### 4. 建议里程碑（可按组织季度重钉）

| 里程碑 | 目标时段（示意） | 内容 |
|--------|------------------|------|
| **M-P2-a** | Q1 | W1 闭合 + W5 文档/registry；月度台账刷新 |
| **M-P2-b** | Q2 | W2 最小 demo + W4 选一.depth |
| **M-P2-c** | Q3 | W3 路径 + W6 smoke |
| **M-P2-d** | Q4 | W7 打包；残余 `partial` 填入 [附录 B §6](与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 或升级 Y3 项 |

（若与 **Y1 台账** Q3/Q4 重叠，以台账 [附录 B](与InQuanto能力差距与实施计划.md#appendix-b) 季度 OKR 为准，本文 WBS 作二级拆分。）

---

### 5. 出口闸门（每里程碑必选）

1. **`python -m pytest`**（含 parity/export 相关测）全绿。  
2. **`python scripts/check_parity_export_sample.py`** 通过；新增 YAML 加入脚本列表。  
3. **[inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)** 与 **`inquanto_gap_categories`** 无矛盾；禁止未文档化的 `parity_snapshot` 顶键。  
4. **双站**：仓库 `docs/` 与 `docs-site` 关键入口（路线图、差距计划、L1 signoff）交叉链接更新。  
5. **公开站钉扎**：重大改版记录在 L1 signoff 或台账 §1。

---

### 6. 建议执行顺序（P1 签字后的首轮实施）

以下按 **依赖少 → 可并行 → 风险可控** 排序；与 [附录 E](与InQuanto能力差距与实施计划.md#appendix-e) §6 衔接。每步结束仍走 **§5 出口闸门**（pytest 全量、`check_parity_export_sample`、矩阵 ↔ gap、双站链接）。

| 序 | 工作包 | 具体动作（可拆 PR） | 并行关系 |
|----|--------|---------------------|----------|
| **1** | **P2-W1 深化** | 在已有 **`resource_estimation_preview_v1`** 上扩展 **resource estimation 叙事/字段**（新键须注册 `inquanto_contract`）；矩阵 §2 QPE 行 + 差距表 §1 备注同步；单测沿用 `test_methods_resource_unified_export.py` 家族 | 可与 **5** 并行 |
| **2** | **P2-W1 文档** | `qpe_qec_demo/README.md` + docs-site `p2-detailed-plan` 英中页各增一节「深度 vs P1 演示轨」 | 依赖 **1** 的键名冻结 |
| **3** | **P2-W5** | Tangelo/公开算法 **registry 对照表**（Markdown 表）；BK/SCBK Trotter 若仍 **n/a**，只补文档不升格矩阵 | 与 **1** 并行 |
| **4** | **P2-W2 范围钉扎** | Issue/ADR：最小可跑分解 demo 选 **ONIOM 插件路径** 或 **预计算 fragment 输入** 二选一；更新 `dmet_scf_loop` / embedding gap 叙事 | 可与 **1** 并行 |
| **5** | **P2-W6 起步** | `QMEFDataset` + 一条 `repro` 字段冻结清单（YAML 或 contract 注释）；扩展 `pytest -m l1_md_ml` 一条 smoke | 与 **1** 并行 |
| **6** | **P2-W3** | AVAS/产品 CASSCF：设计文档 + `partial` caveat 机读字段（不宣称 L0）；driver 表面单测若触及新键则同步矩阵 §3 | 依赖 PySCF 可选链 |
| **7** | **P2-W4** | 在 `mitigation_PMSV_ZNE_Qermit_mapping.md` 选一 **进阶块**（shadows 或 ZNE 变体）做 DAG 或 `parity_snapshot` 增量 | 可与 **6** 并行 |
| **8** | **P2-W7** | examples 与 docs-site 教程 **索引表**（新用户三条路径）；CONTRIBUTING 链到该表 | 贯穿，可在 **2** 后收尾 |
| **9** | **B→J 序 21 / computable 深度** | `ComputableRef` ↔ workflow-preview **双向**单测 + 最小互转 API（若产品需要）；否则维持 SLA「长期 partial」 | 中高成本，可压到 M-P2-c 后 |

**抽样 CI**：`scripts/check_parity_export_sample.py` 已含 DMET fragment、QPE track、CASSCF audit、embedding parity 等代表 YAML，并已加入 **几何/SCF 扩展**抽样（**RI/DF**、**zmatrix**、**ECP** 及组合：`example_h2_sto3g_density_fit` / `example_h2_zmatrix_sto3g*` / `example_mg_lanl2dz_ecp_*` / `example_hbr_zmatrix_lanl2dz_ecp_density_fit`，见脚本 `SAMPLE_CONFIGS_REL`）；新增 P2 驱动配置时继续扩展该列表。

---

### 7. 相关索引

- **文档总索引**（母稿全表、合并记录、阅读顺序）：[README.md](../README.md) 与 [CONTRIBUTING.md](../CONTRIBUTING.md)。  
- 战略总表：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §5–§6。  
- 差距总表与维护约定：[与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)。  
- **文档站镜像（VitePress）**：中文全文路由 `/concept/p2-detailed-plan`，英文摘要 `/en/concept/p2-detailed-plan`（`npm run docs:dev` / `docs:build` 生成站点内路径）。  
- **P2-W5（registry）**、**ADR（P2-W2 分解范围）**、**P2-W3（经典边界）**：见本节 **§9–§11**（[§9 ADR](#adr-p2-w2-decomposition-scope) · [§10 W3](#p2-w3-avas-casscf-boundary) · [§11 W5](#p2-w5-algorithm-registry-alignment)；原独立 `ADR_P2_decomposition_scope.md`、`P2_W3_classical_avas_casscf_boundary.md`、`P2_W5_algorithm_registry_alignment.md` 已并入，技术表与决策 **全文保留**）。**MD 冻结**：[工程记忆 §16](工程记忆_Quantinuum对标与数据流技术文档.md)。  
- 维护角色占位：[CONTRIBUTING.md](../CONTRIBUTING.md)。  
- 295 节点 backlog：`docs/inquanto-node-backlog.generated.json`（波次筛选见台账 §3.5）。

---

### 8. 双月执行日历（8 周；钉扎用）

**用途**：把 §6 执行序落到 **可排期周历**；起止日期由维护人在台账「当周」行填写。**闸门**：每两周至少跑 §5 五项一次（`pytest`、`check_parity_export_sample`、矩阵 ↔ gap、双站、公开站钉扎记录）。

| 周次 | 日历占位（填写实际起止） | 主题 | 交付物索引 |
|------|---------------------------|------|------------|
| **1–2** | `YYYY-MM-DD` ~ `YYYY-MM-DD` | 并行打底 | 本节 **[§11](#p2-w5-algorithm-registry-alignment)**（registry）、**[§9](#adr-p2-w2-decomposition-scope)**（ADR）；[工程记忆 §16](工程记忆_Quantinuum对标与数据流技术文档.md)；文档站 [新用户三条路径](/guide/onboarding-three-paths) |
| **3–4** | `YYYY-MM-DD` ~ `YYYY-MM-DD` | P2-W1 最小代码 | `export_parity_criteria_table` 顶键 **`resource_estimation_preview_v1`**（`parity_integrations.resource_estimation_preview`）；`tests/test_methods_resource_unified_export.py` |
| **5–6** | `YYYY-MM-DD` ~ `YYYY-MM-DD` | P2-W3 + W4 | 差距表 / 矩阵 §3 AVAS–CASSCF 边界（本节 **[§10](#p2-w3-avas-casscf-boundary)**）；[mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) §「P2 进阶块（双月）」 |
| **7–8** | `YYYY-MM-DD` ~ `YYYY-MM-DD` | 收口 + 可选 B→J-21 | `qpe_qec_demo/README.md`；docs-site「深度 vs P1」；`tests/test_computable_roundtrip_minimal.py`（若启用） |

**关联母稿**：§6 序 1–9 与上表逐行对应；[附录 E](与InQuanto能力差距与实施计划.md#appendix-e) §6 声明 P1 已闭合后从 **本表第 1 行** 开工。

---

<a id="adr-p2-w2-decomposition-scope"></a>

### 9. ADR：P2-W2 分解与大体系 — 最小可跑 demo 范围钉扎

**状态**：已接受（文档 ADR，2026-05-07）。**母稿**：上文 §6 序 4、§8 第 1–2 周。**合并说明**：原独立文件 `ADR_P2_decomposition_scope.md` 已并入本节，正文与决策表 **全文保留**。

### 9.1 背景

P2 需在「不冒充 InQuanto 闭源分解产品」前提下，选一条 **最小可跑** 的分解 / 大体系增量（ONIOM、QM-MM、MI-FNO、预计算 fragment 等叙事并存）。

### 9.2 决策

1. **双轨保留，双月内只深做一轨**  
   - **轨 A — ONIOM / 层场玩具 → 可插拔层元数据**：继续以 `embedding.oniom_layers_v1` + `configs/example_oniom_toy.yaml` 为基线；P2 代码增量优先落在 **文档化插件边界**（`embedding.mode: plugin` + 已有 toy YAML），不宣称全文献 ONIOM 能量一致。  
   - **轨 B — 预计算 fragment / 用户 bath**：继续以 `schmidt_bath_sidecar_json_path` + DMET fragment exact 小体系为基线；全文献 DMET bath 自洽 **不** 在本 ADR 内承诺为 `yes`。

2. **本双月默认优先级**：**轨 A（插件 + 层元数据路径）** 先于轨 B 扩代码；轨 B 以 **gap `dmet_scf_loop` 文档 + 侧车** 收束，避免并行两套大改。

3. **非目标（重申）**：真 Nexus；闭源 ONIOM/QM-MM **数值** L0；无 `repro` 机读键的新「营销级」分解宣称。

### 9.3 后果

- 差距表与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §3 **DMET / embedding** 行保持 **`partial`**，本 ADR 作为 caveat 引用。  
- 若产品方强制轨 B，需 **新开 ADR** 修订优先级并更新 [附录 B §6](与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 对应行季度。

### 9.4 链接（ADR）

- [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §1 经典化学 / Ansatz。  
- [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md)。

---

<a id="p2-w3-avas-casscf-boundary"></a>

### 10. P2-W3：AVAS / 产品级 CASSCF — 与开放栈 `partial` 边界

**母稿**：上文 §6 序 6、§8 第 5–6 周。**合并说明**：原独立文件 `P2_W3_classical_avas_casscf_boundary.md` 已并入本节，表格 **全文保留**。

### 10.1 已交付（诚实 `partial`，非 L0）

| 能力 | 机读 / 配置 | 说明 |
|------|-------------|------|
| **PySCF AVAS（阈值投影 + 回填 ncas/nelec）** | `active_space.strategy=avas` + `chem.active_space.mean_field_meta` / `chem.active_space.pyscf_active_space_hooks`；`configs/example_h2_avas.yaml`；能力位 **`supports_avas_active_space_projection`** | 将 **`mcscf.avas.AVAS`** 输出的 **`mo_coeff`** 接到 CASCI 型活性积分；写入 **`qchem_active_space_resolution_v1`**；与 InQuanto **封闭产品 driver 全流程**仍为 **语义 partial** |
| **一步 CASSCF → 可选活性积分 orbitals** | `chemistry_extended.casscf_orbital_optimization_for_integrals`（与 **`casscf_orbital_optimization_audit`** 共用 kernel） | 可选将 **`mcscf.CASSCF`** 优化 **`mo_coeff`** 接到 CASCI 提取；audit 仍为 `casscf_orbital_audit_v1` |
| **一步 CASSCF 轨道优化审计** | `chemistry_extended.casscf_orbital_optimization_audit`；`configs/example_h2_casscf_audit.yaml` | 同上共享 kernel：`casscf_orbital_audit_v1` |
| **CASCI 默认变分哈密顿量** | 主 `pipeline` 路径 | 变分阶段默认 CASCI 型积分；可与上两行组合 |

### 10.2 未交付（仍为差距表 **`partial`** 的含义）

- **InQuanto 级「产品预设」**：闭源 **`ChemistryDriver*`** 上捆绑的 UX、默认值、frozen/avas 自动生成与全流程教程 **不** 逐键复刻。  
- **InQuanto 级 CASSCF 产品**：多步轨道迭代、活性空间自洽与厂商默认 orchestration **不** 等价于本节「单次内核 + YAML 钩子」。  

### 10.3 维护动作

- 矩阵 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §3「PySCF / active space」行与本节一致时即视为文档闭合。  
- 若扩展 PySCF 可选链：同步 [chem/inquanto_driver_surface.py](../src/qchem_stack/chem/inquanto_driver_surface.py) 与 `tests/test_inquanto_driver_surface_l1.py`。

---

<a id="p2-w5-algorithm-registry-alignment"></a>

### 11. P2-W5：公开算法 / ansatz / 映射 — 机读 registry 对照（Tangelo / InQuanto 叙事）

**角色**：把「研究包里常见的算法名」钉到本仓 **registry 模块**与 **parity 矩阵 §2**，避免口头对齐。不声称与闭源类名 L0 同构。**母稿**：上文 §6 序 3、§8 第 1–2 周。**合并说明**：原独立文件 `P2_W5_algorithm_registry_alignment.md` 已并入本节，各表 **全文保留**。

### 11.1 YAML `quantum.algorithm`（`ALGORITHM_REGISTRY`）

| Registry `id` | 实现入口（摘要） | 公开文档类比（叙事级） |
|-----------------|------------------|-------------------------|
| `vqe` | `quantum.algorithms.vqe.VQE` | 通用 VQE / HEA 变分层 |
| `adapt` | `adapt.FermionicAdaptVQE` | ADAPT-VQE；pool 与日程见 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §2 |
| `iqeb` | `iqeb.IQEBVQE` | IQEB 类外环；`configs/example_h2_iqeb.yaml` |

源码：`src/qchem_stack/quantum/algorithm_registry.py`。

### 11.2 变分 ansatz 名（`ANSATZ_REGISTRY`）

| Registry `id` | 说明 |
|-----------------|------|
| `hea` | HEA 深度由 `quantum.vqe_depth` |
| `uccsd` | JW 参考态 UCCSD（`UCCSDVQE`） |
| `fermionic_adapt` | ADAPT 池驱动 |
| `iqeb` | IQEB 与算法键一致 |
| `uccsd_closed_shell_reference` | 激发计数 / bookkeeping 入 `parity_snapshot`，主线仍可 HEA |
| `trotter_ucc_placeholder` | JW + `quantum.uccsd_trotter_steps` → `UCCSDTrotterVQE`；**BK/SCBK 上 UCCSD Trotter 仍为矩阵 `n/a`** |

源码：`src/qchem_stack/quantum/ansatz_registry.py`。

### 11.3 Fermion→qubit 映射（`DOCUMENTED_FERMION_QUBIT_MAPPINGS`）

| 映射名 | 备注 |
|--------|------|
| `jordan_wigner` | 默认 |
| `bravyi_kitaev` | 全栈 Hamiltonian 构建 |
| `symmetry_conserving_bravyi_kitaev` | OpenFermion SCBK |

源码：`src/qchem_stack/chem/fermion_mapping_registry.py`；conformance：`tests/test_backend_conformance.py`。

### 11.4 维护

- 新增 registry 键：同步本表 + [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §2（若影响对外叙事）+ `export_parity_criteria_table` 稳定列（若导出暴露名称）。  
- P2 双月闸门见上文 **§5**。


---

<a id="appendix-b"></a>

## 附录 B：Y1 对标台账（合并收录；原 `InQuanto_Y1_public_alignment_ledger.md`）

**作用**：执行「一年计划」时的**维护台账**（锚定日期、季度 OKR、度量、文档索引）。**不**替代 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 与 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)。

**终局口径（与年度计划一致）**

- **L1+**：除刻意 `n/a` 外，矩阵每行有 gap 锚点 / caveat / 证据链（模块 + 机读键 + 测试或脚本）；残余 `partial` 须有 SLA 或收束为 `yes`。
- **L3（可选）**：`integrations.l3_algorithm_benchmark.L3_PYTEST_YAMLS` 为代表门禁集（当前 **6**：`QCHEM_RUN_L3=1` + `pytest -m l3`）；更宽默认见 `DEFAULT_BENCHMARK_YAMLS`（`algorithm_benchmark_bundle_v1` / `scripts/l3_algorithm_benchmark_report.py`）。**非**闭源 wheel 数值等价。
- **排除**：真 Nexus/`qnexus`/HQC/OAuth/配额；硬件校准、原生门集专优、拓扑；Qermit/cuTensorNet **商业二进制**等价。

---

### 1. 钉扎与月度 diff

| 字段 | 值 / 动作 |
|------|-----------|
| Quantinuum 公开站 | `https://docs.quantinuum.com/inquanto/` |
| 本次台账起始钉扎 | 2026-04-28（与 [附录 C](与InQuanto能力差距与实施计划.md#appendix-c) 一致） |
| 月度 | 维护人记录当月公开站**是否改版**；若改版 → 更新矩阵/差距表 §5，不自动记为功能回归 |
| **W2 进度（激发态 `run_summary`）** | 已完成：`vqd_three_protocol_present`、`qse_shot_mode`、`qse_shot_noise_model`（条件）、`sceom_*` 写入 `repro.run_summary`；`out["qse"].meta` 含 `qse_shot_mode`；验收见 [工程记忆 §3.1](工程记忆_Quantinuum对标与数据流技术文档.md) 与 `tests/test_orchestration_pipeline.py` |
| **IQEB / projection L1** | `quantum.algorithm=iqeb` + `configs/example_h2_iqeb.yaml`；`embedding.mode=projection` + `configs/example_h2_projection_trace.yaml`；CI：`smoke_pipeline.py --iqeb` / `--projection-trace`；`PARITY_SNAPSHOT_DOCUMENTED_KEYS` 含 `iqeb_max_rounds`、`projection_embedding_open_trace` |
| **非云「超越」机读钉扎** | `GET /v1/meta/capability-surface` → **`open_stack_differentiators`**（`open_stack_differentiators_v1`）；矩阵 [§0](inquanto_public_parity_matrix.md) 与 [竞争定位 §3 卖点 6](竞争定位与路线图_对标Quantinuum产品与技术路线.md) |
| **P2 双月周历（8 周）** | 排期与周交付物见 [附录 A](与InQuanto能力差距与实施计划.md#appendix-a) **§8**；与 §6 执行序同源，季度 OKR 可引用 §8 行作为子任务 |

---

### 2. 季度 OKR（滚动）

### Q1（月 1–3）：L1 + 算法 export + 嵌入叙事

| 周区间 | 核心交付 | 验收 |
|--------|----------|------|
| W1–W4 | 台账 + `gaps`/`object_map` 与 `GET /v1/meta/capability-surface` 同源；export 黄金样例 | `test_capability_surface_matches_inquanto_contract`；`scripts/check_parity_export_sample.py` |
| W5–W8 | Schmidt / DMET / projection：`run_summary`、export `--results`；矩阵 §3 | `tests/test_schmidt_embedding_production.py` 等 |
| W9–W12 | Protocol resource + computable 表面；矩阵 §1 Computable | workflow-preview API 单测；export 图字段 |

### Q2（月 4–6）：缓解 + TKET 编译路径

- PMSV/ZNE 机读与 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) 对 errmit 小节。
- `qermit_analog` / `mitigation_dag_execution` 场景扩充（叙事 + JSON，非商业运行时）。
- `CompilerSpec` + TKET 技术文档与矩阵 `compiler_pass_bundle` 同步。

### Q3（月 7–9）：张量网 + 经典化学深度 + L3 套件

- TN：矩阵与 gap **`tensornet`** 诚实 **`n/a`**（开放 stub，不宣称 `inquanto-cutensornet`）；可选环境里 L3 交叉检仍见 **[§7](#l3-benchmark-suite-roadmap)**（原 `L3_benchmark_suite_roadmap.md` 已并入）。
- 经典化学：driver/PBC + **最小 CASSCF 审计**（`configs/example_h2_casscf_audit.yaml`）；AVAS/产品 CASSCF **仍为 partial**。

### Q4（月 10–12）：QPE/容错叙事 + 残余清零 + 年度签off

- QPE 与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) P2；`qpe_qec_demo` 与主线 pipeline 配置；`run_summary`/export 全链。
- **[§6 残余 SLA 模板](#y1-residual-partial-sla-template)** 填满或升下年项（原独立 `Y1_residual_partial_SLA_template.md` 已并入）。

---

### 3. 度量（每月末更新）

在下方复制一行并填写：

| 月份 | yes 行数（估算） | partial | n/a | 无 gap 解释的 partial（目标 0） | 备注 |
|------|------------------|---------|-----|----------------------------------|------|
| Y1-M01 | | | | | |
| Y1-M04 | **3** | **14** | **2**（含 `tensornet`→矩阵/`gap` **n/a**） | 0 | **广义 P1 排期闭合**；主表 §1–§3 行计数见 `python scripts/count_parity_matrix_main_tables.py`（示例输出：`yes=3 partial=14 n/a=2`，与手填冲突时以 gap 语义为准）；后续路线图见 [附录 A](与InQuanto能力差距与实施计划.md#appendix-a) |

*说明：行数统计以 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 主表 §1–§3 为准；脚本辅助计数，主观分类仍以 `inquanto_gap_categories` 与矩阵备注为准。*

---

### 3.5 节点级 backlog（295 manifest 节点）

**与矩阵的关系**：parity 矩阵按 **能力 / 模块行** 收敛；[`inquanto-node-backlog.generated.json`](inquanto-node-backlog.generated.json) 按 **InQuanto 公开 IA 节点（manifest 叶 + 类叶）** 展开，字段含附录 C 同构的 **验收项、平台维度、`differentiator_focus`**。二者通过 `qchem_module` 与 `parity_doc_hint` 弱关联。

**再生成**（仓库根 `qchem_qml_md/docs-site/`）：

```bash
npm run report:inquanto-backlog
npm run check:node-backlog
```

**按 wave 筛选（机读）**：用 `jq` 对 JSON 过滤，例如 **W0（云叙事 + meta）** — `differentiator_focus` 含 `cloud_tenant`：

```bash
jq '.nodes[] | select(.differentiator_focus | index("cloud_tenant")) | .breadcrumb | join("/")' docs/inquanto-node-backlog.generated.json
```

**W1（P2 shipped 非类叶）** 示例：

```bash
jq '.nodes[] | select(.pillar=="P2" and .status=="shipped" and .is_class_leaf==false) | .appendix_c_node_index' docs/inquanto-node-backlog.generated.json
```

**人读索引表**：[inquanto-node-backlog.generated.md](inquanto-node-backlog.generated.md)。**深度拆解**仍读架构报告 [appendix-C-deep-node-architecture.generated.md](architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md)。

---

### 4. 每日节奏（全年）

周一：公开文档锚点 + 矩阵当周行；周二：repro/export 契约；周三：实现；周四：单测 + fixture；周五：文档双改 + `pytest` + `scripts/check_parity_export_sample.py`。

---

### 5. 相关路径

- **295 节点机读 backlog**：[`inquanto-node-backlog.generated.json`](inquanto-node-backlog.generated.json) · [Schema](inquanto-node-backlog.schema.json)
- **InQuanto B→J 逐项闭合计划（L1 序列表 + DoD）**：[附录 D](与InQuanto能力差距与实施计划.md#appendix-d)
- **公开手册 How-to（功能参考）**：[工程记忆 §14](工程记忆_Quantinuum对标与数据流技术文档.md)（锚 [How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html)）
- 架构边界：[工程记忆 §0](工程记忆_Quantinuum对标与数据流技术文档.md)
- 竞争策略：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md)
- 签字清单：[附录 C](与InQuanto能力差距与实施计划.md#appendix-c)；维护角色：[CONTRIBUTING.md](../CONTRIBUTING.md)
- **P1 全量核对报告**：[附录 E](与InQuanto能力差距与实施计划.md#appendix-e)

---

<a id="y1-residual-partial-sla-template"></a>

### 6. Y1 残余 `partial` 与 SLA 模板（Q4 / 年度签off）

**用途**：矩阵或差距表中仍为 `partial` 且**本年内未收束为 yes** 的项，必须有一行 SLA，避免「口头对齐」。筛选候选时可用机读 backlog：`jq '.nodes[] | select(.status=="partial")'` 见 `docs/inquanto-node-backlog.generated.json`。

**负责人**：流程角色见 [CONTRIBUTING.md](../CONTRIBUTING.md)；表格内可留空或填职能角色。

**合并说明**：原独立文件 `Y1_residual_partial_SLA_template.md` 已并入本节，下表 **全文保留**（含 gap 行、季度与依赖列）。

| gap.id 或矩阵节 | 残余能力摘要 | 目标状态（yes / 仍 partial） | 目标季度 | 负责人 | 依赖（PySCF / GPU / …） |
|------------------|--------------|------------------------------|----------|--------|-------------------------|
| `ucc_chem_ansatz` | 化学 UCC 池与闭源默认非逐条对齐 | partial + JW UCCSD/Trotter YAML | Y1-Q4 | 见 CONTRIBUTING | |
| `tensornet` | TN 化学尺度收缩 | **n/a**（开放栈 stub；不宣称 `inquanto-cutensornet`） | Y2-Q2 | 见 CONTRIBUTING | 见矩阵 §1 |
| `drivers_cosmo_pbc` | 全 driver 表面 / 多 k / 溶剂边界 | partial_kmesh | Y1-Q4 | 见 CONTRIBUTING | PySCF 版本；变更 `PYSCF_MIN_VERSION_RECOMMENDED` 时同步矩阵 §3 + `test_inquanto_driver_surface_l1` |
| `composable_computable` | 与闭源 Computable 融合顺序 | rich_optional（workflow-preview） | Y1-Q4 | 见 CONTRIBUTING | |
| `integrations_closure_layer` | 产品默认闭包 | reference_v1 | 长期 | 见 CONTRIBUTING | 仅 L1 |
| `dmet_scf_loop` | 化学意义上完整 DMET bath / 闭源 bath 拟合 | partial + 文档钩子 | Y2-Q1 | 见 CONTRIBUTING | 用户钩子 + Schmidt 生产路径 |
| `qermit_graph`（ZNE×Qiskit） | `circuit_scale_fold` 与 `run_qiskit_shots_pauli_protocol` 合一 | partial + **`zne_qiskit_unification_v1`** 机读块 | Y1-Q4 | 见 CONTRIBUTING | 见 `mitigation_PMSV_ZNE_Qermit_mapping.md` |
| `AlgorithmBayesianQPE` / Phayes | 非 Phayes 产品深度 | partial + stub 键 | 长期 | 见 CONTRIBUTING | 公开站 diff 复核 |
| **矩阵 §2 `AlgorithmAdaptVQE`** | pool / 日程与 InQuanto/Tangelo 公开「化学激发池」非逐条对齐 | partial + 文档对照节（parity §2 下「ADAPT 与公开 pool」） | Y2-Q1 | 见 CONTRIBUTING | `tutorial_inquanto_chain_h2.yaml`；`adapt.py` |
| **矩阵 §2 `AlgorithmIQEB`** | IQEB 可选路径；内层 VQE 深度 | partial + 既有 export 键 | Y1-Q4 | 见 CONTRIBUTING | `example_h2_iqeb.yaml` |
| **矩阵 §2 `AlgorithmVQD`** | 三通道报告 vs 闭源多目标叙事 | partial + `l1_excited` CI | Y1-Q4 | 见 CONTRIBUTING | PySCF；`test_qse_sceom_vqd_extended.py` |
| **矩阵 §2 `AlgorithmQSE` / `AlgorithmSCEOM`** | shot 语义与矩阵元噪声 | partial + `l1_excited` CI | Y1-Q4 | 见 CONTRIBUTING | PySCF |
| **矩阵 §2 `Algorithm*QPE`** | 演示轨 + Methods 合一（浅层） | partial；**深度资源估计** → [附录 A](与InQuanto能力差距与实施计划.md#appendix-a) P2-W1 | Y2-Q1 | 见 CONTRIBUTING | `example_h2_qpe_track.yaml`、`example_h2_qpe_track_parity_integrations.yaml`（pytket） |
| **`http_submit_poll_workspace`** | 本地 FastAPI 类比 vs Nexus UX | partial + caveat 固定 | Y1-Q4 | 见 CONTRIBUTING | `test_api_runs.py` |
| **`compiler_pass_bundle`** | 默认 `CompilerSpec`+CircuitIR；**非**默认全链 TKET | partial + 矩阵 §4「默认 / 可选 pytket」叙事 | Y1-Q4 | 见 CONTRIBUTING | 可选 `pytket`；`test_pytket_bridge.py` |
| **`computables_rich` 入 repro** | `parity_integrations.include_computables_rich_in_repro` | partial；golden 可选 | Y2-Q1 | 见 CONTRIBUTING | `test_workflow_preview_repro_alignment.py` |
| **矩阵 §3 分解插件** | `embedding.mode: plugin` 玩具 demo 与教程互链 | partial + 文档索引 | Y1-Q4 | 见 CONTRIBUTING | `example_decomposition_plugin_toy.yaml`；[case-study-h2-family](../docs-site/docs/tutorial/case-study-h2-family.md) |
| **`l1_md_ml` / QMEFDataset** | 长板字段与 `repro` 对齐清单 | partial + CONTRIBUTING 指针 | Y2-Q1 | 见 CONTRIBUTING | `md_bridge/`、`tests/test_md_bridge.py`；见 CONTRIBUTING「CI markers」 |

**签off 规则**

- **云/硬件**：不进入本表（刻意不对齐）。
- **闭源不可检证**：允许长期 `partial`，但须每季度复核公开文档是否新增可检证项。

**年度结束时**：未达标行 → 复制至下年路线图或降级为文档级 `n/a` 并说明原因。

**实施索引**（P1 全量核对后）：队列来源见 [附录 E](与InQuanto能力差距与实施计划.md#appendix-e) §5。

---

<a id="l3-benchmark-suite-roadmap"></a>

### 7. L3 小体系基准套件（Y1 Q3 交付物 — 路线图）

**目的**：在 **排除云/硬件** 前提下，为「公开面最大对齐」提供 **可重复数值门槛**（不等价 InQuanto 闭源默认）。**合并说明**：原独立文件 `L3_benchmark_suite_roadmap.md` 已并入本节，条文 **全文保留**。

### 7.1 规划项（实施顺序）

1. **基准 1**：H₂ sto-3g，活性 (2e,2o)，VQE+Pauli 协议 — 固定 `random_seed`、`energy_after_variational`、`energy_pauli_protocol` 阈值（见后续 `configs/l3_*.yaml`）。
2. **基准 2**：同上 + `run_sampled_pauli_protocol` 或 Qiskit shots 路径 — 方差/shots 门槛。
3. **基准 3（可选）**：极小 Schmidt 单轮 — `schmidt_dmet_cycles_executed` 与能量一致性与文档断言。

### 7.2 CI 策略

- **主 CI**：仅 schema / config 校验 + **skip** 重型断言。
- **夜间 / 可选 job**：`pytest -m l3`（`QCHEM_RUN_L3=1`，跑 **`L3_PYTEST_YAMLS`**，当前 **6** 条含 ADAPT/IQEB 池与别名）跑全量；论文表 JSON：`scripts/l3_algorithm_benchmark_report.py`。

### 7.3 与 export

跑完后 `export_parity_criteria_table --results out.json` 必须包含文档用键（与 `scripts/export_parity_criteria_table.py` 一致）。

### 7.4 占位单测

见 `tests/test_l3_benchmark_smoke.py`、`integrations/l3_algorithm_benchmark.py`（`L3_PYTEST_YAMLS` / `algorithm_benchmark_bundle_v1`）（默认 skip，文档指针回本节 **[§7](#l3-benchmark-suite-roadmap)**）。


---

<a id="appendix-c"></a>

## 附录 C：L1 对齐签字（合并收录；原 `L1_InQuanto_alignment_signoff.md`）

**契约**：与 [`docs/inquanto_public_parity_matrix.md`](inquanto_public_parity_matrix.md) + `qchem_stack.protocols.inquanto_contract` **同源**；**排除**真 Nexus/HQC 云产品与 H 系硬件标定。

| 矩阵锚点（parity_matrix_anchor / 表节） | gap.id（若有） | 证据（模块 / 键 / 测试） | 残余说明（caveat） |
|----------------------------------------|----------------|--------------------------|---------------------|
| §1 五阶段 Protocol | （叙事覆盖多项 gap） | `protocols/protocol.py`，`export_parity_criteria_table`，`POST /v1/meta/workflow-preview` | 异步作业非 Nexus 1:1 |
| §1 qnexus / HQC | `cloud_nexus` | `jobs/nexus_analog`，`nexus_cloud` | **非云**：本地类比 |
| §1 作业提交/轮询 | `http_submit_poll_workspace` | `api/app.py` `/v1/runs` | 无厂商身份/配额 |
| §1 Qermit | `qermit_graph` | `mitigation/qermit_analog`，`mitigation_execution_model_public`，`parity_snapshot.zne_qiskit_unification_v1`（ZNE×Qiskit Pauli），见 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) | 非闭源 Qermit |
| §1 Computable | `composable_computable` | `computable_graph_v2`，`computable.py`，可选 **`computables_rich_v1`**（workflow-preview） | 语义 DAG，非厂商融合 |
| §1 CuTensorNet | `tensornet` | `cutensornet_protocol_stub`，`parity_snapshot.tensornet_engine_resolved` | **n/a**：不宣称厂商 cuTN 化学收缩；开放 stub + 可选引擎探测 |
| §2 Algorithms | `ucc_chem_ansatz` 等 | `quantum/algorithms/*`；**JW UCCSD**：`configs/example_h2_uccsd.yaml`；**JW UCCSD Trotter**：`quantum.uccsd_trotter_steps`，`configs/example_h2_uccsd_trotter.yaml`；**IQEB**：`configs/example_h2_iqeb.yaml` | BK/SCBK 上映射的 UCCSD Trotter **n/a**（矩阵 §2）；IQEB 可选 |
| §2 VQD `three_protocol` | — | `excited.py`，`export`：`vqd_three_protocol_present_from_run`（`--results`）；`tests/test_qse_sceom_vqd_extended.py` | 单目标优化 + 三通道报告 |
| §2 QSE / SCEOM | — | `qse_transition.py`，`meta.qse_shot_mode`，`sceom.py` 中 `shot_noise_model`；`export`：`qse_shot_mode_from_run_meta`，`sceom_shot_noise_model_from_run`（`--results`） | 与闭源默认可能不同 |
| §2 QPE track | — | `qpe_qec_demo/`，`run_summary.qpe_demo_track_ran`，`export` `qpe_*_from_run` | `configs/example_h2_qpe_track.yaml` |
| §2 BayesianQPE / Phayes（计划序 C14） | — | [`qpe_qec_demo/README.md`](../src/qchem_stack/qpe_qec_demo/README.md)，`BayesianQPEStub`，`tests/test_l1_phase_c_iqeb_bayesian.py` | `partial`：非 Phayes 产品 |
| §3 PySCF / DMET | `dmet_scf_loop` | `chem/embedding`；**Schmidt–DMET 密度反馈**：`schmidt_dmet_max_cycles>1` 时 `integrations/schmidt_dmet_self_consistent`（`repro`/`schmidt_dmet_self_consistency`）；通用骨架 `integrations/dmet_self_consistent.DMETSelfConsistencyLoop`；`schmidt_bath_sidecar_json_path`；`oniom_layers_v1`（`configs/example_oniom_toy.yaml`）；`技术文档_DMET与parity_snapshot开放契约.md` | 闭源级全文献 DMET bath 仍 **partial**；多轮工程形态已可检证 |
| §3 Projection | — | `embedding.mode: projection`，`embedding_workflow`，`parity_snapshot.projection_embedding_open_trace`；`example_h2_projection_trace.yaml`（默认 `global_active_space`）；`example_h4_projection_mulliken.yaml`（`fragment_mulliken_mo`） | 默认路径：变分＝全局 active-space + 所选映射；Mulliken 路径：变分 Hamiltonian 按文档 §3；均 **非** full many-body projection 产品深度 |
| §3 driver 表面 | `drivers_cosmo_pbc` | `chem/inquanto_driver_surface.py`（`PYSCF_MIN_VERSION_RECOMMENDED`，`tests/test_inquanto_driver_surface_l1.py`） | PySCF 版本约束；非闭源 driver 行级等价 |
| §4 TKET / 编译 | `compiler_pass_bundle` | `CompilerSpec`，`tket_first_compiled_circuit_probe`，`技术文档_CircuitIR与TKET桥接及作业契约.md`，矩阵 §4 首条 | 无离子阱专有路由包 |
| 设备比特串期望 | `qpu_shot_histogram` | `run_qiskit_shots_pauli_protocol`，`技术文档_设备比特串与Qiskit采样路径.md` | 依赖 Qiskit/Aer |
| 集成参考包 | `integrations_closure_layer` | `parity_snapshot.open_gap_closure_reference`，`integrations/gap_closure_bundle.py` | L1 非 L0 |
| 评估支持集 | `evaluate_support_set` | `protocol_counts.hamiltonian_pauli_strings`，`pauli_support.assert_evaluate_compatible` | 保守兼容检查 |

### 计划序 24–25（激发态谱系 / MD-ML 长板）

| ID | 证据 | caveat |
|----|------|--------|
| **H1**（激发态 C10–C14） | CI：`pytest -m l1_excited`；代表测 `tests/test_qse_sceom_vqd_extended.py`（`l1_excited`）、`tests/test_orchestration_pipeline.py`；残余 `partial` 见 [附录 B §6](与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) | 与闭源算法深度非 L0 |
| **I1**（MD/ML） | CI：`pytest -m l1_md_ml`；`md_bridge/`，`tests/test_md_bridge.py`；竞争定位 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) | 差异化长板，非 InQuanto 主线 |

**公开文档钉扎（Quantinuum InQuanto）**

- 对照站点：`https://docs.quantinuum.com/inquanto/`（含 protocols、algorithms、errmit、cutensornet 等手册/API）。
- **How-to 工作流总览**：官方 [How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html) 与本栈模块映射见 [工程记忆 §14](工程记忆_Quantinuum对标与数据流技术文档.md)（章节改版时与矩阵一并 diff）。
- **最近一次人工锚定日期**：2026-04-30。若公开站改版，按 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §5 做一次矩阵 + `inquanto_gap_categories` 差异登记（不自动视为功能回退）。

**M2 环境约定（完整管线 + export）**

- 需 **PySCF**：`tests/test_export_parity_golden.py::test_m2_pipeline_then_export_documented_keys`；无 PySCF 的 CI 以 **config-only** 三 YAML 导出 + 黄金样例 [`tests/fixtures/parity_export_example_h2_config_only.json`](../tests/fixtures/parity_export_example_h2_config_only.json) 替代。

**机读键注册**：`PARITY_SNAPSHOT_DOCUMENTED_KEYS`、`PARITY_EXPORT_V2_STABLE_KEYS`（`protocols/inquanto_contract.py`）；快照全表见 [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md) §3 附录。

**回归**：`python -m pytest`；`python scripts/check_parity_export_sample.py`（仓库根；**抽样** 另含 `example_h2_uccsd_trotter`、`example_oniom_toy`、`example_h2_pbc_gamma` 等，完整列表见脚本内 `SAMPLE_CONFIGS_REL`）。**HTTP 总览**：`GET /v1/meta/capability-surface` 含 **`open_stack_differentiators`**（非云、非专有硬件下的可检证长板钉扎）。

**workflow-preview ↔ repro（P1）**：默认 `repro.workflow_preview_v1` 与 `POST /v1/meta/workflow-preview` 在 **同 YAML、不含** `computables_rich` 时同源（`tests/test_workflow_preview_repro_alignment.py`）。若 Methods 需要 rich 块入 repro，置 `parity_integrations.include_computables_rich_in_repro: true`（与 API `include_computables_rich` 对齐）。**异步作业**：`GET …/summary` 在 `DONE` 前为 `partial`；与 Nexus 云 UX 非 1:1 的键边界见 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)。

**广义 P1 计划闭合纪要（对照计划判据 1–5）**：§141 五项已在 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) 「仍需推进」段与矩阵/`inquanto_gap_categories`中落实为 **已交付 YAML + pytest/export** 或 **`n/a`+原因**（含 TN、`BK/SCBK` UCCSD Trotter）；差距总表 §1 已与源码及导出一致；双 parity 矩阵与 `check_parity_export_sample.py` 抽样覆盖新增 YAML；B→J 逐项闭合见 [附录 D](与InQuanto能力差距与实施计划.md#appendix-d)。

**负责人 / 日期**：流程角色见 [CONTRIBUTING.md](../CONTRIBUTING.md)；合并前可替换为实名 / 2026-04-30


---

<a id="appendix-d"></a>

## 附录 D：B→J 逐项闭合（合并收录；原 `InQuanto_B_J_逐项闭合计划.md`）

**权威差距叙述**：[inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)、[与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)。**机读 gap**：`qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`。

---

### 0. 「完美对拍」的严格定义（本计划唯一验收哲学）

本仓库**不**验收与 **InQuanto 闭源 wheel / 内部默认启发式 / 商业 Qermit-cuTensorNet 二进制**的逐比特或逐数值等价（**L0**）。  
**本条计划的「对拍完成」= L1+**（与 [附录 C](与InQuanto能力差距与实施计划.md#appendix-c)、[工程记忆 §0](工程记忆_Quantinuum对标与数据流技术文档.md) 一致）：

| 层级 | 含义 |
|------|------|
| **L1 闭合** | 针对该项：[Quantinuum 公开文档](https://docs.quantinuum.com/inquanto/) 中**可指明的条目**；本仓 **机读 JSON**（`repro` / `parity_snapshot` / `run_summary` / `export_parity_criteria_table` / `GET .../capability-surface`）中 **键与语义固定**；**pytest 或脚本**回归；矩阵行从 `partial` 收束为 **`yes`（诚实 caveat）** 或保持 `partial` 但 **[附录 B §6](与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 有季度 SLA** |
| **排除** | **A 段（云/HQC/OAuth/配额）**、**硬件专优**：不进入「对拍完成」，维持 `n/a` / 刻意不对齐文案 |
| **不可公开检证** | 任一项无法只用公开资料定义判据的：允许 **长期 `partial`**，但必须 **SLA + epistemic 固定文案** |

**PR 规则**：改行为 → **双改** [parity 矩阵](inquanto_public_parity_matrix.md) 或 gap；动 `parity_snapshot` 顶键 → 更新 `PARITY_SNAPSHOT_DOCUMENTED_KEYS`。

**执行顺序**：下文 **严格按序号 1→N**（对应前答 **B→J** 分项）；每一序号为**可并行子 PR 的一个里程碑**，但**台账上建议按序钉扎**，避免未闭合契约就堆算法特例。

---

### 阶段 B — Protocols 与工作流（矩阵 §1）

| 序 | 对应分项 | 闭源 L0 是否可达 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|------------------|---------|--------|-------------|
| **1** | B1 五阶段 Protocol | 否 | 五阶段语义、三能量路径、异步边界文档与机读一致 | 矩阵 B1 行 caveat 收束；`protocol_counts` / `repro` 时间线字段（若需）与 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md) 一致 | `pytest` 覆盖五阶段 + 至少一条 Qiskit shots 路径 smoke；export 样例无未文档化键 |
| **2** | B2 `dataframe_circuit_shot` | — | **签认 yes** | 矩阵明示 yes；资源行与 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) § 一致 | 现有资源单测 + export `excited_resource` 不回归 |
| **3** | B3 Computable / Methods | 否 | **语义 DAG + YAML 预览 + `computables_rich`（可选）** 与公开「Computable+Protocol」叙事对表；若 API 形态永异：SLA | `computable_graph_v2` 边策略文档化；`POST computables-preview` / `workflow-preview` schema 冻结；缺口写入 gap `composable_computable` | API 单测 + golden export；矩阵 §1 Computable 行更新 |
| **4** | B4 HTTP 作业网关 | 否（非真 Nexus） | **本地类比**能力与限制写死 | [launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md) + ENGINEERING §9 + gap `http_submit_poll_workspace` 同步 | `test_api_runs.py` 覆盖 submit/list/summary/repro；矩阵 **partial** + caveat「无厂商配额」 |
| **5** | B5 Qermit MitRes/MitEx | 否 | **开放 DAG + 线性迹 + `mitigation_execution_model`** 与 [errmit 手册](https://docs.quantinuum.com/inquanto/manual/errmit.html) 公开节对表；MitEx 批量 → SLA | [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) 与 `capability-surface` 同源；ZNE/PMSV 键完整 | gap `qermit_graph` status 与单测；**不宣称**商业 Qermit |
| **6** | B6 CuTensorNet | 否 | **stub + 引擎解析 + `tensornet_engine_resolved`**；化学尺度收缩 → SLA 或 L3 | [附录 B §7](与InQuanto能力差距与实施计划.md#l3-benchmark-suite-roadmap) 挂钩；矩阵 TN 行与 `tensornet/` 一致 | pytest stub + 可选引擎探测；gap `tensornet` |

---

### 阶段 C — Algorithms（矩阵 §2）

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

### 阶段 D — 经典化学与嵌入（矩阵 §3）

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **15** | D1 PySCF/JW | **签认 yes** | — | 既有单测 |
| **16** | D2 DMET 框架 | Schmidt 密度反馈 + `cycles_executed` / 钩子 | [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md) + gap `dmet_scf_loop` | Schmidt 生产单测 |
| **17** | D3 Projection | `projection` + YAML 示例 + 矩阵行 | `configs/` 示例 + 嵌入 export | 集成测或文档签认 |
| **18** | D4 Driver 表面 | `inquanto_driver_surface` 与矩阵 **逐项** yes/partial+约束 | 差距表 §「driver 审计」闭环 | driver 表 + PySCF min 版本注释 |
| **19** | D5 Schmidt 多轮叙事 | 与 D2 合并验收；多碎片 sweep | 矩阵 §3 + `embedding_workflow_from_run` | `test_schmidt_embedding_production` |

---

### 阶段 E — 编译 / TKET（矩阵 §4）

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **20** | E1–E3 TKET 链 | `CompilerSpec` + **tket_first 探针**与 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §2–4 **一致**；Ion 专有 routing → **n/a 叙事** | gap `compiler_pass_bundle`；可选默认 `pytket` CI job | `test_tket_compiler_narrative` + `test_pytket_bridge` |

---

### 阶段 F — 对象模型与 Ansatz

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **21** | F1 Computable 薄层 | `ComputableSpec` 或与 `ComputableRef` **双向转换**（L1 签字稿 [附录 C](与InQuanto能力差距与实施计划.md#appendix-c) 原三周日历口径）；**不**承诺闭源融合顺序 | `protocols/computable.py` + workflow-preview 可选 `computables_rich` | 单测 + 矩阵 **`composable_computable` 状态升级** |
| **22** | F2 UCC / 化学池 | `ChemicallyAwareUCCPolicy` + `ucc_reference` 在 **`open_gap_closure_reference` 可见** | [gap_closure_bundle.py](../src/qchem_stack/integrations/gap_closure_bundle.py) + 矩阵 §2 | UCC 计数/导出单测；gap `ucc_chem_ansatz` 备注更新 |

---

### 阶段 G — 协议 run 语义

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **23** | G1 三能量路径 + DataFrame 叙事 | 在 [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md) 与 export 中 **对齐「云侧 shot 叙事」的开放等价物**（非真云） | 矩阵 Protocol 行收束 caveat | `classify_pauli_expectation_path` + parity_export CI |

---

### 阶段 H / I — 激发态产品线自述 + MD/ML

| 序 | 对应分项 | L1 目标 | 交付物 | 验收（DoD） |
|----|----------|---------|--------|-------------|
| **24** | H1 激发态谱系 | C10–C14 **汇总签字**；残余算法 → SLA | L1 签字表 §2 全钩 | 一节「激发态总回归」CI（或 nightly） |
| **25** | I1 MD/ML 长板 | **签认差异化** | [竞争定位](竞争定位与路线图_对标Quantinuum产品与技术路线.md) + README | `md_bridge` smoke（若有）或文档签认 |

---

### 阶段 J — `inquanto_gap_categories` 行（与非云软件相关）

在 **序 1–25** 推进中 **同步**更新 gap：**`http_submit_poll_workspace`、`qermit_graph`、`composable_computable`、`evaluate_support_set`、`compiler_pass_bundle`、`ucc_chem_ansatz`、`dmet_scf_loop`、`tensornet`、`integrations_closure_layer`、`drivers_cosmo_pbc`**。  
`qpu_shot_histogram` 已为 **`yes_qiskit`**：序 23 中 **签认**与矩阵 §1–2 一致。

**序 26（总闸）**：`GET /v1/meta/capability-surface` 与 `inquanto_gap_categories()` **逐字段同源**（已有 `test_capability_surface_matches_inquanto_contract`）；**月度**跑 `scripts/check_parity_export_sample.py` + 全 `pytest`。

---

### 台账与季度签 off

- 进度钉扎：[附录 B](与InQuanto能力差距与实施计划.md#appendix-b) §3 度量表每月一行；**序 1–26** 完成度映射到「无 unexplained `partial`」。
- 闭源不可达项：一律在 [附录 B §6](与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 落表。

---

### 附录 A — P1 maximal 机读对账（`gap.id` ↔ 矩阵锚点 ↔ 测试 / YAML / CI）

**用途**：Phase0 基线；合并 PR 时按本表检查「改代码 → 改矩阵 / gap / 测试」是否闭环。`inquanto_gap_categories()` 为机读权威列表。

| gap.id | parity_matrix_anchor（摘要） | 主要 pytest / 脚本 | 代表 YAML（节选） |
|--------|------------------------------|---------------------|-------------------|
| `cloud_nexus` | §1 qnexus/HQC | `tests/test_api_runs.py`（侧车元数据） | Nexus 类比 YAML（见 ENGINEERING） |
| `http_submit_poll_workspace` | §1 作业网关 | `tests/test_api_runs.py` | `_minimal_experiment_yaml` |
| `qermit_graph` | §1 Qermit | `tests/test_mitigation_dag_trace_homology.py` | `example_h2_zne_circuit_fold.yaml`（ZNE） |
| `composable_computable` | §1 Computable | `tests/test_computable.py`、`tests/test_workflow_preview_repro_alignment.py`、`tests/test_inquanto_workflow_preview.py` | `example_h2.yaml`；rich：`parity_integrations.include_computables_rich_in_repro` |
| （导出）`methods_resource_preview_v1` / `methods_resource_unified_v1` | §1 Methods / QPE 资源合一 | `tests/test_methods_resource_unified_export.py`、`scripts/export_parity_criteria_table.py` | `qpe_dual_track_demo.yaml`、`configs/example_h2.yaml`（`--results` 路径） |
| （导出）`resource_estimation_preview_v1` | §1 resource estimation 公开叙事（浅层） | `tests/test_methods_resource_unified_export.py::test_resource_estimation_preview_v1_config_only_export`、`scripts/export_parity_criteria_table.py` | `configs/example_h2_qpe_track_parity_integrations.yaml`（`parity_integrations.resource_estimation_preview: true`） |
| `evaluate_support_set` | §1 resource | `tests/test_pauli_support*`（若存在）/ protocol 单测 | `example_h2.yaml` |
| `compiler_pass_bundle` | §4 TKET | `tests/test_backend_conformance.py::test_example_h2_tket_probe_dict_when_pauli_protocol_runs` | `example_h2.yaml` |
| `ucc_chem_ansatz` | §2 UCC/ADAPT | `tests/test_backend_conformance.py::test_example_h2_uccsd_packaged_yaml_repro_schema`、`tests/test_orchestration_pipeline.py`（Trotter） | `example_h2_uccsd.yaml`、`example_h2_uccsd_trotter.yaml` |
| `dmet_scf_loop` | §3 DMET | Schmidt / fragment 相关 `tests/test_*schmidt*`、`test_export_parity_golden` | `example_h4_dmet_fragment_exact_small.yaml` 等 |
| `tensornet` | §1 CuTensorNet（矩阵 **`n/a`**） | tensornet stub 单测 + `parity_snapshot.tensornet_*`；gap status 闭合为 vendor-free **`n/a`** | `quantum.tensornet_expectation_stub` 配置；见矩阵 §1 |
| `integrations_closure_layer` | 架构闭合 | `integrations/gap_closure_bundle` 导出链 | parity export |
| `drivers_cosmo_pbc` | §3 driver | `tests/test_inquanto_driver_surface_l1.py` | `example_h2_pbc_gamma.yaml`、`chemistry_extended` PBC/ddCOSMO |
| （教程）projection 深入 | §3 Projection | — | `docs-site/docs/tutorial/projection-embedding-deep-dive.md`；`example_h2_projection_trace.yaml`、`example_h4_projection_mulliken.yaml` |
| `qpu_shot_histogram` | Qiskit shots | `tests/test_*qiskit*` / export 抽样 | `example_h2_qiskit_shots.yaml` |

**CI 挂钩**：[`../.github/workflows/ci.yml`](../.github/workflows/ci.yml) — `check_parity_export_sample`、`l1_excited`、`l1_md_ml`、projection smoke；脚本内 `SAMPLE_CONFIGS_REL` 与上表 YAML 应对齐。

---

### 依赖解除声明

若业务方坚持的「完美对拍」= **L0 与 InQuanto 闭包数值/对象同构**，则 **超出本开源仓范围**，须单列商务与法务项；本计划 **不作此类验收**。

---

*版本：与对话中 **B–J 分项** 1:1 对应；维护人按序更新矩阵/gap/SLA。*


---

<a id="appendix-e"></a>

## 附录 E：P1 全量核对（合并收录至 §2；原 `P1_completion_audit.md`）

**钉扎日期**：2026-05-07（审计生成时仓库状态）。**范围**：竞争定位 §6「P1 开源工作流超越」四行 + 差距文档 §3 摘要表中 **P1 中程** 三条（证据见本文 §2）+ [附录 C](与InQuanto能力差距与实施计划.md#appendix-c) 主表与 H1/I1 + 与 P1 叙事强相关的 parity 主表（§1–§3）及 [附录 D](与InQuanto能力差距与实施计划.md#appendix-d) 交叉引用。**不含**：路线图 P2/P3 实现（见 [附录 A](与InQuanto能力差距与实施计划.md#appendix-a)）、真 Nexus/H 系、L0 闭源等价。

---

### §0 方法与状态枚举

| 状态 | 含义 |
|------|------|
| **done** | 竞争定位 / L1 / 差距文档所述验收口径在开放栈内已满足，且有 **pytest 或脚本或 YAML** 可复跑。 |
| **partial+caveat** | 能力存在且机读键齐全，但与 InQuanto 公开产品形态或深度**非 1:1**；矩阵与 gap 已写 caveat 或 `n/a`。 |
| **n/a** | 刻意不对齐或非公开可检证范围（云、专有硬件、商业二进制等）。 |
| **doc_only_gap** | 叙事/矩阵已闭合，但缺少**专用**单测或 export 黄金样例；建议补测而非改算法。 |

**证据写法**：每条给出 `src/...` 或 `configs/...` 或 `tests/...` 或 `scripts/...` 的仓库相对路径。无单测则标 **证据缺口**。

---

### §1 竞争定位 §6「P1 开源工作流超越」四行对照

| # | 竞争目标 | 工程动作摘要 | 主要证据 | 验收口径是否满足 | 缺口 | 建议 |
|---|----------|--------------|----------|------------------|------|------|
| P1-1 | 吸收 InQuanto 的对象模型纪律 | workflow/computable graph；YAML 与 API 共用；`workflow-preview` 与 `repro` 对齐 | [`src/qchem_stack/protocols/computable.py`](../src/qchem_stack/protocols/computable.py)；[`integrations/inquanto_workflow_preview.py`](../src/qchem_stack/integrations/inquanto_workflow_preview.py)；[`api/app.py`](../src/qchem_stack/api/app.py)；[`tests/test_workflow_preview_repro_alignment.py`](../tests/test_workflow_preview_repro_alignment.py) | **partial+caveat**：薄层 DAG + preview 已对齐；非闭源 `Computable` 产品类 | 与差距表「无独立 Computable 产品类」一致 | **保持 P1 签字**；深度对象模型 → **P2** 或长期 SLA |
| P1-2 | 吸收 Tangelo 多算法与多后端广度 | ansatz/solver/mapping registry；JW/BK/SCBK；conformance | [`chem/hamiltonian.py`](../src/qchem_stack/chem/hamiltonian.py)、[`quantum/algorithm_registry.py`](../src/qchem_stack/quantum/algorithm_registry.py)、[`chem/fermion_mapping_registry.py`](../src/qchem_stack/chem/fermion_mapping_registry.py)；[`tests/test_backend_conformance.py`](../tests/test_backend_conformance.py)；样例 [`configs/example_h2_uccsd.yaml`](../configs/example_h2_uccsd.yaml)、[`configs/example_h2_uccsd_trotter.yaml`](../configs/example_h2_uccsd_trotter.yaml) | **partial+caveat**：三映射 + 多 provider schema 稳定；BK/SCBK 上 UCCSD Trotter 矩阵 **n/a** | 化学池广度、BK Trotter | **P1 已可发表**；池扩展 → **P2-W5** |
| P1-3 | embedding-first 主线 | DMETContext、projection、fragment；Schmidt 密度反馈；`repro` 全量 | [`chem/embedding/`](../src/qchem_stack/chem/embedding/)；[`integrations/schmidt_dmet_self_consistent.py`](../src/qchem_stack/integrations/schmidt_dmet_self_consistent.py)、[`integrations/dmet_self_consistent.py`](../src/qchem_stack/integrations/dmet_self_consistent.py)；[`orchestration/pipeline.py`](../src/qchem_stack/orchestration/pipeline.py)；[技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md)；[`configs/example_h2_projection_trace.yaml`](../configs/example_h2_projection_trace.yaml)、[`configs/example_h4_dmet_fragment_exact_small.yaml`](../configs/example_h4_dmet_fragment_exact_small.yaml)、[`configs/example_oniom_toy.yaml`](../configs/example_oniom_toy.yaml)、[`configs/example_h2o_sto3g_cas44.yaml`](../configs/example_h2o_sto3g_cas44.yaml)、[`configs/example_n2_sto3g_cas44.yaml`](../configs/example_n2_sto3g_cas44.yaml)、侧车键见 L1 表 | **partial+caveat**：小体系 trace、Schmidt 生产、Schmidt–DMET 密度反馈工程链已闭合；闭源 bath 拟合未宣称 | 产品级 ONIOM/QM-MM | **P1 叙事闭合**；产品级分解 → **P2-W2** |
| P1-4 | mitigation 升为 workflow block | PMSV/ZNE/SPAM DAG；`qermit_analog` | [`mitigation/`](../src/qchem_stack/mitigation/)；[`tests/test_mitigation_dag_trace_homology.py`](../tests/test_mitigation_dag_trace_homology.py)；[`mitigation_PMSV_ZNE_Qermit_mapping.md`](mitigation_PMSV_ZNE_Qermit_mapping.md)；[`configs/example_h2_zne_circuit_fold.yaml`](../configs/example_h2_zne_circuit_fold.yaml) | **partial+caveat**：DAG 与 trace 同源；非商业 Qermit | 进阶 shadows 等 | **P1 闭合**；进阶块 → **P2-W4** |

---

### §2 差距文档 §3 摘要表「P1 中程」三条映射

| 差距文档条目 | 实现要点 | 单测 / 脚本 |
|--------------|----------|-------------|
| **嵌入** `repro.embedding_config` = 全 `EmbeddingSpec` | `collect_repro_metadata` / `EmbeddingSpec` 序列化 | [`tests/test_repro_snapshot_qse_sceom.py`](../tests/test_repro_snapshot_qse_sceom.py) 内 `test_repro_includes_embedding_config_block`（差距文内点名） |
| **激发态报告** `excited_methods_unified` + export `excited_resource_from_config` | `orchestration` 内 `excited_resource_summary`；export v2 | `tests/test_orchestration_pipeline.py`；`export_parity_criteria_table` config-only 路径 |
| **PMSV** 合并 `protocol_counts['pmsv_report']` | `mitigation.pmsv.finalize_pmsv_report` | `tutorial_inquanto_chain_h2.yaml` + 管线测；`check_parity_export_sample` 含链式 YAML |

**结论**：三条均为 **done**（在「可发表 L1」语义下）；残余 **partial** 见差距总表 §1「激发态 / 经典化学」行（算法深度），属 H1 与矩阵 §2，不与此三条矛盾。

---

<a id="appendix-f"></a>

## 附录 F：不排期项转排期（合并收录；原 `不排期项_转排期与实现说明.md`）

原差距计划正文曾**显式不排期**的 Nexus/HQC、Qermit 全图、CuTensorNet、InQuanto 全 driver 名，现转入**有期限迭代**，以 **可审计的开放栈类比** 交付（**非** 闭源或商业云等价物）。

| 原不排期项 | 合规定位 | 实现入口（v1） | 仍非目标 |
|------------|----------|----------------|----------|
| Nexus / HQC 计价 | 本地 `CostEstimate` + YAML 权重，项目标签 | `jobs.nexus_analog`；流水线 `nexus_analog_ledger`；异步 `nexus_analog_billing` 与同步一致（`PauliAveragingProtocol` 上序列化 `NexusAnalogSpec`） | 无 Quantinuum API、无真货币 |
| Qermit 全图 | **DAG**（`nodes` + `edges` + `topological_order`），映射 PMSV/ZNE | `mitigation/qermit_analog.py`（`qermit_analog_v2`）→ `mitigation_graph_report` | 非 Qermit 运行时、非 NVIDIA/CQC 二进制 |
| CuTensorNet | 协议位；`opt_einsum` / `cupy` / **`cuquantum_if_available`**（检测 NVIDIA 栈） | `tensornet/cutensornet_protocol_stub.py`；`quantum.tensornet_expectation_stub` + `tensornet_contraction_engine` | 无 `inquanto-cutensornet` 产品包 |
| 全 driver 面（COSMO/PBC…） | 名称映射 + PySCF | `chem/inquanto_driver_surface.py`；`solvent_model=ddcosmo`；`pbc_cell_vectors_bohr` + `pbc_kpoint_mesh` → **RHF**（Γ）或 **KRHF**（k 网）；`pbc_active_space_kpoint_index` 选 CASCI 用 k；PBC+ddCOSMO 在 PySCF 支持时包装（失败则报错提示） | 非全 InQuanto 封闭 driver |
| Nexus 云 / cuTensorNet 真服务 | 云侧需合同与密钥 | `jobs/nexus_cloud.py` HTTP/ mock 侧车；`tensornet` 的 `cuquantum_if_available` 检测 NVIDIA 栈 | 非内建供应商 SLA |
| Qermit 可执行图 | 与 YAML 一致的 **线性** 执行迹 | `mitigation/qermit_runtime.py` → `mitigation_dag_execution` | 非 Qermit 产品运行时 |

**维护**：更新能力矩阵时同步 `inquanto_contract.inquanto_gap_categories()` 中 `status` 字段与本文。

---

*版本：正文 §1–§6 为差距与维护入口；**附录 A–F** 收编原 P2 / Y1 / L1 / B→J / P1 审计 / 不排期项独立稿。与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 表同源维护。*
