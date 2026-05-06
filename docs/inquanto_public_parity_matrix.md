# InQuanto 公开契约 vs `qchem_stack` 覆盖矩阵

**目的**：仅对照 [Quantinuum 公开文档与 API](https://docs.quantinuum.com/inquanto/)，说明本仓库 **独立实现** 的等价程度；**不**声称复现闭源二进制或默认超参数。

**用户指南级叙事映射（How to use）**：[InQuanto_manual_howto_与_qchem_stack_映射.md](InQuanto_manual_howto_与_qchem_stack_映射.md) 对照官方 [How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html) 与本仓库模块 / `repro` 出口。

**逐项闭合执行计划（B→J 顺序，L1 对拍定义）**：[InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md)

**差距清单 + 分阶段计划（维护稿）**：[与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)（机读分类：`qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`）。**L1 签字清单**：[L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)。

**边界（必读）**：把「公开叙事 + 可检证」做到底是 **L1**；**完全复现 InQuanto 闭源包在内部默认值、全部 driver 组合与商业运行时细节**属于 **L0**，在无源码与许可下**不可作为工程承诺**。见 [架构_InQuanto闭源能力闭合与可复现边界.md](架构_InQuanto闭源能力闭合与可复现边界.md)。

**图例**：`yes` 已实现 / `partial` 部分或 API 形态不同 / `no` 未实现 / `n/a` 刻意不做或非公开范围

## 0. 非云、非专有硬件：对齐范围与「超越」（L1+）

**全面对齐（本仓承诺）**：除下述 **刻意排除** 项外，矩阵 §1–4 与机读表 `inquanto_gap_categories()`、`GET /v1/meta/capability-surface` **同源**；`partial` 均配有 gap 锚点、caveat 或 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)。

**刻意排除（不对齐、不宣称超越）**：Quantinuum **商业云**（Nexus / `qnexus` / HQC / OAuth / 配额）与 **专有硬件**（H 系等校准、原生门集、拓扑专优）。矩阵中该类行保持 `n/a` 或本地类比。

**「超越」的可辩护含义**（相对「公开 InQuanto 文档 + 闭源产品包」在 **工程可检证性** 上的加强，**非** L0 数值/二进制等价）：

- **全栈开源可审计**：Methods 级编排不依赖闭源 wheel 即可复现语义与 JSON 契约。
- **判据与 CI 闸门**：`parity_snapshot` 键注册、`export_parity_criteria_table`、`check_parity_export_sample`、全量 pytest。
- **多后端可插拔**：同一 YAML 下 statevector / Qiskit / ionstack mock。
- **MD/ML 扩展面**：`md_bridge` / QMEFDataset（相对纯化学闭合产品的长板）。

机读汇总（与 HTTP 同源）：**`capability_surface.open_stack_differentiators`**，schema **`open_stack_differentiators_v1`**（显式列出 `scope_excludes` 与 `beyond_public_doc_bundle`）。

## 1. Protocols 与工作流

