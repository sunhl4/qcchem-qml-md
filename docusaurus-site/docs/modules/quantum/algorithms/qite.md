---
title: QITE（研究插件）
description: 量子虚时演化研究插件：梯度下降步进、池、YAML 边界。
---

# QITE（研究插件）

固定算符池上的 **最速下降式虚时** 烟雾实现：按 $g_k=\mathrm{Re}\langle\psi|H O_k|\psi\rangle$ 更新角度，非完整 McLachlan 度量 QITE。

实现：`qchem_stack.quantum.algorithms.qite.QITEVQE`。ansatz：`qite`（`research_plugin`）。

---

## 1. 文献

Motlagh / Motta 等 QITE / 虚时变分工作（如 [npj Quantum Inf.](https://www.nature.com/npjqi/) 系列）。本栈为开放简化版。

---

## 2. 数学实现

每步：

1. 从 HF 参考施加当前池指数得 $|\psi(\boldsymbol{\theta})\rangle$  
2. $g_k=\mathrm{Re}\langle\psi|H O_k|\psi\rangle$  
3. $\theta_k \leftarrow \theta_k - \Delta t\, g_k$  
4. 若 $\|g\| \lt$ `QITE_GRAD_TOLERANCE`（$10^{-8}$）停止  

默认池：`fermionic_uccsd_singles`，`max_ops=2`，`n_steps=30`，`dt=0.05`。

**注意**：`quantum.vqe.maxiter` 在配置中可出现，但 **QITE 忽略 maxiter**，只用 `n_steps`。

---

## 3. 参数

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: qite
  vqe:
    maxiter: 80   # 被忽略；保留仅为配置树兼容
```

| 类 / `run` | 默认 | YAML？ |
|------------|------|--------|
| `pool_id` | `fermionic_uccsd_singles` | 否 |
| `max_ops` | `2` | 否 |
| `n_steps` | `30` | 否 |
| `dt` | `0.05` | 否 |

代表：`configs/example_h2_qite.yaml`。报告：`algorithm_qite_report_v1`（`nfev`←`n_steps`）。

---

## 4. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config
out = run_pipeline_from_config("configs/example_h2_qite.yaml")
print(out.get("energy_after_variational"))
```

```bash
python3 -c "from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids; assert 'qite' in list_registered_ansatz_ids(); print('ok')"
```

---

## 5. 边界与相关

- 需 `fermion_space`；每步从参考重施全池（简化）。  
- 真 McLachlan 轨迹演示见 [VQS](./vqs)。  
- [UCCSD](./uccsd) · [算符池](./operator-pools)
