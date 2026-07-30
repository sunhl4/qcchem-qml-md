---
title: protocols 模块
description: 五阶段 PauliAveragingProtocol、computables 与 product_contract。
---

# protocols 模块

`qchem_stack.protocols` 负责逻辑测量电路、能量估计协议、computable 图与 product / parity 契约导出。

深读请优先：[Pauli 平均协议深读](./quantum/algorithms/pauli-protocol)。选型：[Pauli 协议与 shots](/guide/pauli-protocol-and-shots)。

---

## 1. 文献与角色

| 角色 | 文献 / 文档 |
|------|-------------|
| VQE 测量 | McClean et al., NJP **18**, 023023 (2016) |
| 对易分组 | OpenFermion tensor-product / 贪心对易 |
| 本栈工程 | `docs/pauli_averaging_protocol_five_stage_engineering.md` |
| 选型 | [parity 契约](/guide/parity-repro-contract) |

协议层把「制备 → 分组测量 → 聚合期望」固化为可作业化、可导出的五阶段对象。

---

## 2. 理论

哈密顿量

$$
\hat{H}=\sum_k c_k P_k
$$

能量估计

$$
\hat{E}=\sum_k c_k\,\widehat{\langle P_k\rangle}
$$

两 Pauli 串对易当且仅当辛内积为 0：

$$
\langle(x,z),(x',z')\rangle = x\cdot z' + z\cdot x' \pmod{2}
$$

分组减少电路行数；有限 shots 时附带 `energy_stderr_model`（见 `protocol_counts`）。

---

## 3. 实现：五阶段

`PauliAveragingProtocol`（`protocols/protocol.py`）与 `ProtocolPhase`：

| 阶段 | 枚举 | 方法 / 模块 |
|------|------|-------------|
| Instantiate | `INSTANTIATE` | `instantiate()` |
| Build | `BUILD` | `build()` → `protocol_build.build_logical_circuits` |
| Compile | `COMPILE` | `compile()` → `compile_circuits` |
| Run | `RUN` | `run()` → `protocol_run.run_energy_estimation` |
| Evaluate | `EVALUATE` | `evaluate()` → `counts["expectation"]` |

Preview 键：`protocol_stages_preview_v1`（`instantiate` / `build` / `compile` / `run` / `evaluate`）。

**Shot 模式互斥**：精确 executor（默认）｜`run_sampled` 分组 MC｜`run_qiskit_shots`。

作业：`process_pauli_protocol_job`；安全序列化：`secure_dumps_protocol` / `secure_loads_protocol`。管线装配：`orchestration/protocol_finalize_protocol.py`。

### Computables

| API | 路径 |
|-----|------|
| `list_computables_for_config` | `protocols/computables/list_for_config.py` |
| `computables_export_dict` | 同上 |
| 运行时类 | `ExpectationValueComputable`、`OverlapSquaredComputable`、`QSEMatricesComputable`、`SCEOMMatrixComputable` |

典型名：`ground_state_energy`、`hamiltonian_expectation_pauli_protocol`、`excited_energies_vqd`、`qse_matrices_uccsd`、`sceom_energies` 等。

### product_contract

| 符号 | 作用 |
|------|------|
| `validate_pauli_protocol_for_config` | ansatz×协议运行守卫 |
| `validate_qse_protocol_for_config` | QSE 协议守卫 |
| `ansatz_protocol_matrix_v1` | 兼容矩阵 |
| `product_gap_categories` / `PRODUCT_CAPABILITY_MAP` | 能力缺口文档 |
| `PARITY_EXPORT_V3_STABLE_KEYS` | parity 导出稳定键 |

公开面：`protocols/product_contract.py`。

---

## 4. YAML

```yaml
quantum:
  pauli:
    use_protocol: true
    grouping: tensor_product   # 或 greedy_commuting
    run_sampled: false
    run_qiskit_shots: false
    record_histograms: false
    support_max_terms: null
```

| YAML（`quantum.pauli`） | 协议字段 |
|-------------------------|----------|
| `use_protocol` | 启用 finalize + computable |
| `grouping` | `measurement_grouping` |
| `run_sampled` / `run_qiskit_shots` | 互斥采样模式 |
| `record_histograms` | 直方图 |
| `support_max_terms` | Pauli 支撑截断 |

缓解 YAML（`mitigation.*`）经 `protocol_finalize_protocol` 注入协议（ZNE / PMSV / shadows flags）。

代表：`configs/example_h2_qcc_pauli_protocol.yaml`。

---

## 5. Python

```python
from qchem_stack.protocols.product_contract import product_gap_categories
from qchem_stack.protocols.computables.list_for_config import list_computables_for_config
from qchem_stack.sdk import export_parity_table, workflow_preview_payload
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2.yaml")
print(list_computables_for_config(cfg)[:5])
print(product_gap_categories()[:3] if callable(product_gap_categories) else type(product_gap_categories))
table = export_parity_table("configs/example_h2.yaml")
```

能量估计核心由编排调用：`run_energy_estimation`。

---

## 6. 验证

```bash
python3 -c "from qchem_stack.sdk import export_parity_table; t=export_parity_table('configs/example_h2.yaml'); print(type(t).__name__)"
```

期望：退出码 `0`；打印导出文档类型名。

```bash
python3 -c "from qchem_stack.config import load_experiment_config; from qchem_stack.protocols.computables.list_for_config import list_computables_for_config; print(len(list_computables_for_config(load_experiment_config('configs/example_h2.yaml'))))"
```

期望：打印正整数（computable 数量）。

---

## 7. 调优建议

- 项数多时优先 `tensor_product` 或 `greedy_commuting`，并设合理 `shots`。  
- `run_sampled` 与 `run_qiskit_shots` 勿同时开。  
- 改 ansatz 后跑 `validate_pauli_protocol_for_config` / workflow-preview，避免 product_contract 缺口。  
- 生产导出用 parity v3 稳定键，勿手写漂移字段名。

---

## 8. 相关

- **深读**：[Pauli 平均协议](./quantum/algorithms/pauli-protocol)  
- [backends](./backends) · [mitigation](./mitigation) · [orchestration](./orchestration) · [repro](./repro) · [jobs](./jobs)
