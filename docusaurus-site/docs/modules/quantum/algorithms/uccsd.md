---
title: UCCSD-VQE
description: 幺正耦合簇 SD 完整手册：簇算符、JW/BK、传播、YAML/API 与示例。
---

# UCCSD-VQE

本页说明本栈 **闭壳层自旋轨道 UCCSD** 变分实现：从费米子簇算符到稠密矩阵指数传播、映射约束、配置与调用。

实现：`qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE`。映射边界：仓库 `docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md`。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| UCC 量子化学变分 | J. Romero et al., *Strategies for quantum computing molecular energies using the unitary coupled cluster ansatz*, [Quantum Sci. Technol. **4**, 014008 (2019)](https://doi.org/10.1088/2058-9565/aad3e4)（arXiv:1701.02691） |
| 耦合簇理论 | R. J. Bartlett & M. Musiał, *Coupled-cluster theory in quantum chemistry*, [Rev. Mod. Phys. **79**, 291 (2007)](https://doi.org/10.1103/RevModPhys.79.291) |
| Trotter 分解实践 | 多种 NISQ UCC 编译工作；本栈 `UCCSDTrotterVQE` + `variational.uccsd_trotter_steps` |

---

## 2. 理论思想

经典 CC 写 $|\Psi\rangle=e^{\hat{T}}|\mathrm{HF}\rangle$，但 $\hat{T}$ 非厄米，难直接做酉电路。  
**幺正耦合簇（UCC）** 改为反厄米生成元：

$$
|\psi(\boldsymbol{\theta})\rangle
= e^{\hat{\tau}(\boldsymbol{\theta})}|\mathrm{HF}\rangle,\qquad
\hat{\tau}=\hat{T}-\hat{T}^\dagger
$$

**UCCSD** 取 $\hat{T}=\hat{T}_1+\hat{T}_2$（单、双激发）。参数与化学激发一一对应，通常比 HEA 更易得到正确粒子数扇区与化学精度，但门深/参数随活性空间增大更快。

本栈默认用 **乘积指数**（非单一大指数）在 HF 参考上逐个传播生成元，便于实现与调试：

$$
|\psi\rangle
= \Biggl(\prod_k e^{\theta_k(\hat{T}_k-\hat{T}_k^\dagger)}\Biggr)|\mathrm{HF}\rangle
$$

---

## 3. 数学实现（本栈）

### 3.1 生成元

`chem.kernels.spin_ucc.build_spin_uccsd_fermion_generators(n_so, n_e)` 构造自旋轨道费米子激发，再经

`antihermitian_cluster_matrices(..., mapping=..., n_qubits=...)`

映成反厄米稀疏/稠密矩阵 $\{A_k\}$，满足传播 $e^{\theta A_k}$。

### 3.2 参考态与映射

`reference_state_dense(mapping, n_spin_orbitals, n_electrons)`：

| 映射 | 行为 |
|------|------|
| `jordan_wigner` | JW HF 参考；传播后可做 **固定电子数扇区投影**（`jw_number_indices`） |
| `bravyi_kitaev` | BK 参考 + BK 匹配簇；**不做** JW 粒子投影 |
| `jkmn` | 方阵编码路径之一（需 $n_{\mathrm{so}}=n_{\mathrm{qubits}}$） |
| `symmetry_conserving_bravyi_kitaev` / `hard_core_boson` | **拒绝**（非方阵/截断空间不匹配） |

硬约束：`n_spin_orbitals == n_qubits`，且 `hamiltonian.fermion_space` 必须存在。

### 3.3 态传播（`_state_from_angles`）

```text
psi ← |HF⟩
for (θ_k, A_k) in zip(angles, antiherm_mats):
    psi ← expm(θ_k * A_k) @ psi
    psi ← psi / ‖psi‖
psi ← post_propagation(psi)   # JW: 扇区投影；其它: 仅归一化
```

`prepare_state(angles)` 供 VQD 等在同一流形上制备态。

### 3.4 变分优化

`_run_variational_optimize`：SciPy 最小化 $E(\boldsymbol{\theta})=\langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle$，支持 `bounds`、`initial_parameters`、`record_energy_trace`。

### 3.5 Trotter 变体

`variational.uccsd_trotter_steps: K` → `UCCSDTrotterVQE`：把簇演化拆成 $K$ 层一阶 Trotter，便于电路导出（见教程 [UCCSD Trotter](/tutorial/uccsd-trotter-export)）。

`quantum.uccsd.decomposition_mode`：`pauli` | `unitary`（CircuitIR 制备风格）。

---

## 4. 参数详表

### 4.1 YAML

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: uccsd
    uccsd_trotter_steps: null     # 或正整数
  uccsd:
    decomposition_mode: pauli     # pauli | unitary
  vqe:
    maxiter: 80
    optimizer_method: COBYLA
active_space:
  # 嵌套 schema 中映射常在 active_space.mapping.fermion_qubit
  mapping:
    fermion_qubit: jordan_wigner
```

代表配置：

| 文件 | 用途 |
|------|------|
| `configs/example_h2_uccsd.yaml` | 标准 JW UCCSD |
| `configs/example_h2_uccsd_trotter.yaml` | Trotter 层 |
| `configs/example_h2_uccsd_bk.yaml` | BK 路径 |
| `configs/example_h2_uccsd_pauli_protocol.yaml` | + Pauli 协议 |

### 4.2 能力查询

```python
from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_mapping_support_matrix_v1
from qchem_stack.quantum.ansatz_registry import ansatz_registry_export

print(uccsd_mapping_support_matrix_v1())
print(ansatz_registry_export()["uccsd"]["capabilities"])
# 通常含 jordan_wigner_only 等提示；以运行时为准
```

---

## 5. 函数调用

### 5.1 管线

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_uccsd.yaml")
print(out["energy_after_variational"])
print(out["pre_quantum_input"]["fermion_to_qubit_map"])
```

### 5.2 验证命令

```bash
python -c "
from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_mapping_support_matrix_v1
from qchem_stack.sdk import run_pipeline_from_config
m=uccsd_mapping_support_matrix_v1()
print('matrix_ok', bool(m))
o=run_pipeline_from_config('configs/example_h2_uccsd.yaml')
print('E', o.get('energy_after_variational'))
"
```

### 5.3 期望输出

- `matrix_ok True`  
- `E` 为负浮点能量  
- 退出码 `0`  

---

## 6. 调参与排错

| 错误 / 现象 | 原因与处理 |
|-------------|------------|
| `requires fermion_space` | 哈密顿未带活性空间元数据；检查 pre-quantum |
| `n_spin_orbitals == n_qubits` 断言失败 | 映射/编码非方阵；勿对 SCBK 硬跑 UCCSD |
| SCBK / HCB ValueError | 换 JW 或 BK 专用配置 |
| 能量差、BK 与 JW 不可比 | 指纹与希尔伯特编码不同；parity 须同映射对照 |
| 要电路层导出 | 设 `uccsd_trotter_steps` 并跟 Trotter 教程 |

---

## 7. 边界与相关

- 注册表常标 `jordan_wigner_only` 为**主路径**能力提示；BK 走专门配置。  
- 广义 doubles：[UCCGD](./uccgd)。  
- 激发态可复用 `prepare_state`：[VQD](./vqd)。  
- [映射深读](/modules/chem/mappings) · [VQE/HEA](./vqe-hea)
