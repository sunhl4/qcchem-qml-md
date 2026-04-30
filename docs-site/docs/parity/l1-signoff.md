# L1 InQuanto 非云非硬件对齐签字清单

**契约**：与 [公开 parity 矩阵](/parity/public-matrix) + `qchem_stack.protocols.inquanto_contract` **同源**；**排除**真 Nexus/HQC 云产品与 H 系硬件标定。

| 矩阵锚点（parity_matrix_anchor / 表节） | gap.id（若有） | 证据（模块 / 键 / 测试） | 残余说明（caveat） |
|----------------------------------------|----------------|--------------------------|---------------------|
| §1 五阶段 Protocol | （叙事覆盖多项 gap） | `protocols/protocol.py`，`export_parity_criteria_table`，`POST /v1/meta/workflow-preview` | 异步作业非 Nexus 1:1 |
| §1 qnexus / HQC | `cloud_nexus` | `jobs/nexus_analog`，`nexus_cloud` | **非云**：本地类比 |
| §1 作业提交/轮询 | `http_submit_poll_workspace` | `api/app.py` `/v1/runs` | 无厂商身份/配额 |
| §1 Qermit | `qermit_graph` | `mitigation/qermit_analog`，`mitigation_execution_model_public`，见 [mitigation_PMSV_ZNE_Qermit_mapping.md](/concept/mitigation-mapping) | 非闭源 Qermit |
| §1 Computable | `composable_computable` | `computable_graph_v2`，`computable.py` | 语义 DAG，非厂商融合 |
| §1 CuTensorNet | `tensornet` | `cutensornet_protocol_stub`，`parity_snapshot.tensornet_engine_resolved` | 非 `inquanto-cutensornet` |
| §2 Algorithms | `ucc_chem_ansatz` 等 | `quantum/algorithms/*`，`INQUANTO_TO_QCHEM_OBJECT_MAP`；**IQEB**：`quantum.algorithm=iqeb`，`configs/example_h2_iqeb.yaml` | UCC 仍 partial；IQEB 为可选算法键 |
| §2 VQD `three_protocol` | — | `excited.py`，`export`：`vqd_three_protocol_present_from_run`（`--results`）；`tests/test_qse_sceom_vqd_extended.py` | 单目标优化 + 三通道报告 |
| §2 QSE / SCEOM | — | `qse_transition.py`，`meta.qse_shot_mode`，`sceom.py` 中 `shot_noise_model`；`export`：`qse_shot_mode_from_run_meta`，`sceom_shot_noise_model_from_run`（`--results`） | 与闭源默认可能不同 |
| §2 QPE track | — | `qpe_qec_demo/`，`run_summary.qpe_demo_track_ran`，`export` `qpe_*_from_run` | `configs/example_h2_qpe_track.yaml` |
| §3 PySCF / DMET | `dmet_scf_loop` | `chem/embedding`，`技术文档_DMET与parity_snapshot开放契约.md` | 全文献 DMET 需用户钩子 |
| §3 driver 表面 | `drivers_cosmo_pbc` | `chem/inquanto_driver_surface.py` | PySCF 版本约束 |
| §4 TKET / 编译 | `compiler_pass_bundle` | `CompilerSpec`，`tket_first_compiled_circuit_probe`，`技术文档_CircuitIR与TKET桥接及作业契约.md`，矩阵 §4 首条 | 无离子阱专有路由包 |
| 设备比特串期望 | `qpu_shot_histogram` | `run_qiskit_shots_pauli_protocol`，`技术文档_设备比特串与Qiskit采样路径.md` | 依赖 Qiskit/Aer |
| 集成参考包 | `integrations_closure_layer` | `parity_snapshot.open_gap_closure_reference`，`integrations/gap_closure_bundle.py` | L1 非 L0 |
| 评估支持集 | `evaluate_support_set` | `protocol_counts.hamiltonian_pauli_strings`，`pauli_support.assert_evaluate_compatible` | 保守兼容检查 |

**公开文档钉扎（Quantinuum InQuanto）**

- 对照站点：`https://docs.quantinuum.com/inquanto/`（含 protocols、algorithms、errmit、cutensornet 等手册/API）。
- **最近一次人工锚定日期**：2026-04-28。若公开站改版，按 [与InQuanto能力差距与实施计划.md](/parity/gap-implementation-plan) §5 做一次矩阵 + `inquanto_gap_categories` 差异登记（不自动视为功能回退）。

**M2 环境约定（完整管线 + export）**

- 需 **PySCF**：`tests/test_export_parity_golden.py::test_m2_pipeline_then_export_documented_keys`；无 PySCF 的 CI 以 **config-only** 三 YAML 导出 + 黄金样例 `tests/fixtures/parity_export_example_h2_config_only.json` 替代。

**机读键注册**：`PARITY_SNAPSHOT_DOCUMENTED_KEYS`、`PARITY_EXPORT_V2_STABLE_KEYS`（`protocols/inquanto_contract.py`）；快照全表见 [技术文档_DMET与parity_snapshot开放契约.md](/reference/dmet-parity-snapshot) §3 附录。

**回归**：`python -m pytest`；`python scripts/check_parity_export_sample.py`（仓库根；**抽样** `example_h2`、`tutorial_inquanto_chain_h2`、`example_h2_excited_smoke`）。

**负责人 / 日期**：（维护人填写）/ 2026-04-28
