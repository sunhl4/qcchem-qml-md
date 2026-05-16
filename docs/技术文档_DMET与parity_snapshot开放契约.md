# 技术文档：DMET 形流程、`parity_snapshot` 开放契约与 `whole_active_system`

## 1. 配置：`EmbeddingSpec`

| 字段 | 说明 |
|------|------|
| `mode` | `none` / `dmet` / `projection` / **`plugin`**（分解插件玩具层；需 `decomposition_plugin` + `decomposition_plugin_json_path`） |
| `fragment_labels` | DMET 模式下片段 id 列表 |
| `n_scf_cycles_embedding` | 设计意图上的自洽轮数（台账；完整数值循环需用户钩子） |
| `classical_reference_method` | 文档/parity 用经典基线标签 |
| **`dmet_hamiltonian_source`** | **`parity_stub`**：占位 dict，不求解。**`whole_active_system`**：杂质哈密顿量 = **全局活性空间** `QubitHamiltonian`；默认要求 **恰好一个** 非空 `fragment_labels`。若 `dmet_multifragment_one_shot_shared_hamiltonian: true`，允许 **≥2** 个标签：各片段杂质求解仍使用 **同一** 全局 `qh`（演示/可复现用，非物理多片段 DMET）。**`schmidt_atomic_production`**：Schmidt + 谱 bath 杂质 `qh`；`schmidt_dmet_max_cycles>1` 时先跑 `integrations/schmidt_dmet_self_consistent` 密度反馈（`repro` / `schmidt_dmet_self_consistency`），再可选 μ 与主 VQE。 |
| **`schmidt_bath_sidecar_json_path`** | 可选：相对实验 YAML 解析的 JSON，合并入 `embedding_workflow.schmidt_bath_sidecar_v1`（用户/Methods 审计钩子）。 |
| **`oniom_layers_v1`** | 玩具 QM/MM 层提示 → `embedding_workflow.oniom_toy_v1`（文档向元数据）。 |
| **`decomposition_plugin` / `decomposition_plugin_json_path`** | `mode=='plugin'` 时必填：注册玩具插件名 + 片段积分 JSON 路径。`decomposition_plugin_toy_v1` 载荷会校验 **`primary_fragment_id`**、每个 fragment 的 **`n_qubits`** 与 `pauli_coefficients[*].{label,coeff}`，并在 `embedding_workflow` 暴露 `decomposition_fragment_count` / `decomposition_fragment_ids` 摘要。 |

校验（`model_validator`，见 `config.py`）：

- `whole_active_system`：`mode == "dmet"`；默认 `len(fragment_labels)==1`；若 `dmet_multifragment_one_shot_shared_hamiltonian` 则 `len(fragment_labels)>=2`。
- `schmidt_atomic_production`：`mode == "dmet"`，且不得与 `dmet_uniform_multifragment_toy` 同时开启。**单片段**：`schmidt_fragment_atom_indices` 非空（且 `schmidt_multi_fragment_atom_groups` 为空）。**多片段**：`schmidt_multi_fragment_atom_groups` 非空、与 `schmidt_fragment_atom_indices` 互斥；可选 `fragment_labels` 与组数一致；`schmidt_multi_primary_fragment_index` 指定主线路 `qh` 对应的组。可选 `dmet_target_fragment_electrons` + `schmidt_run_mu_bisection`；**多轮密度反馈**：`schmidt_dmet_max_cycles`（>1）、`schmidt_dmet_mixing_alpha`、`schmidt_dmet_convergence_tol`。
- **`projection_quantum_hamiltonian == 'fragment_mulliken_mo'`**：要求 `mode=='projection'` 且 `projection_fragment_atom_indices` 非空。

## 2. Pipeline 行为

1. SCF + 构造 **`qh`**：`schmidt_atomic_production` 时先按 `schmidt_dmet_max_cycles` 做（可选多轮）密度反馈，再得到 **杂质 qubit Hamiltonian**（`active_space.fermion_qubit_mapping`，默认 Jordan–Wigner）`qh`；否则为全局活性空间 `molecular_hamiltonian_from_classical_reference`。
2. 若 `embedding.mode == "dmet"`，写入 `out["embedding_workflow"]`（含 `dmet_hamiltonian_source`、所用求解器类名字符串）；可选并入 **`schmidt_bath_sidecar_v1`**、**`oniom_toy_v1`**。若 `mode == "projection"`，写入 `out["embedding_workflow"]`（`schema: projection_embedding_workflow_v1`）记录投影工作流元数据。若 **`parity_integrations.enabled`** 且 `mode == "projection"`，另在开放栈快照中写入 **`parity_snapshot.projection_embedding_open_trace`**（`schema: projection_embedding_open_trace_v1`，见 `pipeline._append_open_stack_parity_fields`）。
3. 若 `dmet_hamiltonian_source == "whole_active_system"`，调用 `_run_dmet_fragment_solve_if_requested`：  
   `QubitHamiltonianFragmentSolverVQE` + `OneShotEmbeddingDriver.run(ctx, {label: qh})` → `out["dmet_fragment_solve"]`（并带 `hamiltonian_source` 字段）。
4. 主变分（VQE/ADAPT/IQEB）仍在 **`qh`** 上运行，与杂质 VQE **独立** 两次优化；在相同 `random_seed`、`vqe_depth`、`vqe_maxiter`、同一 `executor` 下，**单片段** `whole_active_system` 时杂质基态能量应与 `energy_after_variational` **数值一致**（见 `tests/test_orchestration_pipeline.py::test_dmet_whole_active_system_impurity_vqe_matches_global_vqe`）。**`dmet_multifragment_one_shot_shared_hamiltonian`** 路径不声称多片段物理自洽，仅验证驱动与杂质接口。

