---
title: IQEB
description: 迭代量子激发筛选完整手册：外环梯度、有效哈密顿更新、YAML/API 与示例。
---

# IQEB（Iterative Qubit Excitation Based）

本页是 **IQEB 风格** 自适应外环的完整手册：文献与思想、本栈与论文差异、数学步骤、全部参数与可复制调用。

实现：`qchem_stack.quantum.algorithms.iqeb.IQEBVQE`。池：[算符池全表](./operator-pools)。对照：[ADAPT-VQE](./adapt-vqe)。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| Qubit excitation / IQEB 路线 | Y. S. Yordanov et al., *Qubit-excitation-based adaptive variational quantum eigensolver*, [Communications Physics **4**, 228 (2021)](https://doi.org/10.1038/s42005-021-00730-0) |
| 相关 qubit-ADAPT | 多种「比特激发池 + 梯度筛选」变体；本栈为开放实现，**不**宣称与闭源/Tangelo 比特级一致 |

---

## 2. 要解决什么问题

完整费米子 ADAPT 池大、梯度贵；固定 UCCSD 又可能过深。  
**IQEB 风格** 用更贴近硬件的 **量子比特激发** 生成元，并在外环只筛选少量候选，内环用浅层 VQE 再优化能量。

与本栈 **ADAPT** 的关键差异：

| | ADAPT（`FermionicAdaptVQE`） | IQEB（`IQEBVQE`） |
|--|------------------------------|-------------------|
| 生长对象 | 在 HEA 上乘 $e^{-i\theta A}$ **层** | 把选中池算符 **加进有效哈密顿**，再跑 HEA-VQE |
| 每轮选几个 | 1 个（或 tetris 多选） | 梯度排序后取 Top-`n_grads`，但当前实现每轮只 **追加最大者** 到 $H$ |
| 默认池 | `fermionic_uccsd*` | `iqeb_qubit_excitation` |

---

## 3. 理论思想

1. **池**：成对量子比特的反厄米激发类比（见下节数学）。  
2. **外环**：在当前有效算符 $H^{(r)}$ 上跑内层 VQE → 态 $|\psi_r\rangle$ → 对未选池元算对易子梯度。  
3. **更新**：把梯度最大的池算符按固定尺度加到 $H$，进入下一轮。  
4. **停止**：能量变化小于 `energy_tolerance`，或用尽 `max_rounds`。

目标：在可控轮数内逐步提高相关描述，同时限制单轮电路膨胀（内层仍是 HEA）。

---

## 4. 数学实现（本栈）

### 4.1 默认池元（`iqeb_qubit_excitation`）

对每对比特对 $i \lt j$：

$$
A_{ij}
= \tfrac{i}{2}\,X_i Y_j
- \tfrac{i}{2}\,Y_i X_j
$$

（源码：`0.5j * XX…` 形式的 `QubitOperator`。）这是 **单粒子比特激发** 的反厄米类比，不要求费米子空间元数据。

### 4.2 外环第 $r$ 轮

1. 构造 `QubitHamiltonian(operator=h^{(r)}, …)`。  
2. `VQE(qh, depth=depth).run(maxiter=120, seed=seed+r)` → 能量 $E_r$、角度 $\boldsymbol{\alpha}_r$。  
3. $|\psi_r\rangle=\mathrm{HEA}(\boldsymbol{\alpha}_r)$。  
4. 对未选下标 $j$：

$$
g_j=\bigl|\mathrm{Re}\,\langle\psi_r|[H^{(r)},A_j]|\psi_r\rangle\bigr|
$$

5. 按 $g$ 降序；记录 Top-`n_grads` 到 `iqeb_rounds` 元数据。  
6. 若 $|E_r-E_{r-1}|&lt;\varepsilon$，停止。  
7. 否则取最大梯度下标 $j^\*$，

$$
H^{(r+1)} \leftarrow H^{(r)} + c\,A_{j^\*},\qquad
c=`IQEB_POOL_COEFF_SCALE`
$$

（尺度常量见 `quantum.algorithms.tolerances`。）

### 4.3 结果

`IQEBResult`：`energy`、`selected_pauli_strings`（标签如 `pool_k_roundr`）、内层 `vqe`、`meta`（含 `selected_pool_indices`、`iqeb_rounds`、`pool_id`）。  
报告 schema：`algorithm_iqeb_report_v1`。

---

## 5. 管线位置

`quantum.algorithm: iqeb` → 算法注册表解析为 `IQEBVQE`。  
YAML 块 `quantum.iqeb.*` 映射到构造参数；`quantum.vqe.depth` 常作内层 HEA 深度。

---

## 6. 参数详表

### 6.1 YAML

```yaml
quantum:
  algorithm: iqeb
  iqeb:
    pool_id: iqeb_qubit_excitation   # 或别名 qubit_excitation
    n_grads: 3
    energy_tolerance: 1.0e-8
    max_rounds: 2
  vqe:
    depth: 1
```

| 字段 | 含义 | 默认 |
|------|------|------|
| `iqeb.pool_id` | 池 ID / 别名 | `iqeb_qubit_excitation` |
| `iqeb.n_grads` | 每轮梯度排序保留/报告的 Top-$k$ | `3` |
| `iqeb.energy_tolerance` | $\|E_r-E_{r-1}\|$ | `IQEB_ENERGY_TOLERANCE` |
| `iqeb.max_rounds` | 外环上限（≥1） | `2` |
| `vqe.depth` | 内层 HEA 深度 | `1` |

代表：`configs/example_h2_iqeb.yaml`、`example_h2_iqeb_qubit_excitation_alias.yaml`。

### 6.2 Python

```python
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE

# iqeb = IQEBVQE(
#     qh,
#     max_rounds=2,
#     n_grads=3,
#     energy_tolerance=1e-8,
#     pool_id="iqeb_qubit_excitation",
# )
# result = iqeb.run(depth=1, seed=0)
# print(result.energy, result.meta["selected_pool_indices"])
```

| 参数 | 含义 |
|------|------|
| `max_rounds` | 外环轮数 |
| `n_grads` | Top-$k$ 报告宽度 |
| `energy_tolerance` | 能量收敛阈值 |
| `pool_id` | 池名 |
| `executor` | 可选期望值执行器 |
| `run(depth, seed)` | 内层深度与种子 |

---

## 7. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids

assert "iqeb" in list_registered_algorithm_ids()
out = run_pipeline_from_config("configs/example_h2_iqeb.yaml")
print(out.get("energy_after_variational"))
```

### 验证命令

```bash
python3 -c "
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
from qchem_stack.quantum.operator_pool_registry import is_registered_operator_pool_id
assert 'iqeb' in list_registered_algorithm_ids()
assert is_registered_operator_pool_id('qubit_excitation')
print('ok')
"
```

### 期望输出

- `ok`  
- 管线能量为负浮点（H₂ 烟雾）  

---

## 8. 调参与排错

| 现象 | 处理 |
|------|------|
| 能量几乎不变 | 增大 `max_rounds`；换更大化学池（若映射允许） |
| 与 ADAPT 能量差很大 | 正常：更新对象不同（$H$ vs ansatz 层） |
| 未知 pool | 查 [算符池全表](./operator-pools) 别名 |
| 要费米子化学生长 | 优先 [ADAPT](./adapt-vqe) + `fermionic_uccsd*` |

---

## 9. 相关

- [ADAPT-VQE](./adapt-vqe) · [算符池全表](./operator-pools) · [选型](/guide/operator-pools-adapt-iqeb) · [QCC](./qcc-paired)（同用 qubit-excitation 池作固定 ansatz）
