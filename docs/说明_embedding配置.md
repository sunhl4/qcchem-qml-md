# 实验 YAML 中的 `embedding:` 配置说明

本文说明 `src/qchem_stack/config/embedding_specs.py` 与 `embedding.py` 中嵌套 `EmbeddingSpec` 各字段、四种 `mode` 与 pre-quantum / post-variational 分工。配置加载见 [说明_实验配置加载_io.md](说明_实验配置加载_io.md)。

---

## Breaking change（nested schema v2）

自 nested 重构起，**不再支持 flat 键**（如 `embedding.schmidt_fragment_atom_indices`）。请改用子块：

| 旧 flat 键 | 新 nested 路径 |
|-----------|----------------|
| `dmet_hamiltonian_source` | `embedding.dmet.hamiltonian_source` |
| `fragment_labels` | `embedding.dmet.fragment_labels` |
| `schmidt_*` | `embedding.dmet.schmidt.*`（去掉 `schmidt_` 前缀） |
| `dmet_fragment_use_exact_solver` | `embedding.dmet.fragment_solver.use_exact` |
| `projection_*` | `embedding.projection.*` |
| `decomposition_plugin` | `embedding.plugin.name` |
| `decomposition_plugin_json_path` | `embedding.plugin.json_path` |


---

## 四种 `mode`（判别联合类型）

`mode` 决定允许出现的子块；错误 mode 下出现 `dmet` / `projection` / `plugin` 会在加载时报错。

| mode | 变分前是否改 `QubitHamiltonian` | 典型用途 |
|------|----------------------------------|----------|
| `none` | 否（走默认 CAS 活性空间） | 大多数 H₂ 示例 |
| `dmet` | 是（Schmidt 生产路径）或 parity/演示 | DMET 形 workflow |
| `projection` | 是（Mulliken 片段 MO 路径） | 片段投影 Hamiltonian |
| `plugin` | 是（JSON 积分插件） | 玩具 / 契约 Hamiltonian |

**变分之后**的 `embedding_workflow` 阶段仅做审计/演示，不改主路径 `qh`（`post_variational_embedding_audit_only=true`）。

---

## 共享顶层字段（所有 mode）

```yaml
embedding:
  mode: none
  embedding_input_representation: mo   # mo | ao | lowdin_orth_ao
  n_scf_cycles_embedding: null
  classical_reference_method: null
  oniom_layers_v1: []
```

---

## `mode: dmet` 示例（Schmidt 多片段）

```yaml
embedding:
  mode: dmet
  dmet:
    fragment_labels: ["left", "right"]
    hamiltonian_source: schmidt_atomic_production
    target_fragment_electrons: null
    uniform_multifragment_toy: false
    multifragment_one_shot_shared_hamiltonian: false
    fragment_solver:
      use_exact: false
      exact_max_qubits: 14
    schmidt:
      multi_fragment_atom_groups: [[0, 1], [2, 3]]
      multi_primary_fragment_index: 0
      n_bath_spatial: 1
      max_impurity_spatial_orbitals: 8
      dmet_max_cycles: 1
      dmet_mixing_alpha: 0.35
      dmet_convergence_tol: 1.0e-3
      run_vqe_on_all_fragments: false
      per_fragment_vqe_maxiter: null
      bath_sidecar_json_path: null
```

### `dmet.hamiltonian_source`

| 值 | 含义 |
|----|------|
| `parity_stub` | parity ledger 占位 |
| `whole_active_system` | 用全局 active-space `QubitHamiltonian` 作杂质（通常需 1 个 fragment label） |
| `schmidt_atomic_production` | SCF 密度 → Schmidt + bath → 杂质 JW 哈密顿量（主 VQE 目标） |

Schmidt 路径要求 `scf.method: RHF`；`schmidt.dmet_max_cycles` schema 上限 256，生产 guard 上限 50（见 `SCHMIDT_DMET_MAX_CYCLES_LIMIT`）。

---

## `mode: projection` 示例

```yaml
embedding:
  mode: projection
  n_scf_cycles_embedding: 1
  classical_reference_method: MP2
  projection:
    low_level: HF
    high_level: CAS
    threshold: 1.0e-8
    quantum_hamiltonian: fragment_mulliken_mo
    fragment_atom_indices: [0, 1]
```

`quantum_hamiltonian: fragment_mulliken_mo` 时 `fragment_atom_indices` 必填且需在分子原子范围内。

---

## `mode: plugin` 示例

```yaml
embedding:
  mode: plugin
  plugin:
    name: uniform_fragment_guess
    json_path: configs/decomposition_plugin_toy_integrals.json
```

---

## 代码 helper

| 函数 | 用途 |
|------|------|
| `is_schmidt_production(spec)` | 是否走 Schmidt 生产 pre-quantum 分支 |
| `is_projection_mulliken(spec)` | 是否走 Mulliken projection 分支 |
| `require_dmet(spec)` / `require_projection` / `require_plugin` | 类型窄化 |
| `resolve_schmidt_per_fragment_vqe_maxiter(cfg)` | per-fragment VQE 迭代上限 |

---

## 与 `pre_quantum_path` 的对应关系

`resolve_pre_quantum_path(cfg)` 优先级：

1. `scf.driver == precomputed` → precomputed bundle  
2. `mode == plugin` → embedding plugin  
3. Schmidt production（`dmet.hamiltonian_source`）  
4. projection Mulliken MO  
5. 默认 canonical active-space integral pack  

详见 `src/qchem_stack/chem/pre_quantum_path.py` 与 `docs/pre_quantum_yaml_matrix.md`。

## 相关文档

- [pre_quantum_yaml_matrix.md](pre_quantum_yaml_matrix.md) — 允许的组合矩阵
- [public_parity_matrix.md](public_parity_matrix.md) §3 — DMET / projection 能力行
- [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md) — DMET workflow 与 repro 键
- [学习路线图_框架理论到源码阅读顺序.md](学习路线图_框架理论到源码阅读顺序.md) §③ — pre-quantum 分支选路