## 3. `parity_snapshot` 中与 DMET/开放栈相关的键

| 键 | 来源 | 含义 |
|----|------|------|
| `parity_integrations` | `ParityIntegrationsSpec.model_dump` | 开关快照 |
| `open_stack_contract_schema` | 静态 | `parity_open_stack_contract_v1` |
| `open_stack_design_intent` | 静态 | 开放替代物的设计声明 |
| `dmet_open_loop_architecture` | 静态（`mode==dmet`） | 自洽循环/单轮 driver 的 **类路径** 与工作流说明 |
| `dmet_one_shot_open_ledger` | 运行后 | `dmet_one_shot_v1`：either stub dicts or 真 VQE 行 |
| `dmet_solver_mode` | 运行后 | `parity_stub` / `whole_active_system` / `schmidt_atomic_production` |
| `schmidt_embedding_production` | 运行后（Schmidt 路径） | `schmidt_production_audit`：单轮或多轮 `schmidt_dmet_self_consistency`（`schema: schmidt_dmet_density_feedback_v1`） |
| `dmet_fragment_solve_error` | 异常路径 | 预留（当前校验主要在 Pydantic） |
| `projection_embedding_open_trace` | `parity_integrations.enabled` 且 `mode==projection` | `schema: projection_embedding_open_trace_v1`；与矩阵 §3 Projection 行同源（`embedding_workflow` 另有 `projection_embedding_workflow_v1`） |
| `tket_closure_layer_descriptor` | `parity_integrations` 开启 | TKET 开放层描述（编译阶段叙事） |
| `tket_first_compiled_circuit_probe` / `qnexus_probe` / … | 运行后 / 条件 | 见 ``pipeline._finalize_open_stack_parity_snapshot`` / ``_append_open_stack_parity_fields`` |
| `tensornet_engine_resolved` | 运行后 | TN stub 的 `engine_resolved` 或 YAML `tensornet_contraction_engine` |
| `tensornet_fallback_reason` | 运行后 | stub `status` 或 `tensornet_expectation_stub_disabled` 等 |

`collect_repro_metadata` 仅包含配置阶段字段；**`dmet_one_shot_open_ledger` / `dmet_solver_mode` / TKET 首电路探测** 在 `run_pipeline_sync` 末尾 `_finalize_open_stack_parity_snapshot` 合并进 **同一** `out["repro"]` 字典。

## 3b. `parity_snapshot` 顶层键与维护惯例

**已无单文件 frozenset 白名单**：历史上 `PARITY_SNAPSHOT_DOCUMENTED_KEYS` 曾与 dedicated 单测对齐；该注册表已从默认发行树移除。新增或更名 `parity_snapshot` 顶层键时，开发者应：

1. 在 **`qchem_stack.orchestration.pipeline`**（及 `parity_finalize`、`repro_metadata` / `repro_snapshot` 等快照装配处）写明字段语义并保证 JSON 安全；
2. 更新本节 §3 **摘要表**与相关中文技术文档（尤其是 DMET / 嵌入 / TKET 小节）；
3. 根据需要扩展 **`scripts/export_parity_criteria_table.py`**、**`scripts/check_parity_export_sample.py`**、`tests/fixtures/` Golden、以及 **`tests/test_orchestration_pipeline.py`**（或新增的聚焦用例）。

**导出块稳定键**：config-only 「判据」类 JSON **仍**须满足 **`qchem_stack.protocols.product_contract.PARITY_EXPORT_V3_STABLE_KEYS`**（由 `tests/test_export_parity_golden.py` 与 **`scripts/check_parity_export_sample.py`** 兜底）。

### 3c. 与 CI（两阶段快照）

写入 `parity_snapshot` 的常见阶段仍分为 **配置期** (`_repro_quantum_snapshot` + `_append_open_stack_parity_fields`) 与 **收尾期** (`_finalize_open_stack_parity_snapshot`)，详见前文 §3 表与各函数 docstring。**键名集合则以源码与上述脚本/测试为准**，不再从一个 `frozenset` 单点导出。

## 4. 求解器类

- **`VQEFragmentSolverStub`**：占位，返回类型名。
- **`QubitHamiltonianFragmentSolverVQE`**：`solve(fid, qh)` 内对 `QubitHamiltonian` 再跑 `VQE`；非 `QubitHamiltonian` 回退 stub。
- **`DMETSelfConsistencyLoop`**（`integrations/dmet_self_consistent.py`）：提供 `run_with_hooks(...)`；**未** 在默认 pipeline 中自动调用（多片段自洽需用户注入 `build_fragment_hamiltonian` / `update_bath`）。

## 5. 与真实 DMET 的差距（避免误用）

`whole_active_system` **不提供**：

- bath 轨道与 bath 哈密顿量；
- 多片段之间的全局密度 / 化学势自洽；
- DMET 文献中的完整 embedding 势能拟合。

它唯一保证的是：**在单片段覆盖全活性空间的理想化下，杂质 VQE 与全局 VQE 在同一算符上一致**，从而验证 **数据结构与求解器接口**。

## 6. YAML 示例片段

```yaml
embedding:
  mode: "dmet"
  fragment_labels: ["impurity"]
  dmet_hamiltonian_source: "whole_active_system"
  n_scf_cycles_embedding: 1

quantum:
  algorithm: "vqe"
  vqe_depth: 1
  vqe_maxiter: 120
  # use_pauli_protocol: false   # 若仅调 DMET+变分、缩短用例时可关
```

教程默认仍使用 `parity_stub`，以保持与占位台账教程一致；需要演示真杂质能量时改用 `whole_active_system`。