| 公开能力 | 官方入口 | qchem_stack |
|----------|----------|-------------|
| 五阶段 instantiate→build→compile→run→evaluate | [Protocols overview](https://docs.quantinuum.com/inquanto/manual/protocols_overview.html) | `partial`：五阶段有等价；可选 `run_sampled`（statevector MC）与 `run_qiskit_shots_pauli_protocol`（Qiskit `get_counts` / Aer/硬件，见 [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md)）；五阶段上可挂 **`nexus_analog` 计价**与 **`zne_scales`**（若启用 ZNE）。异步侧 **非** Nexus 1:1，见 [launch/retrieve 对照](launch_retrieve_nexus_analog.md)（`JobHandle` 含 `protocol_hash`，本地 SQLite 队列 + worker；pickle 协议上带 `NexusAnalogSpec` 与同步计价一致） |
| `dataframe_circuit_shot` 式资源表 | [Resource estimation](https://docs.quantinuum.com/inquanto/manual/protocols/resource_estimation.html) | `yes`：`dataframe_circuit_shot_rows` + `spec.dataframe_circuit_shot` |
| 公开 `Computable` / Methods 摘要（文档向） | API 与导出脚本 | `partial`→**可检证 L1**：YAML 机读 `POST /v1/meta/computables-preview`、`POST /v1/meta/workflow-preview`（五阶段 + `computable_graph_v2` + 可选 `include_computables_rich` → **`computables_rich_v1`**）；跑完后 slim 面板 `GET /v1/runs/{id}/summary`，完整 `repro` 见 `GET /v1/runs/{id}/repro`（`DONE`）；gap `composable_computable` 状态 **`analog_v2_semantic_graph_rich_optional`** |
| 作业提交 / 列表 / 轮询（产品网关） | Nexus / 云侧 UX 叙事 | `partial`：**本地 FastAPI 类比** `qchem_stack.api`：`POST/GET /v1/runs`、`GET /v1/meta/parity-gaps`、**`POST /v1/meta/computables-preview`**、**`GET /v1/meta/queue-stats`**；无厂商身份与配额，见 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §9、[launch/retrieve 对照](launch_retrieve_nexus_analog.md) |
| `qnexus` / HQC 计价 | 同上 | `n/a` + **本地类比**：`jobs/cost` + `nexus_analog` 权重（`nexus_analog_ledger` / 作业 `nexus_analog_billing`）；**不**伪造 HQC 货币。可选 `nexus_cloud`（`http`/`mock` 侧车条，非厂商 SDK） |
| Qermit `MitRes`/`MitEx` | [Noise mitigation](https://docs.quantinuum.com/inquanto/manual/errmit.html) | `partial`：`PMSV`/`ZNE`/`SPAM` 存根；可选 **`mitigation.zne_mode=circuit_scale_fold`**（每尺度 HEA 放大 + `protocol_counts.zne_curve` 写入 **`mitigation_dag_execution`**）；**ZNE×Qiskit Pauli** 与 YAML 口径合一机读块 **`parity_snapshot.zne_qiskit_unification_v1`**（见 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md)）；**机读图** `mitigation/qermit_analog`（`qermit_analog_v2`：`nodes`+`edges`+`topological_order`）；**线性执行迹** `mitigation/qermit_runtime` → `mitigation_dag_execution`（非 Qermit 商业运行时）；**L1 顺序不变量**：DAG 中 SPAM/PMSV/ZNE 节点 `kind` 序列与 `mitigation_dag_execution.trace[].node` 一致（`tests/test_mitigation_dag_trace_homology.py`） |
| `CuTensorNetProtocol` | [inquanto-cutensornet API](https://docs.quantinuum.com/inquanto/api/extensions/inquanto-cutensornet_api.html) | `n/a`（诚实降级）：开放栈仅 `tensornet/cutensornet_protocol_stub` + 引擎探测键 **`tensornet_engine_resolved`** / **`tensornet_fallback_reason`**；**不**随仓库附带 `inquanto-cutensornet` 级化学尺度收缩或厂商二进制；若业务需要 L3 收缩 demo，走可选环境里 cuQuantum/cuPy，而非宣称产品 parity |

## 2. Algorithms（与 [algorithms API](https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html) 对照）

| 公开类 | qchem_stack | 备注 |
|--------|-------------|------|
| `AlgorithmVQE` | `yes`：`quantum/algorithms/vqe.py`；可选 **`quantum.variational_ansatz: uccsd`**（JW，`quantum/algorithms/uccsd_vqe.py` — 稠密簇指数或对 **`quantum.uccsd_trotter_steps`** 一阶 Trotter 层重复，`configs/example_h2_uccsd.yaml` / `configs/example_h2_uccsd_trotter.yaml`）；**`n/a`**：同一 UCCSD Trotter 电路语义 **未** 在 BK/SCBK 参考态上包装（变分层仍可用 HEA+BK/SCBK Hamiltonian） |
| `AlgorithmAdaptVQE` / FermionicAdapt | `partial`：`adapt.py`（形态与 **operator pool / 日程** 与 InQuanto、Tangelo 等公开「化学激发池」描述**非逐条对齐**；对照练习见 `configs/tutorial_inquanto_chain_h2.yaml`） |
| `AlgorithmIQEB` | `partial`：**管线可选** `quantum.algorithm: iqeb`（`IQEBVQE` 外层 + 内层 VQE）；`configs/example_h2_iqeb.yaml`；export / `run_summary` 含 **`iqeb_implementation_path`**（与 `export_parity_criteria_table` 恒定键一致）、**`iqeb_meta`** / **`iqeb_selected_pauli_strings`** |
| `AlgorithmVQD` | `partial`：`excited.py` 多级 deflation；优化单目标，**报告**三通道 `three_protocol`（能量 Pauli 采样 / swap-test 重叠 / 权重） |
| `AlgorithmQSE` | `partial`：`excited.py` + `quantum/qse_transition.py`：`run_from_vqe_hea_basis_pauli_transitions`（逐 $(i,j)$ Pauli 项噪声 + 日程）；稠密参考仍可用 |
| `AlgorithmSCEOM` | `partial`：`run_sceom_nested_commutator`（D2SC05371C 型 $M_{ij}=\langle\psi\|[S_i^\dagger,[H,S_j]]\|\psi\rangle$，Pauli 玩具生成元）+ 参考子空间路径 |
| `Algorithm*QPE` | `partial`：`qpe_qec_demo/`；**主配置树**：`quantum.qpe_demo_track_after_variational` 或 **`qpe_pipeline_integration`** → `qpe_qec_demo.pipeline_track.qpe_demo_track_payload`（`configs/qpe_dual_track_demo.yaml`）；**Methods + 可选 TKET 浅层合一**（演示验收）：`configs/example_h2_qpe_track_parity_integrations.yaml`（深度资源估计见 [P2_详细实施计划.md](P2_详细实施计划.md) P2-W1） |
| `AlgorithmBayesianQPE` + Phayes | `partial`：`qpe_qec_demo/bayesian_stub.py`（`BayesianQPEStub`）；模块说明见 [`qpe_qec_demo/README.md`](../src/qchem_stack/qpe_qec_demo/README.md)；并入 `qpe_demo_track` / `run_summary.qpe_demo_track_ran`；单测 `tests/test_l1_phase_c_iqeb_bayesian.py` |

**Registry 钉扎（P2-W5）**：YAML `quantum.algorithm`、变分 ansatz 名、fermion→qubit 映射的机读对照表见 [P2_W5_algorithm_registry_alignment.md](P2_W5_algorithm_registry_alignment.md)（与上表各行交叉维护）。

## 3. Classical chemistry & embedding

| 能力 | qchem_stack | 备注 |
|------|-------------|------|
| PySCF RHF / active space → qubits | `yes`：`chem/drivers`, `hamiltonian.py`；`active_space.fermion_qubit_mapping`：`jordan_wigner`（默认）或 `bravyi_kitaev`；`repro.parity_snapshot.fermion_qubit_mapping`；**AVAS / 全 CASSCF 产品深度**仍为 **`partial`**，边界见 [P2_W3_classical_avas_casscf_boundary.md](P2_W3_classical_avas_casscf_boundary.md) |
| DMET 框架 / fragment solver 钩子 | `partial`：`chem/embedding/dmet.py`（`DMETContext` 含 `n_scf_cycles_embedding` / `classical_reference_method` 占位字段）；**小体系稠密 fragment 能**：`QubitHamiltonianFragmentSolverExact` + 多标签共享全局 Hamiltonian 演示（`configs/example_h4_dmet_fragment_exact_small.yaml`）；**Schmidt 路径**可选 JSON 侧车 `embedding.schmidt_bath_sidecar_json_path` → `embedding_workflow.schmidt_bath_sidecar_v1`；**ONIOM 玩具层元数据** `embedding.oniom_layers_v1` → `embedding_workflow.oniom_toy_v1`（`configs/example_oniom_toy.yaml`）；分解插件边界：`embedding.mode: plugin` + `configs/example_decomposition_plugin_toy.yaml` |
| Projection embedding | `partial`：**L1 轨迹闭合** — `embedding.mode: projection` 写入 **`embedding_workflow`** + `parity_snapshot.projection_embedding_open_trace`。默认 `embedding.projection_quantum_hamiltonian: global_active_space` 时，变分阶段与全局 `ActiveSpaceSpec` 所选 fermion→qubit 映射相同（轨迹-only 元数据）。当设为 `fragment_mulliken_mo` 且提供 `projection_fragment_atom_indices` 时，变分 **`QubitHamiltonian`** 由 **RHF MO + 片段 Mulliken 排序 + PySCF CASCI 活性积分 + `active_space.fermion_qubit_mapping`** 构建（模块 `qchem_stack.chem.embedding.projection_hamiltonian`，**非** full many-body projection embedding，见快照 `epistemic_bound`）。样例：`configs/example_h2_projection_trace.yaml`、`configs/example_h4_projection_mulliken.yaml`。 |
| InQuanto 全量 driver/方法名表（COSMO、PBC、多 k…） | `partial`：名称映射击 `chem/inquanto_driver_surface`；**PySCF** 上已实现 **ddCOSMO**、**PBC**（`pbc_kpoint_mesh`：Γ 为 `RHF`，否则 `KRHF`）、**PBC+ddCOSMO 尝试**（受 PySCF 版本约束）；**非** 与 InQuanto 闭源 `inquanto-pyscf` 行级一一覆盖 |

## 4. 差异化（相对闭源产品）

- **编译 / TKET（`compiler_pass_bundle`）**：**默认**管线以 `CompilerSpec` + 自研 `CircuitIR` 为主，**不**要求安装 TKET；**可选** `pytket` 且开启 `parity_integrations.tket_first_circuit_stats` 时，才写入 `parity_snapshot.tket_first_compiled_circuit_probe`（Pauli 协议已编译出 `CircuitIR` 时）。Ion 阱专有 routing 与 InQuanto 私有 pass 包 **不对齐**。叙事与字段见 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §2–4。
- **可复现**：YAML、`protocol_hash`、job 元数据、版本写入 `orchestration` 流水线；`JobHandle.protocol_hash` 与 SQLite `jobs` 表对账，详见 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §6。
- **多后端**：`BackendSpec`（statevector / qiskit / ionstack mock）。
- **资源指标双轨**（与 InQuanto「resource estimation / TKET」叙事对齐，**非** 伪造云计价）：`spec.circuit_resource_row` 自研深度；可选 `pytket` 时 `enrich_row_with_pytket` 增加 `pytket_depth` 等，见同技术文档 §2–4。
- **MD / ML**：`md_bridge/contracts.py` 与 `QMEFDataset` 长板。
- **成本透明**：每电路 shots、stderr、分组数；**不**绑定 Nexus HQC。可选 `nexus_cloud` 与 `nexus_analog` 的 **repro/侧车** 便于 Methods 对表（仍非真云凭据流）。
- **判据表导出**：`scripts/export_parity_criteria_table.py`（YAML + 可选运行结果 JSON）。

## 5. PandM 文献对照

- 总索引：[Quantinuum_量子计算化学竞品研究总索引.md](../../PandM/materials/learning/quantum-chem/literature/Quantinuum_量子计算化学竞品研究总索引.md)（自 `qchem_qml_md/docs/` 相对仓库根 `Yaozheng`）
- 平替与复现线：[Quantinuum_代表性复现与平替方案.md](../../PandM/materials/learning/quantum-chem/literature/Quantinuum_代表性复现与平替方案.md)
- 数据流与判据：[Quantinuum_深度技术剖析_从积分到Shots的数据流与可证伪判据.md](../../PandM/materials/learning/quantum-chem/literature/Quantinuum_深度技术剖析_从积分到Shots的数据流与可证伪判据.md)
- 激发态：`Quantinuum_激发态深度剖析_VQD_QSE_SCEOM.md`
- 本包**竞争定位与分阶段目标**（相对 Quantinuum 产品/技术路线）：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md)
