---
title: SCEOM（自洽激发算符方法）
description: q-sc-EOM / SCEOM 完整手册：嵌套对易 M、生成元策略、自洽轮、YAML/API。
---

# SCEOM（q-sc-EOM / 自洽激发）

本页详述本栈 SCEOM：嵌套对易矩阵 $M$、生成元策略、参考子空间锚点、shots 与全部配置字段。

实现：`qchem_stack.quantum.algorithms.sceom`。调度：`orchestration.excited_stages`（`after_variational`）。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 量子 SCEOM / q-sc-EOM | *Chem. Sci.* [D2SC05371C](https://doi.org/10.1039/D2SC05371C)（源码亦标 arXiv:2206.10502） |
| 经典 EOM-CC | Stanton & Bartlett, [J. Chem. Phys. **98**, 7029 (1993)](https://doi.org/10.1063/1.464746) |

---

## 2. 要解决什么问题

在相关参考态 $|\psi\rangle$ 上，用激发算符 $\{S_i\}$ 构造有效激发矩阵并对角化，得到激发能谱。  
相对 [VQD](./vqd)（顺序惩罚）与 [QSE](./qse)（$H,S$ 广义本征），SCEOM 更贴近 **EOM 化学语言**（嵌套对易）。

---

## 3. 理论思想

主路径语义（论文式）：

$$
M_{ij}
= \langle\psi|[S_i^\dagger,[H,S_j]]|\psi\rangle
$$

对角化 $M$（玩具实现中常取重叠近似 $V\approx I$）得能级。  
可选 **自洽轮**：用最低本征矢系数混合 $S_i|\psi\rangle$ 更新参考，再重建 $M$。

---

## 4. 数学实现（本栈）

### 4.1 嵌套对易算符

```text
comm = [H, S_j] = H S_j − S_j H
nested = [S_i, comm]   # 源码对 Si 与 [H,Sj] 再对易（见 nested_sceom_q_sc_eom_operator）
M_ij = Re ⟨ψ| nested |ψ⟩
```

矩阵对称化：$(M+M^T)/2$，再 `eigh`。

### 4.2 入口一览

| 函数 | 用途 |
|------|------|
| `run_sceom_nested_commutator` | 主路径：$M$ + 对角化 |
| `run_sceom_nested_commutator_from_hea` | 参考 = HEA$(\boldsymbol{\theta})$ |
| `run_sceom_nested_commutator_from_uccsd` | 参考 = `prepare_state(θ)` |
| `run_sceom_reference_subspace` | **数值锚点**：取精确低本征矢作基再对角化（**不是**全文 shot-$M$） |
| `run_sceom_reference_subspace_shot_noise` | 对 $H_{\mathrm{sub}}$ 加高斯噪声的占位 |

### 4.3 生成元策略 `generator_strategy`

`resolve_sceom_s_generators`：

| 策略 | 内容 |
|------|------|
| `legacy` / `default` / `pauli_x_toy` | $I$ + 单比特 $X_q$（玩具） |
| `fermionic_singles_mapped` | 自旋轨道 singles → JW/BK（需 `fermion_space`；拒 SCBK） |
| `pauli_xy_extended` | $I$ 后交错 $X_q,Y_q$ |
| `symmetry_filtered_partial` | 扩展 Pauli 池后保留 **偶校验** Pauli 重量 |

### 4.4 Shots

- `shots_per_matrix_element=0`：精确 $\langle\mathrm{nested}\rangle$  
- `>0`：按矩阵元分组测量；`shots_backend`: `statevector` \| `qiskit`

### 4.5 自洽

`self_consistent_rounds` ∈ $\{0,\ldots,4\}$（配置层通常裁剪）：每轮用最低本征矢系数混合 $S_i|\psi\rangle$ 更新 $|\psi\rangle$。

---

## 5. 参数详表

```yaml
quantum:
  excited:
    sceom:
      after_variational: true
      subspace_dim: 4
      shots_per_matrix_element: 0
      generator_strategy: symmetry_filtered_partial
      self_consistent_rounds: 0
      shots_backend: statevector    # 或 qiskit
```

| 字段 | 含义 |
|------|------|
| `subspace_dim` | 目标生成元个数 $k$ |
| `shots_per_matrix_element` | 每 $M_{ij}$ 采样预算；0=精确 |
| `generator_strategy` | 上表四类 |
| `self_consistent_rounds` | 额外自洽轮数 |
| `shots_backend` | 采样后端 |

代表：`configs/example_h2_sceom_symmetry_filtered.yaml`。

### Python

```python
from qchem_stack.quantum.algorithms.sceom import (
    run_sceom_nested_commutator_from_hea,
    resolve_sceom_s_generators,
)

# gens, label = resolve_sceom_s_generators(
#     strategy="symmetry_filtered_partial", hamiltonian=qh, subspace_dim=4
# )
# res = run_sceom_nested_commutator_from_hea(
#     qh, angles, depth=1,
#     subspace_dim=4,
#     generator_strategy_yaml="symmetry_filtered_partial",
#     self_consistent_rounds=0,
# )
# print(res.energies, res.meta["construction"])
```

---

## 6. 函数调用与验证

```python
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids
from qchem_stack.sdk import run_pipeline_from_config

assert "sceom" in list_registered_excited_ids()
out = run_pipeline_from_config("configs/example_h2_sceom_symmetry_filtered.yaml")
sceom = out.get("sceom")
print(type(sceom).__name__, list(sceom)[:12] if isinstance(sceom, dict) else sceom)
```

### 验证命令

```bash
python3 -c "
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids
from qchem_stack.quantum.algorithms.sceom import nested_sceom_q_sc_eom_operator
assert 'sceom' in list_registered_excited_ids()
print('ok', nested_sceom_q_sc_eom_operator.__name__)
"
```

### 期望输出

- `ok nested_sceom_q_sc_eom_operator`  
- 管线含 `sceom`；可读 `meta.implementation_note` / `construction`  

---

## 7. 调参

| 现象 | 处理 |
|------|------|
| 能级无物理 | 先 `legacy` + `shots=0`；对照 `run_sceom_reference_subspace` |
| SCBK + fermionic singles | 换 JW/BK 或玩具策略 |
| Qiskit 路径慢/失败 | 检查 extras；先 `statevector` |
| 与 VQD/QSE 不一致 | 正常：算符与目标不同 |

---

## 8. 相关

- [VQD](./vqd) · [QSE](./qse) · [Pauli 协议](./pauli-protocol) · [选型](/guide/excited-states-vqd-qse-sceom)
