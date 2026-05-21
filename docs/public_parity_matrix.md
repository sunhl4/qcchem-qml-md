# 公开能力契约 vs `qchem_stack` 覆盖矩阵

**目的**：对照公开发表的量子化学软件能力叙事与可检证键，说明本仓库 **独立实现** 的等价程度；**不**声称复现任意闭源二进制或默认超参数。

**用户指南级叙事映射（How to use）**：[工程记忆 §14](工程记忆_Quantinuum对标与数据流技术文档.md) 与 Docusaurus [化学与嵌入](../docusaurus-site/docs/guide/chemistry-and-embedding.md)（站内路径 `/guide/chemistry-and-embedding`）中的模块 / `repro` 出口。

**逐项闭合执行计划（B→J 顺序，L1 对拍定义）**：见本页与 [CONTRIBUTING.md](../CONTRIBUTING.md) 中的 parity / gap 闸门；机读分类：`qchem_stack.protocols.product_contract.product_gap_categories`。**L1 签字清单**：维护者以 `CONTRIBUTING.md` 与 release 台账为准。

**差距清单 + 分阶段计划（维护稿）**：与本文件同源的引擎读字段见 `product_gap_categories()` / `GET /v1/meta/capability-surface`。

**边界（必读）**：把「公开叙事 + 可检证」做到底是 **L1**；**完全复现闭源商业包在内部默认值、全部 driver 组合与商业运行时细节**属于 **L0**，在无源码与许可下**不可作为工程承诺**。见 [工程记忆 §0](工程记忆_Quantinuum对标与数据流技术文档.md)。

**图例**：`yes` 已实现 / `partial` 部分或 API 形态不同 / `no` 未实现 / `n/a` 刻意不做或非公开范围

## 0. 非云、非专有硬件：对齐范围与「超越」（L1+）

