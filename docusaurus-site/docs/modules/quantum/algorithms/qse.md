---
title: QSE（量子子空间展开）
description: McClean QSE 完整手册：H/S 广义本征、基组策略、shot 模式与 API。
---

# QSE（Quantum Subspace Expansion）

实现：`qchem_stack.quantum.algorithms.excited_qse.QSE` 及 `qse_solve_helpers` / `qse_basis_strategies`。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 方法 | J. R. McClean et al., [Phys. Rev. A **95**, 042308 (2017)](https://doi.org/10.1103/PhysRevA.95.042308)（源码亦标 arXiv:1603.05681） |
| 实验 | J. I. Colless et al., [Phys. Rev. X **8**, 011021 (2018)](https://doi.org/10.1103/PhysRevX.8.011021) |

---

## 2. 理论思想

在参考态 $|\psi\rangle$（常为 VQE 基态）附近，用扩展算符生成微基 $\{|\phi_\alpha\rangle\}$，在子空间内解广义本征问题，同时得到基态修正与激发能，并可能缓解部分噪声。

与 VQD：**一次对角化多个本征对**，而非顺序惩罚。

---

## 3. 数学实现

### 3.1 广义本征问题

$$
H_{\alpha\beta}=\langle\phi_\alpha|H|\phi_\beta\rangle,\quad
S_{\alpha\beta}=\langle\phi_\alpha|\phi_\beta\rangle,\quad
\mathbf{H}\mathbf{c}=E\,\mathbf{S}\mathbf{c}
$$

激发能常报告为 $E_i-E_0$。实现中会检查 $S$ 条件数并去掉线性相关基矢。

### 3.2 基组策略（本栈）

| 策略 | 类 | 思想 |
|------|-----|------|
| VQE+HEA | `VqeHeaBasisStrategy` | 在 HEA 态上做 Pauli-X bump 等生成微基 |
| UCCSD | `UccsdBasisStrategy` | 化学单/双激发池扩展 |

`run_from_vqe_hea_basis(angles, depth, max_basis=...)`、`run_from_uccsd_basis(...)` 等入口。

### 3.3 矩阵元模式 `shot_mode`

| 值 | 含义 |
|----|------|
| `exact` | 稠密精确矩阵元 |
| `gaussian_h` | 对矩阵元加高斯噪声（shots 建模） |
| `pauli_transitions` | 泡利跃迁测量风格 |
| `pauli_transitions_qiskit` | Qiskit 路径 |

另有 `run_dense_reference()`：全空间对角化作小体系参考（不可扩展）。

---

## 4. 参数详表

```yaml
quantum:
  excited:
    qse:
      after_variational: true
      subspace_dim: 4
      max_basis: null
      shot_mode: exact
      expansion_pool: fermionic_singles   # 或 fermionic_singles_doubles
      shots_per_matrix_element: 4096
      shots_per_ij_term: 512
```

代表：`configs/example_h2_uccsd_qse_pauli_qiskit.yaml`。

### Python

```python
from qchem_stack.quantum.algorithms.excited_qse import QSE
# qse = QSE(qh, subspace_dim=4)
# ref = qse.run_dense_reference()
# exc = qse.run_from_vqe_hea_basis(angles, depth=1)
```

---

## 5. 函数调用与验证

```python
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids
from qchem_stack.sdk import run_pipeline_from_config

assert "qse" in list_registered_excited_ids()
# out = run_pipeline_from_config("configs/example_h2_uccsd_qse_pauli_qiskit.yaml")
# print(out.get("qse"))
```

### 验证命令

```bash
python -c "from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids; assert 'qse' in list_registered_excited_ids(); from qchem_stack.quantum.algorithms.excited_qse import QSE; print('ok', QSE.__name__)"
```

### 期望输出

- `ok QSE`  

---

## 6. 调参

| 现象 | 处理 |
|------|------|
| $S$ 病态 / 能量乱 | 减小 `subspace_dim` / `max_basis`；用 `exact` 对照 |
| 与 VQD 不一致 | 正常：方法不同；对齐同一参考态与活性空间 |
| Qiskit 路径失败 | 检查 extras 与 `shot_mode` |

---

## 7. 相关

- [VQD](./vqd) · [SCEOM](./sceom) · [Pauli 协议](./pauli-protocol)
