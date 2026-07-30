---
title: mitigation 模块
description: ZNE、PMSV、SPAM、classical shadows 与 qermit_runtime TOY 警告。
---

# mitigation 模块

`qchem_stack.mitigation` 实现误差缓解算法、报告装配与（可选）协议挂载。选型：[误差缓解](/guide/mitigation-zne-shadows)。

---

## 1. 文献与角色

| 方法 | 文献 |
|------|------|
| **ZNE** | Temme, Bravyi, Gambetta, PRL **119**, 180509 (2017) |
| ZNE 实验 | Kandala et al., Nature **567**, 491 (2019) |
| **Classical shadows** | Huang, Kueng, Preskill, Nat. Phys. **16**, 1050 (2020) |
| **PMSV** | 对称性验证 / post-selection（McArdle、Bonet-Monroig 等） |
| **SPAM** | 读出/态制备校准 |
| 本栈对照 | 仓库 `docs/mitigation_PMSV_ZNE_Qermit_mapping.md` |

缓解不纠错到逻辑比特；用额外电路与经典后处理估计更接近零噪声的期望。

---

## 2. 理论

- **ZNE**：在噪声尺度 $\{\lambda_i\}$ 上测 $E(\lambda_i)$，外推到 $\lambda\to 0$。  
- **Classical shadows**：随机 Pauli 测量得经典快照，再估计多个可观测量。  
- **PMSV**：用稳定子本征条件过滤不合规 bitstring（后选择）。  
- **SPAM**：校准矩阵修正读出混淆：$\mathbf{p}_{\mathrm{true}}\approx A^{-1}\mathbf{p}_{\mathrm{obs}}$。

线性外推示意：

$$
E(s) = a + b(s-1)
$$

截距语义以 `zne_extrapolation` 源码为准。

---

## 3. 实现

| 功能 | 模块 | 要点 |
|------|------|------|
| ZNE | `zne.py`、`zne_extrapolation.py`、`zne_fold.py` | `zne_scale_energy`；`fold_unitary_circuit` / `fold_gates_local` |
| PMSV | `pmsv.py` | `PMSVConfig`、`filter_shots_pmsv`；挂载于 `protocol_run_mitigation` |
| SPAM | `spam.py` | `SPAMCalibration`、`apply_spam`、`default_two_qubit_spam_matrix` |
| Classical shadows | `classical_shadows.py` | `classical_shadows_hamiltonian_expectation` — **TOY/STUB** |
| Qermit analog | `qermit_analog.py` | 静态 DAG 报告 — **STUB** |
| Qermit runtime | `qermit_runtime.py` | **TOY/STUB**；`execute_mitigation_dag_runtime` |

**`qermit_runtime` 警告**：可执行 DAG 为演示/桩实现，**不可**当作生产 Qermit 运行时。节点顺序（标志开启时）：

`SPAM_readout_calibration_stub` → `classical_shadows_expectation_stub` → `PMSV_symmetry_filter` → `ZNE_extrapolation_stub`。

Schema：`QERMIT_RUNTIME_V1`。调用侧：`orchestration/protocol_finalize_sidecars.py`。

协议级 flags（非独立 YAML 顶层）：`PauliAveragingProtocol.classical_shadows_enabled` 等，来自 `cfg.mitigation.stubs`。

---

## 4. YAML

```yaml
mitigation:
  execution_class: unspecified   # sync_graph | async_batch | shot_postselect
  zne:
    enabled: true
    mode: circuit_scale_fold     # 或 scalar_stub
    scales: [1.0, 3.0, 5.0]
  pmsv:
    enabled: false
    stabilizers: []
    retention_rate: 1.0
    report_extension: false
  stubs:
    spam_calibration: false
    pec_literature: false
    classical_shadows: false
    classical_shadows_budget_pairs: 256
```

| 字段 | 含义 |
|------|------|
| `zne.enabled` / `mode` / `scales` | ZNE；`mode` ∈ `{scalar_stub, circuit_scale_fold}`；启用时 `scales` 非空 |
| `pmsv.enabled` / `stabilizers` / `retention_rate` | 对称性后选；启用时 `stabilizers` 非空 |
| `stubs.spam_calibration` | SPAM 校准节点 |
| `stubs.classical_shadows` | shadows stub |
| `stubs.classical_shadows_budget_pairs` | 预算对数量 |
| `stubs.pec_literature` | PEC 文献对照桩 |

代表：`configs/example_h2_zne_circuit_fold.yaml`。教程：[ZNE Qiskit](/tutorial/zne-qiskit-repro)。

---

## 5. Python

```python
from qchem_stack.mitigation.zne_extrapolation import (
    linear_extrapolation,
    select_extrapolation_model,
)
from qchem_stack.config.mitigation_helpers import zne_enabled
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2.yaml")
print("zne_enabled", zne_enabled(cfg.mitigation))
# energies 在前、scales 在后
e0, unc = linear_extrapolation([-1.0, -0.9, -0.8], [1.0, 2.0, 3.0])
print(e0, unc)
```

协议挂载：`protocols.protocol_run_mitigation`。

---

## 6. 验证

```bash
python3 -c "from qchem_stack.mitigation.zne_extrapolation import linear_extrapolation; e0,u=linear_extrapolation([-1.0,-0.9,-0.8],[1.0,2.0,3.0]); print(round(e0,6), u)"
```

期望：退出码 `0`；截距约 `-1.0`。

```bash
python3 -c "from qchem_stack.mitigation import qermit_runtime as qr; print('TOY' in (qr.__doc__ or '') or 'STUB' in (qr.__doc__ or '') or hasattr(qr, 'execute_mitigation_dag_runtime')); print('qermit_runtime_ok')"
```

期望：打印 `qermit_runtime_ok`（确认模块可导入；运行时仍为 TOY/STUB）。

---

## 7. 调优建议

- 设备路径用 `circuit_scale_fold` + 合理 `scales`（如 `[1,3,5]`）；仿真对照可用 `scalar_stub`。  
- PMSV：`retention_rate` 过低会吃光 shots 预算。  
- `classical_shadows` / `qermit_runtime` 仅作对照与报告图，勿写入生产 SLA。  
- 与 Qiskit Pauli 合一键见 `zne_qiskit_unification_v1`。

---

## 8. 相关

- [protocols](./protocols) · [backends](./backends) · [Pauli 深读](./quantum/algorithms/pauli-protocol)  
- [orchestration](./orchestration) · [reading-paths P4](./reading-paths)
