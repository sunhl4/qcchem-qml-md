# qchem_stack 工程记忆：与 Quantinuum / InQuanto 公开路线对标及优化路线图

**文档性质**：本仓库的「工程记忆」与 Methods 级技术说明。依据为 PandM 文献库中两篇竞品深度稿（数据流与判据；激发态 VQD/QSE/SCEOM）以及本仓库 **公开** 源码与 [InQuanto 公开文档](https://docs.quantinuum.com/inquanto/) 的对照。**不**声称复现闭源二进制或对方默认超参。

**竞争定位与分阶段目标（对 Quantinuum 产品/技术路线）**：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](/concept/competitive-positioning)（我们「做什么产品」、不拼什么、P0–P2 与仓库模块的映射）。本文偏**模块与判据**；该文偏**战略与优先级**。

**关联文献（工作区）**：

- `PandM/materials/learning/quantum-chem/literature/Quantinuum_深度技术剖析_从积分到Shots的数据流与可证伪判据.md`
- `PandM/materials/learning/quantum-chem/literature/Quantinuum_激发态深度剖析_VQD_QSE_SCEOM.md`
- 能力矩阵：`docs/inquanto_public_parity_matrix.md`
- **开放栈「记忆 + 缺口清单」**：见本文 **[§13](#13-开放栈对标完成度与待闭合项原独立记忆合并)**（原独立页已合并）
- **DMET / `parity_snapshot` 契约**：[技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot)
- **详细技术说明（本包）**：[技术文档_CircuitIR与TKET桥接及作业契约.md](/reference/circuitir-tket-jobs)（`CircuitIR`↔pytket、资源双轨、`JobHandle`/`protocol_hash`、与 Nexus **语义**类比）
- 异步提交/拉结果短表：`docs/launch_retrieve_nexus_analog.md`
- **HTTP + SQLite 队列 + 可观测性（契约）**：[技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)
- **HTTP 维护决策与 Checklist**：[技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs) **§9**

---

## 1. 纵向物化链在本工程中的落点

竞品文强调：可对标深度在「哪一层把数学对象物化成电路与测量统计」，而非「有没有 VQE」。

| 物化阶段 | 竞品要点 | `qchem_stack` 现状 | 备注 |
|----------|----------|-------------------|------|
| 积分与活性空间 | 同一组轨道、同一 JW/BK、同一常数/冻结核 | `molecular_hamiltonian_from_pyscf` → JW `QubitOperator`；`FermionSpace` 元数据 | 可扩展：显式在 `QubitHamiltonian.meta` 中序列化积分来源、CAS 标签、映射名 |
| 费米子 → Pauli | 门综合复杂度与测量复杂度分叉 | `PauliAveragingProtocol` + `build_measurement_plan` | 与 UCC/ADAPT 线路深度分开追踪（parity 矩阵已承认） |
| Protocol | build→compile→run→evaluate；支撑集与 shots | `PauliAveragingProtocol` 五阶段 + `dataframe_circuit_shot_rows` | `run()` 当前用 executor 精确期望 + 经典 shot 方差账；**非**逐电路采样仿真（见 §4）。资源行 depth/2Q：见 **§11** 与 [技术文档](/reference/circuitir-tket-jobs)（自研 `spec` vs 可选 **pytket** 双轨） |
| 缓解 | PMSV 有效样本、方差权衡；竞品另有 Qermit 产品图 | `PMSVConfig` + `filter_shots_pmsv`；**机读** `mitigation/qermit_analog.py`（DAG，`qermit_analog_v2`）+ `mitigation/qermit_runtime.py`（`mitigation_dag_execution` 线性迹）；ZNE **`MitigationSpec.zne_scales`** 接协议 `zne_scales`；仍会报 retention / stderr（见 §7） | **非** Qermit 商业运行时；ZNE 仍为标度 stub，真多电路放大见 §7「优化」 |
| Embedding | DMET 量子在 fragment | `chem/embedding/dmet.py`；`EmbeddingSpec.dmet_hamiltonian_source`（`parity_stub` / `whole_active_system` 单片段真 VQE）；`repro.parity_snapshot` 中 `dmet_*`；`integrations/dmet_self_consistent` 自洽骨架 | 与竞品 §4 一致：论文需写清自洽轮数与经典基线档；**多片段 bath DMET 仍依赖用户钩子** |

---

## 2. 可证伪判据表 → 本工程自检清单

竞品「§7 判据表」建议任何对标至少固定：几何、活性空间、映射、哈密顿量常数、目标量、估计器（分组/shots）、缓解、编译门集、经典强相关基线。

**本工程已具备的复现钩子**：

- YAML 实验配置 + `collect_repro_metadata`（config SHA、包版本）。
- `protocol_hash`、`SqliteJobStore` 作业载荷。
- `resource_summary`：`sum_shots`、`max_depth`、`sum_twoq` 等。

**首轮已落地（判据表友好）**：

- `repro.parity_snapshot`：`pauli_grouping`、`shots_per_circuit`、`target_energy_stderr`（YAML `backend.target_energy_stderr`）、缓解与编译字段、以及 `hamiltonian_meta`（含 JW 映射名与活性空间）；**嵌入**：`embedding_mode`、`n_scf_cycles_embedding`、`classical_reference_method`、`embedding_fragment_labels`（来自 `ExperimentConfig.embedding`）。
- `QubitHamiltonian.meta`：`fermion_to_qubit_map`、`integral_source`、`n_active_*`。

**仍建议后续补齐**：

1. 论文级导出：单表汇总「判据表 §7」各行取值，由脚本从 `ExperimentConfig` + protocol 结果生成。

---

## 3. 激发态：与竞品三算法的差距与路线

竞品文核心：**VQD** 是三通道（objective / weight / overlap）估计问题；**QSE** 是 \(O(K^2)\) 个 \(H_{ij},S_{ij}\) 与广义本征；**SCEOM** 是 EOM 型 \(M\) 矩阵与相关激发流形。

| 算法 | 竞品抽象 | 本工程 | 差距 |
|------|----------|--------|------|
| VQD | 三 `Protocol`、重叠线路、粒子数守恒 ansatz | 优化仍单目标；`vqd_channels[*].three_protocol` 分 **objective / overlap / weight** 报告（可选 shots；重叠为 swap-test 模型） | 缺：优化内环三线路严格解耦、粒子数守恒 ansatz |
| QSE | `QSEMatricesComputable` 式打包 | `qse_transition.py` + `run_from_vqe_hea_basis_pauli_transitions`（逐 $(i,j)$ Pauli 贡献 + `QSEPauliTransitionSchedule`） | 缺：fermionic 激发池与 InQuanto composite 完全同构 |
| SCEOM | shot-\(M\)、分析 DataFrame | `run_sceom_nested_commutator` / `from_hea`：嵌套对易子 \(M\) + 可选矩阵噪声；仍为 Pauli 玩具 \(S\) | 缺：文献费米激发算符、自洽迭代、全部分析 DataFrame |

### 3.1 激发态与 `repro.run_summary`（主线 pipeline）

完成管线后，`orchestration.pipeline._attach_run_summary` 在对应阶段实际运行时写入 Methods 友好键：

| 键 | 含义 |
|----|------|
| `vqd_three_protocol_present` | 任一 `vqd.meta.vqd_channels[*]` 含 `three_protocol`（与 `scripts/export_parity_criteria_table.py` 中 `vqd_three_protocol_present_from_run` 判定一致） |
| `vqd_reused_pipeline_ground` | VQD 复用 variational 基态角标（既有） |
| `qse_shot_mode` | YAML `quantum.qse_shot_mode`（`exact` / `gaussian_h` / `pauli_transitions`）；`out["qse"].meta` 同步写入同名键 |
| `qse_shot_noise_model` | 当 QSE meta 含 `shot_noise_model` 时_mirror（`gaussian_h` / `pauli_transitions` 路径） |
| `sceom_shot_noise_model` | SCEOM meta：`none` / `symmetric_gaussian_on_real_M` 等（`quantum/algorithms/sceom.py`） |
| `sceom_shots_per_matrix_element` | YAML 预算_echo |

**回归**：`tests/test_orchestration_pipeline.py`（`test_run_pipeline_sync_h2_vqd_yaml_shots`、`test_run_pipeline_sync_h2_qse_sceom_yaml`、`test_run_pipeline_sync_h2_qse_pauli_transitions_run_summary`）。**Export**：`--results` 合并时若 `repro.run_summary` 已含上列键，脚本另输出 `vqd_three_protocol_present_from_run_summary`、`qse_shot_mode_from_run_summary`、`sceom_shot_noise_model_from_run_summary`。

**与 `PauliAveragingProtocol` 的咬合方向（推荐实现顺序）**：

1. **QSE 矩阵元协议**：对固定子空间基，引入 `TransitionPauliProtocol`（或扩展现有 plan）：对每组 \((i,j)\) 与 Pauli 项 \(P_p\)，估计 \(\langle\phi_i|P_p|\phi_j\rangle\)；在类上复用 `build_measurement_plan` 的**分组思想**，但测量态为 \(U_j|0\rangle\) 与 \(U_i|0\rangle\) 的线性组合——需选定分解（Hadamard test / LCU 等）并在文档中固定。
2. **VQD**：将 `overlap_penalty` 拆成 `PauliAveragingProtocol`（能量）+ 独立 `OverlapSquared` 估计模块；YAML 中 `shots_budget_vqd: {objective, overlap, weight}`。
3. **SCEOM**：在文献锚点不变前提下，先实现「小体系 \(M\) 稠密参考」与「Pauli 展开 \(M_{ij}\)」的符号层，再挂 shot 估计。

---

## 4. Protocol `run` 语义与竞品「evaluate」差异（重要）

当前 `PauliAveragingProtocol.run()`（`protocol.py`）：

- 能量均值来自 `executor.expectation_hea(...)`（statevector / 模拟器为**精确**或后端定义的单标量）。
- `energy_stderr`、`total_shots_budget` 来自 `energy_estimate_with_uncertainty` 的**经典保守界**，不是从有限 shot 样本重估 \(\langle H\rangle\)。

竞品 InQuanto：`run` 产生测量 DataFrame，`evaluate_expectation_value` 在**同一支撑集**上做线性重组。

**优化建议**：

- **文档**：README 与本节已写明：机读字段 `expectation_source`、`energy_stderr_model` 见 `PauliAveragingProtocol._counts`。
- **二轮已落地**：`PauliAveragingProtocol.run_sampled` + `backends/pauli_shot_sim.py`：在 statevector 上对分组 Pauli 做同时（或 greedy 下逐项）采样重组能量；`_counts` 中 `expectation_source=grouped_shot_simulation_statevector`。YAML：`quantum.run_sampled_pauli_protocol`。
- **Qiskit 真比特串已落地**：`run_qiskit_shots` + `backends/qiskit_pauli_shots.py`（`get_counts`、与 `pauli_shot_sim` 同构的 `comp_index` 与直方图）；`expectation_source=qiskit_shot_counts_get_counts`；见 [技术文档_设备比特串与Qiskit采样路径.md](/reference/qiskit-shot-counts)。
- **仍可选**：非 Qiskit 前端的 `HamiltonianExpectationExecutor` 与设备作业 JSON 1:1 行级契约。
- **PMSV（首轮）**：当 `0 < retention_rate < 1` 时，对保守 `energy_stderr` 乘以 \(1/\sqrt{\eta}\)，并记录 `pmsv_stderr_scale`；真实 stabilizer 比特串后筛选仍为后续项。

---

## 5. Shots 与分组：已有能力与改进点

- `recommended_shots_per_circuit`：反演 `conservative_stderr_equal_shots`，满足目标 `target_energy_stderr`（YAML 可配）。
- **首轮已落地**：`resource_summary` 与 `protocol_counts` 含 `n_pauli_terms`（\(L\)）、`n_pauli_groups`（\(G\)）。
- **改进**：支持**不等 shots**（难测 Pauli 组多分配）、或按组权重闭式分配（在总预算约束下最小化方差上界）。

---

## 6. 控制论视角：流水线外环/内环

- **外环**：`run_pipeline_sync` 中 VQE/ADAPT 更新 \(\theta\)。
- **内环**：可选 `PauliAveragingProtocol` 对固定 \(\theta\) 做能量估计与资源表。

**首轮已落地**：`FermionicAdaptVQE` 的 `meta` 含 `adapt_steps`（每步 `n_pool_candidates_scanned`、`n_gradient_evals`、`best_grad_mag`、`selected_pair`）与 `total_gradient_evals`。

**仍存缺口**：每步与 `PauliAveragingProtocol` 的统一计费、以及真实费米池的 Pauli 梯度项数——需后续与 `adapt_meta` 联合导出。

---

## 7. 缓解与编排

**竞品**：Qermit 产品图与云上异步；本工程：**SQLite** job + `process_job_with_retry`；另有与 InQuanto **公开叙事可对表**的开放栈类比（**非** 二进制等价）：

- **缓解图 + 线性执行**：`mitigation_graph_report`（`qermit_analog`）与管线输出的 `mitigation_dag_execution`（`qermit_runtime`）。详见 [不排期项_转排期与实现说明.md](/parity/backlog-to-schedule)、[inquanto_public_parity_matrix.md](/parity/public-matrix)。
- **真云**：不设 Quantinuum SDK；`jobs/nexus_cloud.py` 为 **http/mock 侧车**（`ExperimentConfig.nexus_cloud`），仅 repro/探活，**非** Nexus 作业 API。
- **计价类比**：`jobs/nexus_analog.py` + YAML `nexus_analog`；异步作业 pickle 上带 **`NexusAnalogSpec`**，`nexus_analog_billing` 与同步 `nexus_analog_ledger` 权重一致。

**与 Nexus 的语义（已文档化，非 1:1 实现）**：

- 短表：[launch_retrieve_nexus_analog.md](/concept/launch-retrieve-nexus-analog)（`launch` / `retrieve` / worker 与 `JobHandle`）。
- **本地 FastAPI 类比**（提交/列表/轮询、`parity-gaps`、`computables-preview`、`queue-stats`、`repro`-only）：[技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)（契约 **§2–§7**；决策 **§9**）。
- **`JobHandle.protocol_hash`**：与入队时 `SqliteJobStore` 中 `protocol_hash` 列一致，为 pickled 协议体的 SHA-256 前缀，便于和 `repro` 中作业指纹对账，**不** 等价于云侧项目 ID。
- **`retrieve`**：语义同 `store.result(job_id)`；`status != DONE` 时**不**应假定存在 `expectation`（见 `PauliAveragingProtocol.retrieve` docstring）。

**优化**：

- PMSV：从 stub 升级为「stabilizer 列表 + 每 stabilizer 投影」接口，与 `filter_shots_pmsv` 或真实比特串过滤衔接。
- ZNE：当前为 `zne_scale_energy` 标度；若走真实电路放大，需与 `dataframe_circuit_shot_rows` 多倍行对齐。

---

## 8. DMET / MD / ML（差异化长板）

- `md_bridge`、`QMEFDataset`、surrogate/active learning 是相对于「纯 InQuanto 化学核」的扩展长板。
- 竞品文 §4：大体系论文应写清 fragment 自洽轮数与经典参考档。**二轮**：`DMETContext` 增加可选字段 `n_scf_cycles_embedding`、`classical_reference_method` 供流水线写入；全量 DMET 自洽循环仍为扩展项。

---

## 9. 优先实施顺序（路线图）

以下按「对标可证伪性」与「实现耦合度」排序：

1. **文档与元数据**：~~判据表字段导出；Protocol `run` 语义澄清；`QubitHamiltonian.meta` 扩展~~（首轮：`parity_snapshot`、`_counts` 机读语义、Hamiltonian `meta`；**二轮**：`scripts/export_parity_criteria_table.py`）。
2. **Shot 真采样路径**：`run_sampled` 为 statevector 上分组蒙特卡洛；`run_qiskit_shots_pauli_protocol` 为 Qiskit `get_counts` 比特串（Aer/硬件，见 [技术文档_设备比特串与Qiskit采样路径.md](/reference/qiskit-shot-counts)），与 `pauli_shot_sim` 同构的重组与直方图 schema。
3. **QSE shot 矩阵元**：`run_from_vqe_hea_basis_pauli_transitions` + `QSEPauliTransitionSchedule`（与分组 Pauli 日程衔接的独立模块）。
4. **VQD 三通道**：`three_protocol` 报告块（能量分组采样 / swap-test 重叠 / 权重）；优化仍为单目标。
5. **SCEOM**：`run_sceom_nested_commutator`（q-sc-EOM 嵌套对易子）；**仍缺** 费米 \(S\)、自洽与 InQuanto 分析 DataFrame。
6. **测量直方图**：`run_sampled` 或 `run_qiskit_shots_pauli_protocol` + `record_pauli_measurement_histograms` → `measurement_histogram_rows`（statevector 模拟或 Qiskit 计数；`source` 区分）。
7. **PMSV 方差修正**：~~接受率进 stderr~~（首轮已做保守放大）。
8. **ADAPT 每步 Pauli 计费**：~~元数据进 `adapt_meta`~~ → `adapt_steps` / `total_gradient_evals`（首轮）。

---

## 10. 模块索引（便于维护者跳转）

| 主题 | 路径 |
|------|------|
| 五阶段协议 | `src/qchem_stack/protocols/protocol.py` |
| Shots 界 | `src/qchem_stack/backends/shot_budget.py` |
| Pauli 分组 | `src/qchem_stack/backends/pauli_grouping.py` |
| 哈密顿量 / JW | `src/qchem_stack/chem/hamiltonian.py` |
| VQE / ADAPT | `quantum/algorithms/vqe.py`, `adapt.py` |
| VQD / QSE | `quantum/algorithms/excited.py`, `quantum/qse_transition.py` |
| SCEOM | `quantum/algorithms/sceom.py` |
| 流水线 | `orchestration/pipeline.py`（含 `nexus_analog_ledger`、`mitigation_*`、`nexus_cloud_repro`、`tensornet_protocol_stub` 挂接） |
| 能力矩阵 | `docs/inquanto_public_parity_matrix.md` |
| **缓解（Qermit 风格 + 存根）** | `mitigation/qermit_analog.py`, `mitigation/qermit_runtime.py`, `mitigation/pmsv.py`, `mitigation/zne.py` |
| **张量网（CuTensorNet 类比）** | `tensornet/cutensornet_protocol_stub.py`（`quantum.tensornet_expectation_stub`、`tensornet_contraction_engine`） |
| **计价 / 云侧车** | `jobs/nexus_analog.py`, `jobs/cost.py`, `jobs/nexus_cloud.py` |
| **周期 / 溶剂（PySCF）** | `chem/drivers/pyscf_driver.py`, `config.ChemistryExtendedSpec`（PBC、k 网、ddCOSMO）；名称映射 `chem/inquanto_driver_surface.py` |
| **资源行（自研）** | `backends/spec.py`（`CircuitIR`, `circuit_resource_row`） |
| **TKET 桥（可选）** | `backends/pytket_bridge.py`；`pip install qchem-stack[pytket]` |
| 作业与队列 | `jobs/store.py`（`JobHandle`, `SqliteJobStore`，`full_pipeline` + `list_jobs`/`count_by_status`） |
| **HTTP API（可选）** | `api/app.py` |
| **可观测性** | `orchestration/run_context.py`（`RunContext`, `PipelineStageTimer`） |
| 全管线异步入队 | `jobs/pipeline_jobs.py`, `jobs/pipeline_runner.py`, `jobs/worker_dispatch.py` |
| 详细技术 | [技术文档_CircuitIR与TKET桥接及作业契约.md](/reference/circuitir-tket-jobs) |
| **HTTP / SQLite 队列 / 可观测性** | [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)（含 §9 维护决策） |

---

## 11. A/B/C 工程轮次摘要（与公开 InQuanto 分层的工程对齐）

本轮在**不扩大闭源复现声索**的前提下，补齐三处可审计工程面：

| 轮次 | 内容 | 维护入口 |
|------|------|----------|
| **A** | 可选 **pytket**：`circuit_ir_to_pytket` / `pytket_circuit_stats` / `enrich_row_with_pytket`；跳过 `PAULI_GROUP` 与 `ANNOTATION`；`resource_estimation_demo.py --pytket` | `backends/pytket_bridge.py`，`pyproject` optional `pytket` |
| **B** | **README**「InQuanto public stack vs this repo」表 + 链到本工程记忆、parity、launch 类比、技术文档 | `README.md` |
| **C** | **`JobHandle.protocol_hash`** 与 `enqueue` 对齐；`retrieve` 语义与 parity 第 1 行脚注；`test_job_flow` 断言 | `jobs/store.py`，`protocols/protocol.py`，[launch_retrieve_nexus_analog.md](/concept/launch-retrieve-nexus-analog) |

**与竞品「Methods/判据」的用法**：自研 `depth`/`twoq` 行用于与历史 `qchem_stack` 结果一致；若论文需强调 **TKET 生态** 一致口径，在补充材料增加 `pytket_*` 列并引用技术文档 §3。

---

## 12. 一句话收束

**深度对标**应钉在：活性空间与 Pauli 支撑、Protocol 支撑集与总 shots、激发态矩阵元/重叠的**独立统计通道**、缓解下的有效样本与方差——本工程在「编排 + 公开可审计」上有优势；下一阶段应把 **QSE/VQD 的 shot 级对象** 与 **Protocol run 的采样语义** 做成与竞品 Methods 同构的可发表闭环。

---

## 13. 开放栈对标完成度与待闭合项（原独立记忆合并）

**文档性质**：维护者决策记忆；口径与 [架构_InQuanto闭源能力闭合与可复现边界.md](/concept/architecture-boundaries) 一致：**L1 可审计**，非 **L0 闭源等价**。

**关联技术说明**：

- [技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot)
- [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs)
- 机读差距：`qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`
- **聚合开放参考单包**：`parity_snapshot.open_gap_closure_reference`（`integrations/gap_closure_bundle.py`）

### 13.1 我们「自己设计」的原则（闭源看不见时）

| 原则 | 含义 |
|------|------|
| 阶段对齐 | SCF → 嵌入标签/意图 → 变分 → Pauli/编译/缓解 → 台账，与公开教程叙事同构 |
| 合同优先 | 用 JSON schema 式字段（`parity_snapshot`、`embedding_workflow`）固定语义，便于审稿与 CI |
| 参考实现可替换 | Protocol/钩子保留；stub 仅用于无 PySCF/无账户的 CI |
| 诚实标注 | `epistemic_binding`、`caveat`、`dmet_solver_mode` 写明假设与不可冒充边界 |

### 13.2 已在仓库落地的「开源侧」能力（≠ 对方闭源默认逐比特一致）

| 原「缺口」叙事项 | 开源侧落地 | 说明 |
|------------------|-----------|------|
| Chemically aware UCC | `SinglesBeforeDoublesLexicographic`、`GreedyCommutingFermionicLayers`（OpenFermion commutator 分层）、`ChemicallyAwareUCCPolicy` 仍保留 | 文献可解释重组，**非** InQuanto 内部启发式 |
| TKET 全链 / 编译 | `circuit_ir_tket_peephole_optimize_stats_or_none`（`FullPeepholeOptimise` before/after）、原 `circuit_ir_to_tket_stats_or_none` | **无** 商业离子阱私有 pass |
| Nexus / HQC 工作流 | `nexus_public_workflow_blueprint`、既有 `nexus_cloud` / `nexus_analog` / `qnexus_probe`；**本地**可选 HTTP + `SqliteJobStore`（`api/app.py`） | **无** 真计费/队列二进制 |
| Qermit | `qermit_mitigation_execution_overlays`、`mitigation_graph_report.execution_class_manifest` | **非** CQCL MitEx/MitRes |
| cuTensorNet / TN 期望 | `tensornet.dense_expectation_reference`、stub + cuQuantum 探测保持 | **无** 大规模化学 TN 拓扑自动生成 |
| 多片段 DMET | `DMETSelfConsistencyLoop` + **`run_uniform_hamiltonian_multifragment_toy`** | **非物理** bath：每片段同一全局 H，仅验证多片段循环 |
| Schmidt 嵌入 + 外层 SCF | **`run_schmidt_density_feedback_cycles`**、**`run_schmidt_multifragment_density_cycles`** + 单片段 `schmidt_atomic_production` | **工程**对标 DMET *工作流形态*；**非**闭源 bath 拟合 |
| L3 统计 | `l3_statistics_reference.energy_bootstrap_ci_stub` | bootstrap **示意** |
| COSMO/PBC 驱动 | `open_driver_coverage_matrix` | **声明式**覆盖表 + PySCF 已实现路径 |

**默认进快照的大包**：`ParityIntegrationsSpec.gap_closure_reference_bundle`（默认 `True`）→ `open_gap_closure_reference`（`open_gap_closure_reference_v1`）。

### 13.3 原则上无法由本仓库「做完」的部分（L0 / 商业域）

- 与 **闭源 wheel / 未公开 API** 的二进制或秘传超参一致（L0）。
- **真实 HQC 账单、Nexus 生产 SLA、专用服务器侧 MitEx 调度延迟**。
- **与某台 H 系列硬件** 在无人值班条件下的逐 shot 复现（L2/L3 需共同实验协议与原始数据）。

若将来对方公开可检证接口，优先增厚 `integrations.*` 与 `parity_snapshot`，而非猜测闭包内行为。

### 13.4 维护动作备忘

- 能力变化时同步：`inquanto_gap_categories()`、[inquanto_public_parity_matrix.md](/parity/public-matrix)。
- 新增 `parity_snapshot` 顶层键时：更新本节 §13.2、[技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot)（若 DMET 相关）。
- 变更 **HTTP 路由** / **作业表 `meta`** / **`run_context` 头** / **`pipeline_profile`** 时：同步 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs) **§9**，并跑 `tests/test_api_runs.py`、`tests/test_job_store_list.py` 等。

---

*文档版本：与仓库源码同步维护；重大行为变更时请更新 §1（缓解行）、§4、§7、§9、**§11**、**§13** 及 [技术文档_CircuitIR与TKET桥接及作业契约.md](/reference/circuitir-tket-jobs)；必要时 bump 配置 `schema_version`（若引入破坏性 YAML 字段）。*
