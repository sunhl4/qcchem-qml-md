---
title: ADAPT-VQE
description: 自适应算符生长完整手册：梯度、池、tetris、YAML/API 与示例。
---

# ADAPT-VQE

本页详述本栈 `FermionicAdaptVQE`：如何从算符池按对易子梯度生长 ansatz，以及 YAML / Python 全部关键旋钮。

实现：`qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE`。池：[算符池全表](./operator-pools)。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 方法提出 | H. R. Grimsley et al., *An adaptive variational algorithm for exact molecular simulations on a quantum computer*, [Nat. Commun. **10**, 3007 (2019)](https://doi.org/10.1038/s41467-019-10988-2) |
| qubit-ADAPT / tetris 变体 | 后续 ADAPT 家族工作（减少测量、并行选算符等） |

---

## 2. 理论思想

固定 ansatz（HEA/UCCSD）要么表达不足，要么参数过多。  
**ADAPT-VQE** 维护算符池 $\mathcal{A}=\{A_\mu\}$，迭代：

1. 在当前态 $|\psi\rangle$ 上计算每个未选算符的能量梯度幅度（对易子期望）；  
2. 选出最大者（或 tetris 下多个互不重叠者）；  
3. 把 $e^{-i\theta A_{\mu}}$ 乘进 ansatz，与已有参数一起经典再优化；  
4. 直到 $\max|g_\mu|<\varepsilon$ 或达到最大算符数。

这样电路结构由数据驱动，常在较少参数下接近化学精度（理想模拟）。

---

## 3. 数学实现（本栈）

### 3.1 梯度

$$
g_\mu = \bigl|\mathrm{Re}\,\langle\psi|[H,A_\mu]|\psi\rangle\bigr|
$$

源码：`comm = h_op * op - op * h_op`，再 `expectation_qubit_operator`。

### 3.2 态构造

本栈在 **HEA 参考角度** 上叠加选中的池指数：

$$
|\psi\rangle
= \Biggl(\prod_{(j,\theta)\in\mathrm{layers}} e^{-i\theta A_j}\Biggr)
U_{\mathrm{HEA}}(\boldsymbol{\alpha})|0\rangle
$$

`hea_depth` 控制 $U_{\mathrm{HEA}}$ 深度；`hea_angles` 与层角度在每轮 COBYLA 中联合优化（`COBYLA_MAXITER=80`）。

### 3.3 停止与 tetris

- 标准：每轮只选 `grad_map` 最大下标。  
- `tetris_style=True`：在梯度够大的候选中，按比特支撑不重叠贪心多选，至多 `TETRIS_MAX_OPERATORS_PER_ROUND=4`。  
- 停止：`best_grad_mag < grad_tol` 或 `iter == max_ops`。

### 3.4 认识论边界

文档与风格约定标明：当前主路径为 **稠密 statevector** 梯度/能量（非硬件可扩展测量协议的完整 ADAPT）。

### 3.5 结果

`AdaptResult`：`energy`、`pool_indices`、`angles_per_layer`、`meta`（含 `adapt_steps`、`total_gradient_evals`、`hea_angles`、`layers`…）。

算法 ID：`adapt`；tetris 外层：`tetris_adapt`。

---

## 4. 参数详表

### 4.1 YAML

```yaml
quantum:
  algorithm: adapt          # 或 tetris_adapt
  adapt:
    max_iter: 5             # 映射到外环/max_ops 预算（见 resolvers）
    pool_id: fermionic_uccsd_singles
    grad_tol: 1.0e-2
  vqe:
    depth: 1                # 常作 hea_depth 来源
```

| 字段 | 含义 | 默认 |
|------|------|------|
| `adapt.max_iter` | 外环迭代/选算符上限相关 | `5` |
| `adapt.pool_id` | 池注册名或别名 | `fermionic_uccsd` |
| `adapt.grad_tol` | $\|g\|_{\max}$ 阈值 | `1e-2` |

类构造额外：`max_ops`、`hea_depth`、`tetris_style`、`pool=` 直接注入。

代表：`configs/example_h2_adapt_singles_pool.yaml`、`example_h2_adapt_bk_pool.yaml`、`example_h2_adapt_generalized_doubles_pool.yaml`。

### 4.2 Python

```python
from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE
from qchem_stack.quantum.operator_pool_registry import list_registered_operator_pool_ids

print(list_registered_operator_pool_ids()[:8])
# adapt = FermionicAdaptVQE(qh, pool_id="fermionic_uccsd_singles", max_ops=4, hea_depth=1)
# adapt.build()
# result = adapt.run(grad_tol=1e-2, seed=0)
```

---

## 5. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_adapt_singles_pool.yaml")
print(out.get("energy_after_variational"))
report = out.get("algorithm_report") or {}
print(report if not isinstance(report, dict) else {k: report.get(k) for k in list(report)[:8]})
```

### 验证命令

```bash
python -c "
from qchem_stack.quantum.operator_pool_registry import list_registered_operator_pool_ids
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
assert 'fermionic_uccsd' in list_registered_operator_pool_ids()
assert 'adapt' in list_registered_algorithm_ids()
print('ok', len(list_registered_operator_pool_ids()))
"
```

### 期望输出

- `ok` 与正整数池数量  
- 管线能量键存在  

---

## 6. 调参建议

| 目标 | 建议 |
|------|------|
| 先跑通 | `fermionic_uccsd_singles` + 小 `max_iter` |
| 更高相关 | 全 `fermionic_uccsd` 或 generalized doubles 池 |
| BK 分子 | 用 BK 池 + BK 映射配置族 |
| 加速选算符 | `tetris_adapt` / `tetris_style` |
| 梯度永不降 | 检查池与映射是否一致；放宽/收紧 `grad_tol` |

---

## 7. 相关

- [IQEB](./iqeb)（外环筛选 + 内层 VQE，池常为 qubit excitation）  
- [算符池全表](./operator-pools) · [UCCSD](./uccsd) · [VQE](./vqe-hea)
