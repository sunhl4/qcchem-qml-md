# Quantum 配置（`quantum` 节）

YAML 路径与 Python 属性一致，例如 `cfg.quantum.vqe.maxiter`、`cfg.quantum.variational.uccsd_trotter_steps`。

## 顶层

| 字段 | 说明 |
|------|------|
| `algorithm` | 变分算法 id：`vqe`、`adapt`、`iqeb`、`tetris_adapt` 等 |
| `algorithm_factory` | 可选插件导入路径 `module:callable`；默认仅允许 `qchem_stack.*` 模块 |

## 子块索引

| 子块 | 何时需要 | 关键字段 |
|------|----------|----------|
| `variational` | 所有变分阶段 | `ansatz`（`hea`/`uccsd`）、`uccsd_trotter_steps` |
| `vqe` | `algorithm=vqe` | `depth`、`maxiter`、`optimizer_method`、`initial_parameters_strategy` |
| `adapt` | `algorithm=adapt` | `max_iter`、`pool_id` |
| `iqeb` | `algorithm=iqeb` | `max_rounds`、`pool_id`、`n_grads`、`energy_tolerance` |
| `uccsd` | UCCSD Pauli 分解 | `decomposition_mode`（`pauli`/`unitary`） |
| `pauli` | Pauli 测量协议 | `use_protocol`、`run_sampled`、`run_qiskit_shots`、`grouping` |
| `excited.vqd` | VQD 激发态 | `after_variational`、`n_states`、`optimizer_mode`、`shots_*` |
| `excited.qse` | QSE | `shot_mode`、`expansion_pool`、`subspace_dim` |
| `excited.sceom` | SCEOM | `generator_strategy`、`subspace_dim` |
| `demos.qpe` / `demos.vqs` | 演示轨道 | `track_after_variational`、`pipeline_integration` |
| `tensornet` | 张量网 stub | `expectation_stub`、`contraction_engine` |
| `graph` | workflow-preview | computable 图边声明 |

## VQE + Pauli（最常见）

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  vqe:
    depth: 1
    maxiter: 200
    optimizer_method: COBYLA
  pauli:
    use_protocol: true
    run_sampled: false
    run_qiskit_shots: false
    grouping: greedy_commuting
```

## UCCSD Trotter

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: uccsd
    uccsd_trotter_steps: 2
  vqe:
    depth: 1
    maxiter: 100
```

见 [`技术文档_UCCSD_JW与BK_SCBK电路边界.md`](技术文档_UCCSD_JW与BK_SCBK电路边界.md)。

## 激发态（VQD 示例）

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  vqe:
    depth: 1
    maxiter: 50
  excited:
    vqd:
      after_variational: true
      n_states: 2
      optimizer_mode: three_computable
      shots_objective: 0
```

Packaged YAML：`configs/example_h2_excited_smoke.yaml`、`configs/example_h2_vqd_uccsd_three_computable.yaml`。

## ADAPT / IQEB 算符池

- `quantum.adapt.pool_id` / `quantum.iqeb.pool_id` 见 [`public_parity_matrix.md`](public_parity_matrix.md) 与算符池 registry。
- 示例：`configs/example_h2_adapt_singles_pool.yaml`、`configs/example_h2_iqeb.yaml`。

## Pauli shot 模式（互斥）

| YAML 标志 | 语义 |
|-----------|------|
| 默认（两者 false） | executor 精确期望 + 保守 stderr 界 |
| `pauli.run_sampled: true` | statevector 分组 Monte Carlo |
| `pauli.run_qiskit_shots: true` | Qiskit `get_counts` 比特串 |

**不可同时**开启 `run_sampled` 与 `run_qiskit_shots`。

## 插件与工厂

```yaml
quantum:
  algorithm: vqe
  algorithm_factory: qchem_stack.quantum.variational_plugins.loader:load_variational_runner_from_factory
```

路径须在 allowlist 内；见 [`quantum_模块风格约定.md`](quantum_模块风格约定.md)。

## 旧扁平键

仅接受嵌套块（`schema_version: "2"` 必填）。`quantum.uccsd_trotter_steps` 等 flat 键 **不再** 接受 — 使用 `quantum.variational.uccsd_trotter_steps`。

## 跨节校验

- UCCSD + BK/SCBK mapping 组合
- `md_ml_export` 与 backend provider
- excited shot budgets 与 backend provider

实现：`config/_experiment_validation.py`、`config/_quantum_validation.py`。

## 代码 helpers

只读解析：`qchem_stack.config.quantum_helpers`（`pauli_protocol_enabled`、`resolve_variational_algorithm` 等）。

## 延伸阅读

- [`说明_config模块技术参考手册.md`](说明_config模块技术参考手册.md) — 全字段
- [`quantum_InQuanto_Tangelo_对照矩阵.md`](quantum_InQuanto_Tangelo_对照矩阵.md) — 能力对照
