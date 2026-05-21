# 技术文档：DMET 形流程、`parity_snapshot` 开放契约与 `whole_active_system`

> **Nested schema v2**：配置字段见 [`docs/说明_embedding配置.md`](说明_embedding配置.md)。下列表格使用 nested 路径；`repro` / `embedding_workflow` 输出键名仍保留历史 flat 名称以便 parity 对表。

## 1. 配置：`EmbeddingSpec`

### 共享顶层

| 字段 | 说明 |
|------|------|
| `mode` | `none` / `dmet` / `projection` / **`plugin`** |
| `embedding_input_representation` | `mo` / `ao` / `lowdin_orth_ao` |
| `n_scf_cycles_embedding` | 设计意图上的自洽轮数（台账） |
| `classical_reference_method` | 文档/parity 用经典基线标签 |
| `oniom_layers_v1` | 玩具 QM/MM 层提示 → `embedding_workflow.oniom_toy_v1` |

### `mode: dmet` → `embedding.dmet`

| 字段 | 说明 |
|------|------|
| `fragment_labels` | 片段 id 列表 |
| `hamiltonian_source` | **`parity_stub`** / **`whole_active_system`** / **`schmidt_atomic_production`** |
| `target_fragment_electrons` | 可选 μ 标定目标 |
| `uniform_multifragment_toy` | 多片段玩具 wiring（与 schmidt 互斥） |
| `multifragment_one_shot_shared_hamiltonian` | 多标签共享同一 global `qh` 演示 |
| `fragment_solver.use_exact` / `exact_max_qubits` | 小体系稠密 ED 杂质求解 |
| `schmidt.*` | Schmidt + bath 生产路径（见 [`说明_embedding配置.md`](说明_embedding配置.md)） |
| `schmidt.bath_sidecar_json_path` | 可选 JSON → `embedding_workflow.schmidt_bath_sidecar_v1` |

### `mode: projection` → `embedding.projection`

| 字段 | 说明 |
|------|------|
| `quantum_hamiltonian` | `global_active_space` 或 **`fragment_mulliken_mo`** |
| `fragment_atom_indices` | Mulliken 模式必填 |

### `mode: plugin` → `embedding.plugin`

| 字段 | 说明 |
|------|------|
| `name` | 注册插件名 |
| `json_path` | 片段积分 JSON 路径 |

校验见 `qchem_stack.config._embedding_validation.validate_embedding`。

## 2. Pipeline 行为

1. SCF + 构造 **`qh`**：`schmidt_atomic_production` 时先按 `dmet.schmidt.dmet_max_cycles` 做密度反馈，再得到杂质 qubit Hamiltonian。
2. `mode == "dmet"` → `embedding_workflow`（输出键 **`dmet_hamiltonian_source`** 映射自 `dmet.hamiltonian_source`）。
3. `dmet.hamiltonian_source == "whole_active_system"` → `dmet_fragment_solve`（post-variational 演示）。
4. 主变分在 **`qh`** 上运行；单片段 `whole_active_system` 杂质 VQE 应与全局 VQE 一致。

## 3. `parity_snapshot` 关键键

| 键 | 含义 |
|----|------|
| `dmet_solver_mode` | `parity_stub` / `whole_active_system` / `schmidt_atomic_production` |
| `dmet_one_shot_open_ledger` | 单轮 driver 台账 |
| `schmidt_embedding_production` | Schmidt 审计块 |
| `projection_embedding_open_trace` | projection L1 轨迹 |

## 4. YAML 示例（nested）

```yaml
embedding:
  mode: dmet
  n_scf_cycles_embedding: 1
  dmet:
    fragment_labels: ["impurity"]
    hamiltonian_source: whole_active_system

quantum:
  algorithm: vqe
  vqe_depth: 1
  vqe_maxiter: 120
```

样例：`configs/example_h4_schmidt_multifragment.yaml`、`configs/example_decomposition_plugin_toy.yaml`。
