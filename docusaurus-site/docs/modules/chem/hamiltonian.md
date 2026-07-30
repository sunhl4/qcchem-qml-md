---
title: chem · 哈密顿量构建
description: 从活性空间积分到 QubitHamiltonian、PreQuantumInput 与指纹的完整手册。
---

# chem · 哈密顿量构建

本页是 **使用者手册级** 说明：从第二量子化电子结构到泡利算符、本栈装配与可复现指纹。

相关：[映射](./mappings) · [Solver](./solvers) · [双线路](./dual-ingress) · [嵌入总览](./embedding)。

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| 第二量子化 / 分子哈密顿量 | Szabo & Ostlund, *Modern Quantum Chemistry*; Helgaker et al., *Molecular Electronic-Structure Theory* |
| 费米子–量子比特映射 | Jordan–Wigner; Bravyi–Kitaev; Seeley et al.; Tangelo / OpenFermion 实现对照 |
| 变分期望 | Peruzzo et al., Nat. Commun. **5**, 4213 (2014) |

经典平均场之后，相关问题落在活性空间电子哈密顿量上。量子算法消费的是映射后的泡利分解，而不是原始 AO/MO 积分张量。本栈在变分**之前**固定主路径 `QubitHamiltonian`，并用指纹保证跨驱动 / 跨机器的算符一致性。

---

## 2. 理论思想

电子哈密顿量（化学家记号下的空间轨道形式，再升到自旋轨道）：

$$
\hat{H} = E_{\mathrm{nuc}} + \sum_{pq} h_{pq}\, a_p^\dagger a_q + \frac{1}{2}\sum_{pqrs} g_{pqrs}\, a_p^\dagger a_q^\dagger a_s a_r
$$

经映射 $M$：

$$
\hat{H}_{\mathrm{qubit}} = M(\hat{H}) = \sum_k c_k\, P_k,\qquad P_k \in \{I,X,Y,Z\}^{\otimes n}
$$

变分能量：

$$
E(\boldsymbol{\theta}) = \langle \psi(\boldsymbol{\theta}) | \hat{H}_{\mathrm{qubit}} | \psi(\boldsymbol{\theta}) \rangle
= \sum_k c_k\, \langle P_k \rangle
$$

指纹对 $\{P_k\}$ 规范串与系数敏感：改映射、CAS 尺寸或积分路径都会改指纹；parity 对照必须对齐同一指纹。

---

## 3. 本栈数学与对象

### 3.1 `QubitHamiltonian`

定义于 `chem/hamiltonian_build.py`（facade：`chem/hamiltonian.py`）：

| 字段 | 含义 |
|------|------|
| `operator` | OpenFermion `QubitOperator` |
| `n_qubits` | 量子比特数 |
| `fermion_space` | 可选 `FermionSpace` |
| `meta` | 映射、积分源、指纹等 |

`sparse_matrix()` → `get_sparse_operator(operator, n_qubits=...)`。

### 3.2 装配链

```text
CanonicalActiveSpaceIntegralPack
  → InteractionOperator 或 空间受限费米子路径
  → fermion→qubit 映射
  → assemble_qubit_hamiltonian(...)
  → QubitHamiltonian (+ meta)
```

主入口：

- `molecular_hamiltonian_from_canonical_active_space_pack(...)`
- `assemble_qubit_hamiltonian(...)`（`hamiltonian_build_assembly.py`）

**JW 捷径**：`prefer_restricted_spatial_fermion_for_jordan_wigner=True` 仅当映射为 `jordan_wigner`。  
**稀疏截断**：`jordan_wigner_coeff_atol` 只作用于 JW 的 InteractionOperator 路径，并与 BK/SCBK 等互斥。  
**BK / SCBK / jkmn / HCB**：走空间 MO 费米子构建，避免稠密自旋轨道 ERI。

### 3.3 指纹

`hamiltonian_fingerprint_from_qubit_operator(qop)`（`hamiltonian_meta.py`）：

1. 各项 Pauli 标签经 `canonical_pauli_string_from_term` 排序（恒等项记为 `"I"`）。  
2. 系数格式 `:.16g`。  
3. SHA-256 十六进制的**前 32 字符**作为指纹；可标记截断。

### 3.4 `PreQuantumInput`

