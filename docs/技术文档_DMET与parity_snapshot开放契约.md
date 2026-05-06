# 技术文档：DMET 形流程、`parity_snapshot` 开放契约与 `whole_active_system`

## 1. 配置：`EmbeddingSpec`

| 字段 | 说明 |
|------|------|
| `mode` | `none` / `dmet` / `projection` |
| `fragment_labels` | DMET 模式下片段 id 列表 |
| `n_scf_cycles_embedding` | 设计意图上的自洽轮数（台账；完整数值循环需用户钩子） |
| `classical_reference_method` | 文档/parity 用经典基线标签 |
| **`dmet_hamiltonian_source`** | **`parity_stub`**：占位 dict，不求解。**`whole_active_system`**：恰好 **一个** 非空 `fragment_labels`；杂质哈密顿量 = **全局活性空间** `QubitHamiltonian`。**`schmidt_atomic_production`**：Schmidt + 谱 bath 杂质 `qh`；`schmidt_dmet_max_cycles>1` 时先跑 `integrations/schmidt_dmet_self_consistent` 密度反馈（`repro` / `schmidt_dmet_self_consistency`），再可选 μ 与主 VQE。 |

校验（`model_validator`）：

- `whole_active_system` 要求 `mode == "dmet"` 且 `len(fragment_labels) == 1`（非空字符串）。
- `schmidt_atomic_production` 要求 `mode == "dmet"`，且不得与 `dmet_uniform_multifragment_toy` 同时开启。**单片段**：`schmidt_fragment_atom_indices` 非空（且 `schmidt_multi_fragment_atom_groups` 为空）。**多片段**：`schmidt_multi_fragment_atom_groups` 非空、与 `schmidt_fragment_atom_indices` 互斥；可选 `fragment_labels` 与组数一致；`schmidt_multi_primary_fragment_index` 指定主线路 `qh` 对应的组。可选 `dmet_target_fragment_electrons` + `schmidt_run_mu_bisection`；**多轮密度反馈**：`schmidt_dmet_max_cycles`（>1）、`schmidt_dmet_mixing_alpha`、`schmidt_dmet_convergence_tol`。

## 2. Pipeline 行为

1. SCF + 构造 **`qh`**：`schmidt_atomic_production` 时先按 `schmidt_dmet_max_cycles` 做（可选多轮）密度反馈，再得到 **杂质 qubit Hamiltonian**（`active_space.fermion_qubit_mapping`，默认 Jordan–Wigner）`qh`；否则为全局活性空间 `molecular_hamiltonian_from_pyscf`。
2. 若 `embedding.mode == "dmet"`，写入 `out["embedding_workflow"]`（含 `dmet_hamiltonian_source`、所用求解器类名字符串）。
3. 若 `dmet_hamiltonian_source == "whole_active_system"`，调用 `_run_dmet_fragment_solve_if_requested`：  
   `QubitHamiltonianFragmentSolverVQE` + `OneShotEmbeddingDriver.run(ctx, {label: qh})` → `out["dmet_fragment_solve"]`（并带 `hamiltonian_source` 字段）。
4. 主变分（VQE/ADAPT）仍在 **`qh`** 上运行，与杂质 VQE **独立** 两次优化；在相同 `random_seed`、`vqe_depth`、`vqe_maxiter`、同一 `executor` 下，单片段全空间时杂质基态能量应与 `energy_after_variational` **数值一致**（见 `tests/test_orchestration_pipeline.py::test_dmet_whole_active_system_impurity_vqe_matches_global_vqe`）。

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
| `tket_closure_layer_descriptor` | `parity_integrations` 开启 | TKET 开放层描述（编译阶段叙事） |
| `tket_first_compiled_circuit_probe` / `qnexus_probe` / … | 运行后 / 条件 | 见 ``pipeline._finalize_open_stack_parity_snapshot`` / ``_append_open_stack_parity_fields`` |
| `tensornet_engine_resolved` | 运行后 | TN stub 的 `engine_resolved` 或 YAML `tensornet_contraction_engine` |
| `tensornet_fallback_reason` | 运行后 | stub `status` 或 `tensornet_expectation_stub_disabled` 等 |

`collect_repro_metadata` 仅包含配置阶段字段；**`dmet_one_shot_open_ledger` / `dmet_solver_mode` / TKET 首电路探测** 在 `run_pipeline_sync` 末尾 `_finalize_open_stack_parity_snapshot` 合并进 **同一** `out["repro"]` 字典。

## 3b. `parity_snapshot` 顶层键注册（维护 CI）

权威集合：`qchem_stack.protocols.inquanto_contract.PARITY_SNAPSHOT_DOCUMENTED_KEYS`（新增快照字段时必须同步更新）。单测 `tests/test_parity_snapshot_key_registry.py` 校验 `collect_repro_metadata(..., qh=None)` 产出的快照键为该集合子集。

条件键（ParityIntegrations / DMET / Schmidt / TN stub）的实现溯源：`orchestration/pipeline._repro_quantum_snapshot`、`_append_open_stack_parity_fields`、`_finalize_open_stack_parity_snapshot`。

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