**全面对齐（本仓承诺）**：除下述 **刻意排除** 项外，矩阵 §1–4 与 **`product_gap_categories()`**（HTTP **`gaps`** / 导出 JSON **`capability_gap_categories`**）、`GET /v1/meta/capability-surface` **同源**；`partial` 均配有 gap 锚点、caveat 或 [Y1 SLA 模板（附录 B §6）](public_parity_matrix.md#y1-residual-partial-sla-template)。
**执行状态（2026Q2）**：Day12–Day90 连续执行已完成本轮收口（`docs/execution/day90_final_closeout_2026Q2.md`）；**Tangelo 差距日历滚动收口**见 `docs/execution/day090_tangelo_calendar_closeout.md`（与 `docs/execution/day001_day090_tangelo_gap_calendar.md` 同源）。后续迭代计划见 `docs/execution/day91_next_phase_plan_2026Q3.md`（Day91–Day120 日拆解：`docs/execution/day91_day120_daily_breakdown_2026Q3.md`）。**2026Q3 执行规划**：见 `docs/execution/comparative_execution_rd_plan_strict_2026Q3Q4.md` 与 `docs/execution/comparative_execution_backlog.yaml`（历史日历文件名已归档，勿再引用已删除路径）。

**刻意排除（不对齐、不宣称超越）**：Quantinuum **商业云**（Nexus / `qnexus` / HQC / OAuth / 配额）与 **专有硬件**（H 系等校准、原生门集、拓扑专优）。矩阵中该类行保持 `n/a` 或本地类比。

**「超越」的可辩护含义**（相对「公开资料 + 闭源产品包」在 **工程可检证性** 上的加强，**非** L0 数值/二进制等价）：

- **全栈开源可审计**：Methods 级编排不依赖闭源 wheel 即可复现语义与 JSON 契约。
- **判据与 CI 闸门**：`parity_snapshot` 键注册、`export_parity_criteria_table`、`check_parity_export_sample`、全量 pytest。
- **多后端可插拔**：同一 YAML 下 statevector / Qiskit / ionstack mock。
- **MD/ML 扩展面**：`md_bridge` / QMEFDataset（相对纯化学闭合产品的长板）。

机读汇总（与 HTTP 同源）：同一响应体含 **`object_map`**、**`gaps`**、**`mitigation_execution_model`**、**`open_stack_differentiators`**（schema **`open_stack_differentiators_v1`**：`scope_excludes`、`beyond_public_doc_bundle`）、**`tangelo_public_mapping_alias_surface_v1`**、**`operator_pool_registry_export_v1`**（ADAPT/IQEB 池 id 与 **`pool_id_aliases`**）、**`algorithm_registry_export_v1`**、**`variational_registry_export_v1`**。

## 1. Protocols 与工作流

| 公开能力 | 官方入口 | qchem_stack |
|----------|----------|-------------|
| 五阶段 instantiate→build→compile→run→evaluate | [Protocols overview](https://www.quantinuum.com/) | `partial`：五阶段有等价；可选 `run_sampled`（statevector MC）与 `run_qiskit_shots_pauli_protocol`（Qiskit `get_counts` / Aer/硬件，见 [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md)）；五阶段上可挂 **`nexus_analog` 计价**与 **`zne_scales`**（若启用 ZNE）。异步侧 **非** Nexus 1:1，见 [launch/retrieve 对照](launch_retrieve_nexus_analog.md)（`JobHandle` 含 `protocol_hash`，本地 SQLite 队列 + worker；pickle 协议上带 `NexusAnalogSpec` 与同步计价一致） |
| `dataframe_circuit_shot` 式资源表 | [Resource estimation](https://www.quantinuum.com/) | `yes`：`dataframe_circuit_shot_rows` + `spec.dataframe_circuit_shot`；导出侧可选 `resource_estimation_preview_v1`（`parity_integrations.resource_estimation_preview: true`）用于 Methods 轻量切片，**非**云计价、非闭源 L0 resource estimator。并可在同开关下导出 `algorithm_registry_alignment_v1` / `md_ml_repro_freeze_fields_v1` 作为 W5/W6 机读证据块（内含 **`operator_pool_registry_export_v1`**）。 |
| 公开 `Computable` / Methods 摘要（文档向） | API 与导出脚本 | `partial`→**可检证 L1**：YAML 机读 `POST /v1/meta/computables-preview`、`POST /v1/meta/workflow-preview`（五阶段 + `computable_graph_v2` + 可选 `include_computables_rich` → **`computables_rich_v1`**）；跑完后 slim 面板 `GET /v1/runs/{id}/summary`，完整 `repro` 见 `GET /v1/runs/{id}/repro`（`DONE`）；gap `composable_computable` 状态 **`analog_v2_semantic_graph_rich_optional`** |
| 作业提交 / 列表 / 轮询（产品网关） | Nexus / 云侧 UX 叙事 | `partial`：**本地 FastAPI 类比** `qchem_stack.api`：`POST/GET /v1/runs`、`GET /v1/meta/parity-gaps`、**`POST /v1/meta/computables-preview`**、**`GET /v1/meta/queue-stats`**；无厂商身份与配额，见 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §9、[launch/retrieve 对照](launch_retrieve_nexus_analog.md) |
| `qnexus` / HQC 计价 | 同上 | `n/a` + **本地类比**：`jobs/cost` + `nexus_analog` 权重（`nexus_analog_ledger` / 作业 `nexus_analog_billing`）；**不**伪造 HQC 货币。可选 `nexus_cloud`（`http`/`mock` 侧车条，非厂商 SDK） |
| Qermit `MitRes`/`MitEx` | [Noise mitigation](https://www.quantinuum.com/) | `partial`：`PMSV`/`ZNE`/`SPAM` 存根；可选 **`mitigation.classical_shadows_stub_enabled`**（DAG：`classical_shadows_expectation_stub` 置于 SPAM 之后、PMSV 之前；`configs/example_h2_classical_shadows_stub.yaml`；迹Homology见 `tests/test_mitigation_dag_trace_homology.py`）；可选 **`mitigation.zne_mode=circuit_scale_fold`**（每尺度 HEA 放大 + `protocol_counts.zne_curve` 写入 **`mitigation_dag_execution`**）；**ZNE×Qiskit Pauli** 与 YAML 口径合一机读块 **`parity_snapshot.zne_qiskit_unification_v1`**（见 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md)）；Methods：`resource_estimation_preview_v1` / `methods_resource_unified_v1` 镜像 **`mitigation_zne_mode_yaml`**、**`mitigation_zne_scales_yaml`**，`--results` 另附 **`parity_snapshot_mitigation_zne_*`**；**机读图** `mitigation/qermit_analog`（`qermit_analog_v2`：`nodes`+`edges`+`topological_order`）；**线性执行迹** `mitigation/qermit_runtime` → `mitigation_dag_execution`（非 Qermit 商业运行时）；**L1 顺序不变量**：DAG 中 SPAM/PMSV/ZNE 节点 `kind` 序列与 `mitigation_dag_execution.trace[].node` 一致（shadows stub 纳入同一不变量测试） |
| `CuTensorNetProtocol` | [vendor-cutensornet API](https://www.quantinuum.com/) | `n/a`（诚实降级）：开放栈仅 `tensornet/cutensornet_protocol_stub` + 引擎探测键 **`tensornet_engine_resolved`** / **`tensornet_fallback_reason`**；**不**随仓库附带 `vendor-cutensornet` 级化学尺度收缩或厂商二进制；若业务需要 L3 收缩 demo，走可选环境里 cuQuantum/cuPy，而非宣称产品 parity |

## 2. Algorithms（与 [algorithms API](https://www.quantinuum.com/) 对照）

| 公开类 | qchem_stack | 备注 |
|--------|-------------|------|
| `AlgorithmVQE` | `yes`：`quantum/algorithms/vqe.py`；可选 **`quantum.variational_ansatz: uccsd`**（JW，`quantum/algorithms/uccsd_vqe.py` — 稠密簇指数或对 **`quantum.uccsd_trotter_steps`** 一阶 Trotter 层重复，`configs/example_h2_uccsd.yaml` / `configs/example_h2_uccsd_trotter.yaml`）；**JW/BK 工程裁断**见 **`docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md`**；**`n/a`**：同一 UCCSD Trotter 电路语义 **未** 在 BK/SCBK 参考态上包装（变分层仍可用 HEA+BK/SCBK Hamiltonian） |
| `AlgorithmAdaptVQE` / FermionicAdapt | `partial(interface-ready)`：`adapt.py` 已切到 **commutator gradient** + 可执行 pool registry（`fermionic_uccsd`/`toy_pair_xx`）；新增 `quantum.algorithm: tetris_adapt`（同轮多算符追加，实验态） |
| `AlgorithmIQEB` | `partial(interface-ready)`：`IQEBVQE` 外层支持 `iqeb_n_grads` + `iqeb_energy_tolerance` + pool registry（默认 `iqeb_qubit_excitation`）；仍属开放栈等价实现而非闭源逐行同构 |
| `AlgorithmVQD` | `partial`：`excited.py` 多级 deflation；**优化单目标**，**报告**三通道 `three_protocol`（能量 Pauli 采样 / swap-test 重叠 / 权重）。变分流形：**HEA**（`configs/example_h2_excited_smoke.yaml`）或 **UCCSD 同簇紧缩**（`configs/example_h2_vqd_uccsd.yaml`，经 `prepare_state`）。行为与契约详解：**[技术文档_VQD紧缩激发与跨栈对照.md](技术文档_VQD紧缩激发与跨栈对照.md)** |
| `AlgorithmQSE` | `partial`：`excited.py` + `quantum/qse_transition.py`：`run_from_vqe_hea_basis_pauli_transitions`（逐 $(i,j)$ Pauli 项噪声 + 日程）；稠密参考仍可用 |
| `AlgorithmSCEOM` | `partial`：`run_sceom_nested_commutator`（D2SC05371C 型 $M_{ij}=\langle\psi\|[S_i^\dagger,[H,S_j]]\|\psi\rangle$，Pauli 玩具生成元）+ 参考子空间路径 |
| `Algorithm*QPE` | `partial(interface-ready)`：新增 `quantum/algorithms/qpe.py`（`AlgorithmDeterministicQPE` / `AlgorithmKitaevQPE` / `AlgorithmInfoTheoryQPE`）并接入 demo track；主配置树仍通过 `qpe_demo_track_after_variational` / `qpe_pipeline_integration` 出具报告；完工后 **`run_summary.qpe_open_stack_contract_v1`** 给出稳定实施路径别名（对齐 Methods / `methods_resource_unified_v1`） |
| `AlgorithmVQS` / `AlgorithmMcLachlan*` | `partial(interface-ready)`：``quantum/algorithms/vqs.py`` + **主配置侧车** `quantum.vqs_track_after_variational` / `quantum.vqs_pipeline_integration` → 管线输出 `vqs_track`（`vqs_track_v1`）与 `run_summary.vqs_open_stack_contract_v1`；示例 `configs/example_h2_vqs_track.yaml`；动力学 RHS 仍为开放栈占位，**非** 产品级时间演化 parity |
| `AlgorithmBayesianQPE` + Phayes | `partial`：`qpe_qec_demo/bayesian_stub.py`（`BayesianQPEStub`）；模块说明见 [`qpe_qec_demo/README.md`](../src/qchem_stack/qpe_qec_demo/README.md)；并入 `qpe_demo_track` / `run_summary.qpe_demo_track_ran`；同上 **`run_summary.qpe_open_stack_contract_v1`**；单测 `tests/test_l1_phase_c_iqeb_bayesian.py` |
| YAML `quantum.algorithm_factory` / `variational_plugins` | `partial`：注册表 + YAML 导入路径派发；示例 `configs/example_h2_echo_variational_plugin.yaml`；parity 导出 **`variational_registry_export_v1`**（嵌于 `algorithm_registry_alignment_v1`，需 `parity_integrations.resource_estimation_preview: true`） |
| `quantum.adapt_pool_id` / `quantum.iqeb_pool_id`（算符池） | `partial`：**可执行** `quantum/operator_pool_registry.py`（JW-mapped spin-UCCSD、可选 **`fermionic_uccsd_singles`** / **`fermionic_uccsd_doubles_only`**、**`iqeb_qubit_excitation`** 与 **`pool_id_aliases`**：`qubit_excitation`、`uccsd_jw`、`toy_pair_xx`）；示例 `configs/example_h2_adapt_singles_pool.yaml`、`example_h2_adapt_doubles_pool.yaml`、`example_h2_iqeb_fermionic_doubles_pool.yaml`、**`example_h2_iqeb_qubit_excitation_alias.yaml`**、`example_h2_adapt_uccsd_jw_alias.yaml`；广度索引见 `docs/算法面广度_Vendor platform_Tangelo对照索引.md`；`run_summary.adapt_pool_id_yaml` / `iqeb_pool_id_yaml`；**`GET /v1/meta/capability-surface`** 内嵌 **`operator_pool_registry_export_v1`**；parity / Methods 导出同 schema；相对 Tangelo / 厂商全套激发 taxonomy **仍为 partial** |

**Registry 钉扎（P2-W5）**：YAML `quantum.algorithm`、`quantum.algorithm_factory`（可选插件）、算符池、`quantum.variational_ansatz`、fermion→qubit 映射的机读对照见 [附录 A §11](public_parity_matrix.md#p2-w5-algorithm-registry-alignment)与本节上表各行交叉维护；机读 gaps 增补 **`adapt_iqeb_operator_pool_surface`**。

## 3. Classical chemistry & embedding

| 能力 | qchem_stack | 备注 |
|------|-------------|------|
| Psi4 RHF → restricted active-space CASCI integrals → qubits | `yes`（`scf.driver=psi4`，`embedding.mode=none`，小活性空间）：`chem/integrals/psi4_active_space_exporter.py` + `CanonicalActiveSpaceIntegralPack`；样例 `configs/example_h2_psi4_rhf_sto3g.yaml`；**不**支持 Schmidt/AVAS/projection（配置层拒绝） |
| PySCF RHF / active space → qubits | `yes`：`chem/drivers`, `hamiltonian.py`；`active_space.strategy=cas|manual|avas_stub|avas`（`cas` 支持 `ncas/nelecas`，`manual` 支持 `n_active_* + frozen_orbitals`，兼容旧字段；**`avas_stub`**：`configs/example_h2_avas_stub.yaml`，与 **`cas` 同尺寸**，诚实元数据由 **`chem.active_space.mean_field_meta`** 写入（**无**阈值投影）；**`avas`**（仅 `scf.driver=pyscf`，需非空 **`chemistry_extended.avas_ao_labels`**）：`configs/example_h2_avas.yaml`，PySCF **`mcscf.avas.AVAS`** 阈值投影，`driver_meta.qchem_active_space_resolution_v1` + 管线回填 `ncas`/`nelecas`，能力位 **`SolverCapabilities.supports_avas_active_space_projection`**；**`chemistry_extended.avas_ao_labels`** 在非 **`strategy=avas`** 时仍可 **仅日志**（`avas_ao_labels_logging_only`）。**CASSCF 轨道**：`casscf_orbital_optimization_audit`（审计）与 **`casscf_orbital_optimization_for_integrals`**（单次 **`mcscf.CASSCF`** kernel，可选将优化 **`mo_coeff`** 接到 CASCI 型活性积分，`configs/example_h2_casscf_audit.yaml` 等）；`active_space.fermion_qubit_mapping`：`jordan_wigner`（默认）或 `bravyi_kitaev`；`repro.parity_snapshot.fermion_qubit_mapping`；可选 `chemistry_extended.classical_benchmark_enabled`；**管线能量分项账本**：`energy_components_v1`。**几何与 SCF**：`molecule.ecp`、`molecule.zmatrix`（与 Cartesian 互斥，`zmatrix` 内部经 PySCF `gto.M`）；**RI/DF**：`scf.density_fit` / `scf.density_fit_auxbasis`（`driver_meta`：`scf_density_fit`、`scf_density_fit_auxbasis`）；冻轨：`active_space.frozen_orbitals` → 管线写入 `driver_meta.active_space_frozen_orbitals` → PySCF CASCI **`frozen`**（电子数约束须满足 PySCF，见测试）；**轨道后处理**：`chemistry_extended.mo_coeff_transform_hook`（快照/导出 **`mo_coeff_transform_hook_v1`**，`identity`|`reverse_mo_columns`|``module:function``）；**一电子算符**：`PySCFDriver.compute_one_electron_operator_fermion` / `compute_one_electron_operator_pauli`（``kin|nuc|hcore|ovlp|r|rr|dm``，不等价闭源 ``compute_one_electron_operator`` 全文）；restricted MO 「量子问题三元组」仍以 **闭壳层 RHF** MF 为前提（其它 MF 在该入口显式报错）。**Vendor platform 级「产品默认」全套 AVAS/CASSCF 编排与闭源 UX**仍为 **`partial`**，边界见 [附录 A §10](public_parity_matrix.md#p2-w3-avas-casscf-boundary) |
| DMET 框架 / fragment solver 钩子 | `partial`：`chem/embedding/dmet.py`（`DMETContext` 含 `n_scf_cycles_embedding` / `classical_reference_method` 占位字段）；**小体系稠密 fragment 能**：`QubitHamiltonianFragmentSolverExact` + 多标签共享全局 Hamiltonian 演示（`configs/example_h4_dmet_fragment_exact_small.yaml`）；**Schmidt 路径**可选 JSON 侧车 `embedding.dmet.schmidt.bath_sidecar_json_path` → `embedding_workflow.schmidt_bath_sidecar_v1`；**ONIOM 玩具层元数据** `embedding.oniom_layers_v1` → `embedding_workflow.oniom_toy_v1`（`configs/example_oniom_toy.yaml`）；分解插件边界：`embedding.mode: plugin` + `embedding.plugin.name` / `json_path`（`configs/example_decomposition_plugin_toy.yaml` 等；**`decomposition_plugin_contract_v1`** 可选 per-fragment `fragment_energy_terms` 账本桩）；`embedding.embedding_input_representation=ao|lowdin_orth_ao` 可写入 `embedding_input_system`。Nested 键表见 [`docs/说明_embedding配置.md`](说明_embedding配置.md)。 |
| Projection embedding | `partial`：**L1 轨迹闭合** — `embedding.mode: projection` 写入 **`embedding_workflow`** + `parity_snapshot.projection_embedding_open_trace`。默认 `embedding.projection.quantum_hamiltonian: global_active_space` 时，变分阶段与全局 `ActiveSpaceSpec` 所选 fermion→qubit 映射相同（轨迹-only 元数据）。当设为 `fragment_mulliken_mo` 且提供 `embedding.projection.fragment_atom_indices` 时，变分 **`QubitHamiltonian`** 由 **RHF MO + 片段 Mulliken 排序 + PySCF CASCI 活性积分 + `active_space.fermion_qubit_mapping`** 构建（模块 `qchem_stack.chem.embedding.projection_hamiltonian`）。样例：`configs/example_h2_projection_trace.yaml`、`configs/example_h4_projection_mulliken.yaml`。 |
| Vendor platform 全量 driver/方法名表（COSMO、PBC、多 k…） | `partial`：**PySCF** 上已实现 **ddCOSMO**、**PBC**（`pbc_kpoint_mesh`：Γ 为 `RHF`，否则 `KRHF`）、**PBC+ddCOSMO 尝试**（受 PySCF 版本约束）；`chemistry_extended.rdm_correction_method=stub_*|pyscf_nevpt2_casci`（stub：零校正机读；`pyscf_nevpt2_casci`：**PySCF `mrpt.NEVPT`** on CASCI，开放钩子 **非** Vendor platform L0）；**非** 与 Vendor platform 闭源 `vendor-pyscf` 行级一一覆盖 |

**Parity export CI 抽样（几何 / SCF 扩展，config-only）**：`configs/example_h2_sto3g_density_fit.yaml`、`example_h2_zmatrix_sto3g.yaml`、`example_h2_zmatrix_sto3g_density_fit.yaml`、`example_mg_lanl2dz_ecp_rhf.yaml`、`example_mg_lanl2dz_ecp_density_fit.yaml`、`example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml` — 与 [`docusaurus-site/docs/parity/public-matrix.md`](../docusaurus-site/docs/parity/public-matrix.md) §3（主站）、本文 §3、`scripts/check_parity_export_sample.py` 内 `SAMPLE_CONFIGS_REL` **一致**。**`geometry_source`** 在上述导出中可被 CI 的稳定键门禁覆盖（见 `qchem_stack.protocols.product_contract.PARITY_EXPORT_V3_STABLE_KEYS`）。

统一口径：`scf.driver` 可替换；是否允许进入某条化学/嵌入分支由 `SolverCapabilities` 门控，不以驱动品牌字符串硬编码。
统一 `ChemIntegralSolver` 接口 90 天计划本轮已封板（见 `docs/execution/day090_unified_chemistry_interface_closeout.md`）。

## 4. 差异化（相对闭源产品）

- **编译 / TKET（`compiler_pass_bundle`）**：**默认**管线以 `CompilerSpec` + 自研 `CircuitIR` 为主，**不**要求安装 TKET；**可选** `pytket` 且开启 `parity_integrations.tket_first_circuit_stats` 时，才写入 `parity_snapshot.tket_first_compiled_circuit_probe`（Pauli 协议已编译出 `CircuitIR` 时）。Ion 阱专有 routing 与 Vendor platform 私有 pass 包 **不对齐**。叙事与字段见 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §2–4。
- **可复现**：YAML、`protocol_hash`、job 元数据、版本写入 `orchestration` 流水线；`JobHandle.protocol_hash` 与 SQLite `jobs` 表对账，详见 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) §6。
- **多后端**：`BackendSpec`（statevector / qiskit / ionstack mock）。
- **资源指标双轨**（与 Vendor platform「resource estimation / TKET」叙事对齐，**非** 伪造云计价）：`spec.circuit_resource_row` 自研深度；可选 `pytket` 时 `enrich_row_with_pytket` 增加 `pytket_depth` 等，见同技术文档 §2–4。
- **MD / ML**：`md_bridge/contracts.py` 与 `QMEFDataset` 长板。
- **成本透明**：每电路 shots、stderr、分组数；**不**绑定 Nexus HQC。可选 `nexus_cloud` 与 `nexus_analog` 的 **repro/侧车** 便于 Methods 对表（仍非真云凭据流）。
- **判据表导出**：`scripts/export_parity_criteria_table.py`（YAML + 可选运行结果 JSON）；config-only 顶键 **`geometry_source`** ∈ {`cartesian`,`zmatrix`}，与 **`molecular_system_from_experiment`** / `MoleculeSpec` 同源，便于 Methods 与竞品「问题构造」表对读。

## 5. PandM 文献对照

本仓库 **单仓克隆** 常不含 `PandM/` 长篇文献树；若你持有完整 monorepo，可在 **`PandM/materials/learning/quantum-chem/literature/`** 下检索「Quantinuum 竞品研究」「复现线」「数据流与判据」「激发态剖析」等文件名。  
**竞争定位与路线图**母稿：[`竞争定位与路线图_对标Quantinuum产品与技术路线.md`](竞争定位与路线图_对标Quantinuum产品与技术路线.md)。用户可读摘要：[docusaurus-site/docs/product/positioning.md](../docusaurus-site/docs/product/positioning.md)（站点路由 `/product/positioning`）。