`pre_quantum_input.py`，schema `pre_quantum_input_v1`：

| 字段 | 含义 |
|------|------|
| `classical_reference` | 平均场参考 |
| `qubit_hamiltonian` | 上表对象 |
| `canonical_active_space_integral_pack` | 在线 CAS 路径有；precomputed 常为 `None` |
| `meta` | `source`、指纹、映射等 |

构建：`build_pre_quantum_input(cfg, reference)` / `build_pre_quantum_input_with_context`（`pre_quantum_build.py`）。  
汇总：`PreQuantumInput.as_summary_dict()` → `schema`、`source`、`n_qubits`、`hamiltonian_fingerprint`、`fermion_to_qubit_map` 等。

`meta` 常见键：`fermion_to_qubit_map`、`qubit_build`、`jw_build`、`integral_source`、`n_active_orbitals`、`n_active_electrons`、`hamiltonian_fingerprint`、`scf_energy_au`。

---

## 4. YAML 参数表

```yaml
active_space:
  strategy: cas                    # cas | manual | avas | avas_stub
  mapping:
    fermion_qubit: jordan_wigner   # jordan_wigner | bravyi_kitaev |
                                   # symmetry_conserving_bravyi_kitaev | jkmn | hard_core_boson
  cas:
    n_orbitals: 2                  # 解析 CAS 时必需
    n_electrons: 2
  jw:
    prefer_restricted_spatial: false
    coeff_atol: null               # 仅 JW InteractionOperator 路径
```

| 字段路径 | 默认 | 作用 |
|----------|------|------|
| `active_space.strategy` | `cas` | 活性空间解析策略 |
| `active_space.mapping.fermion_qubit` | `jordan_wigner` | 费米子–比特映射 |
| `active_space.cas.n_orbitals` / `n_electrons` | — | CAS 尺寸 |
| `active_space.jw.prefer_restricted_spatial` | `false` | JW 空间捷径 |
| `active_space.jw.coeff_atol` | `null` | JW 系数截断 |
| `embedding.mode` | `none` | 是否改走 Schmidt / projection / plugin |
| `scf.driver` | `pyscf` | `precomputed` 时改离线 bundle |

允许组合矩阵：仓库 `docs/pre_quantum_yaml_matrix.md`。

---

## 5. Python 调用

管线（推荐）：

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml")
pq = out["pre_quantum_input"]
print(pq["hamiltonian_fingerprint"])
print(pq.get("fermion_to_qubit_map"))
```

直接构建（调试）：

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.bridges import classical_mean_field_via_solver_bridge
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input

cfg = load_experiment_config("configs/example_h2.yaml")
ref = classical_mean_field_via_solver_bridge(cfg)
pq = build_pre_quantum_input(cfg, ref)
qh = pq.qubit_hamiltonian
print(qh.n_qubits, qh.meta.get("hamiltonian_fingerprint"))
```

Facade 重导出：`from qchem_stack.chem.hamiltonian import (...);`。

---

## 6. 验证命令

```bash
pytest tests/chem/test_hamiltonian_fingerprint.py \
  tests/chem/test_pre_quantum_input_contract.py \
  tests/chem/test_canonical_integral_pack.py -q

python -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print(o['pre_quantum_input']['hamiltonian_fingerprint'][:24])"
```

期望：退出码 `0`；打印非空指纹前缀。

---

## 7. 调参建议

| 目标 | 建议 |
|------|------|
| 与文献 JW 对齐 | 默认 JW；关掉不必要的 `prefer_restricted_spatial` 捷径做对照 |
| 缩小算符 | 试 BK / SCBK；或设合理 `coeff_atol`（仅 JW） |
| 复现对照 | 固定 `n_orbitals`/`n_electrons`、映射与积分源；比对指纹前 24–32 字符 |
| 嵌入分支 | Schmidt 路径会忽略 YAML CAS 尺寸作为主 `qh` 来源（见 [Schmidt](./embedding-schmidt)） |

---

## 8. 相关

- [映射](./mappings) · [Solver](./solvers) · [双线路](./dual-ingress) · [嵌入](./embedding)  
- 仓库：`docs/说明_chem模块技术参考手册.md`  
- 选型：[费米子映射](/guide/fermion-qubit-mappings) · [双线路输入](/guide/dual-classical-ingress)
