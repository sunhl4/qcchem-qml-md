---
title: VQS（变分量子模拟轨迹）
description: 参数流 ODE / McLachlan TDVP 侧车完整手册：demos.vqs 全字段。
---

# VQS（Variational Quantum Simulation 轨迹）

**变分后侧车**，不是 `quantum.algorithm` 主求解器。在 HEA 角度上积分 $\dot{\boldsymbol{\theta}}$，跟踪能量轨迹。

实现：`qchem_stack.quantum.algorithms.vqs` + `vqs_pipeline_track.vqs_track_payload`。挂载：`attach_vqs_track_if_requested`。

---

## 1. 文献

Variational quantum simulation / McLachlan 原理与 TDVP 参数流（如 Yuan et al. 综述与 McLachlan 最小作用量形式）。本栈为开放 HEA 轨迹演示。

---

## 2. 理论思想

实/虚时演化在变分流形上投影为

$$
\dot{\boldsymbol{\theta}} = \arg\min \|(\partial_t + iH)|\psi(\boldsymbol{\theta})\rangle\|
$$

（McLachlan）。本栈两种 RHS：

| `rhs_mode` | 行为 |
|------------|------|
| `linear_damping` | $\dot\theta=\mp 0.1\,\theta$（符号依实/虚时） |
| `hea_mclachlan_tdvp` | 有限差分切空间 + 线性系统求 $\dot\theta$，Euler 步进 |

---

## 3. 数学实现

- 要求角度长度满足 HEA 约束：`len(theta) % (2 * n_qubits) == 0`  
- `mode: vqs` 时强制 `linear_damping`  
- `mclachlan_real_time` / `mclachlan_imag_time` 可选 TDVP RHS  
- 输出写入管线 demos / track 载荷（见 `vqs_track_payload`）

类：`AlgorithmVQS`、`AlgorithmMcLachlanRealTime`、`AlgorithmMcLachlanImagTime`。

---

## 4. 参数详表

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  demos:
    vqs:
      track_after_variational: true   # 或 pipeline_integration: true
      mode: mclachlan_real_time       # vqs | mclachlan_real_time | mclachlan_imag_time
      n_times: 6                      # ≥2
      dt: 0.05
      rhs_mode: linear_damping        # 或 hea_mclachlan_tdvp
      tangent_fd_epsilon: 5.0e-5
```

| 字段 | 默认 |
|------|------|
| `n_times` | `6` |
| `dt` | `0.05` |
| `rhs_mode` | `linear_damping` |
| `tangent_fd_epsilon` | `5e-5` |

代表：`configs/example_h2_vqs_track.yaml`。

---

## 5. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config
out = run_pipeline_from_config("configs/example_h2_vqs_track.yaml")
print([k for k in out if "vqs" in k.lower()][:10])
```

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c=load_experiment_config('configs/example_h2_vqs_track.yaml')
d=c.quantum.demos.vqs
print('ok', bool(getattr(d,'pipeline_integration',False) or getattr(d,'track_after_variational',False)))
"
```

---

## 6. 相关

- [VSQS ansatz](./vsqs-ansatz) · [VQE](./vqe-hea) · [QITE](./qite)
