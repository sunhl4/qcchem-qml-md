---
title: chem · 费米子—量子比特映射（深读）
description: JW/BK/SCBK/JKMN/HCB 完整手册：文献、数学、YAML、API、与 UCC/池兼容性。
---

# chem · 费米子—量子比特映射（深读）

本页是映射层完整手册：每种映射的文献与代数直觉、本栈如何解析配置、与 UCCSD / 算符池 / QCC 的兼容矩阵，以及可复制 API。

对应：`qchem_stack.chem.fermion_mapping_registry`、`chem.hamiltonian_mapping`、`config.active_space_helpers.resolve_fermion_qubit_mapping`。

选型短文：[费米子—量子比特映射](/guide/fermion-qubit-mappings)。

---

## 1. 文献

| 映射 | 文献 |
|------|------|
| **Jordan–Wigner** | P. Jordan & E. Wigner, *Über das Paulische Äquivalenzverbot*, Z. Phys. **47**, 631 (1928) |
| **Bravyi–Kitaev** | S. Bravyi & A. Kitaev, *Fermionic quantum computation*, [Ann. Phys. **298**, 210 (2002)](https://doi.org/10.1006/aphy.2002.6254) |
| **SCBK** | Seeley et al., [J. Chem. Phys. **137**, 224109 (2012)](https://doi.org/10.1063/1.4768229)；对称性守恒变体见后续工作 |
| **JKMN** | Jiang et al., [arXiv:1910.10746](https://arxiv.org/abs/1910.10746) |
| **HCB** | 硬核玻色子 / 配对电子映射；本栈用于空间 CAS 路径 |

---

## 2. 要解决什么问题

第二量子化 $\hat{H}_{\mathrm{f}}$ 活在费米子 Fock 空间；量子硬件操作 Pauli 代数。  
映射 $M$ 给出（子空间）同构：

$$
\hat{H}_{\mathrm{q}} = M(\hat{H}_{\mathrm{f}}) = \sum_k c_k P_k
$$

它决定量子比特数、Pauli 重量（测量与门深）、以及粒子数等对称性是否被编码进更小希尔伯特空间。

**指纹** `hamiltonian_fingerprint` 对 $M$ 与系数敏感——改映射必须重跑对照实验，不能直接比能量数值。

---

## 3. 数学要点

### 3.1 Jordan–Wigner

$$
a_j \mapsto \Biggl(\prod_{k\lt j} Z_k\Biggr)\frac{X_j+iY_j}{2},\qquad
a_j^\dagger \mapsto \Biggl(\prod_{k\lt j} Z_k\Biggr)\frac{X_j-iY_j}{2}
$$

- 优点：直观，与多数 UCC 教程一致；本栈 UCCSD / 多数 JW 池默认路径  
- 缺点：非局部 $Z$ 串使典型 Pauli 重量随轨道数增长  

JW 下 UCCSD 传播后可做 **固定电子数扇区投影**（`jw_number_indices`）。

### 3.2 Bravyi–Kitaev

用二叉树部分和存储占据奇偶，使更新/校验的平均非局域性常优于 JW（渐近 $\mathcal{O}(\log n)$ 量级典型重量）。  
本栈经 OpenFermion `bravyi_kitaev` 与匹配 **BK 算符池**。UCCSD 在 BK 上 **不做** JW 粒子投影。

### 3.3 SCBK（对称性守恒 BK）

利用粒子数等对称性 **截断** 量子比特空间（$n_{\mathrm{qubits}} \lt n_{\mathrm{so}}$）。  
后果：稠密 UCCSD / QCC / UpCCGSD / pUCCD 等要求 $n_{\mathrm{so}}=n_{\mathrm{qubits}}$ 的路径会 **拒绝**；HEA 等比特 ansatz 仍可跑。

### 3.4 JKMN / HCB

- **JKMN**：三元树最优映射族；本栈空间 CAS 构建路径之一  
- **HCB**：硬核玻色子配对电子；适合配对模型直觉；稠密 UCCSD 同样非方阵不适用  

---

## 4. 本栈文档化 ID

```python
from qchem_stack.chem.fermion_mapping_registry import (
    list_documented_fermion_qubit_mappings,
    mapping_status_rows_v1,
    public_mapping_alias_surface_v1,
)

print(list_documented_fermion_qubit_mappings())
for row in mapping_status_rows_v1():
    print(row)
```

典型字面量：

| YAML 字面量 | 角色 |
|-------------|------|
| `jordan_wigner` | 默认化学主路径 |
| `bravyi_kitaev` | 低重量对照；配 BK 池 |
| `symmetry_conserving_bravyi_kitaev` | 截断空间；HEA / 部分算法 |
| `jkmn` | 三元树路径 |
| `hard_core_boson` | 配对电子路径 |

---

## 5. 与算法 / 池的兼容性（实务）

| 组件 | JW | BK | SCBK | JKMN / HCB |
|------|----|----|------|------------|
| HEA-VQE | ✓ | ✓ | ✓（按比特数） | 视构建 |
| UCCSD / pUCCD / QCC | ✓ | ✓ | ✗ | 通常 ✗（非方阵） |
| ADAPT + `fermionic_uccsd*` | ✓ | 用 BK 池 | 慎用 | 慎用 |
| IQEB 默认比特池 | ✓ | ✓ | ✓ | ✓ |
| SCEOM `fermionic_singles_mapped` | ✓ | ✓ | ✗ | ✗ |

详细池 ID：[算符池全表](/modules/quantum/algorithms/operator-pools)。

---

## 6. 参数（YAML）

两种常见写法（以仓库配置为准；解析函数归一化）：

```yaml
# 写法 A：扁平字段（许多 example_*.yaml）
active_space:
  n_electrons: 2
  n_orbitals: 2
  fermion_qubit_mapping: jordan_wigner

# 写法 B：嵌套 mapping（部分 schema）
active_space:
  mapping:
    fermion_qubit: jordan_wigner
```

| 字面量 | 代表配置 |
|--------|----------|
| `jordan_wigner` | `configs/example_h2.yaml` |
| `bravyi_kitaev` | `configs/example_h2_uccsd_bk.yaml` |
| `symmetry_conserving_bravyi_kitaev` | `configs/example_h2_scbk_hea.yaml` |
| `jkmn` | `configs/example_h2_jkmn.yaml` |
| `hard_core_boson` | `configs/example_h2_hcb.yaml` |

解析：

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.config.active_space_helpers import resolve_fermion_qubit_mapping

cfg = load_experiment_config("configs/example_h2.yaml")
print(resolve_fermion_qubit_mapping(cfg.active_space))
```

哈密顿 meta 常写 `fermion_to_qubit_map`，供 UCCSD / SCEOM / QCC 读取。

---

## 7. 函数调用与验证

```python
from qchem_stack.chem.fermion_mapping_registry import (
    list_documented_fermion_qubit_mappings,
    public_mapping_alias_surface_v1,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.config.active_space_helpers import resolve_fermion_qubit_mapping

assert "jordan_wigner" in list_documented_fermion_qubit_mappings()
cfg = load_experiment_config("configs/example_h2.yaml")
print(resolve_fermion_qubit_mapping(cfg.active_space))
print(public_mapping_alias_surface_v1()["tutorial_alias_rows"][:3])
```

### 验证命令

```bash
python3 -c "
from qchem_stack.chem.fermion_mapping_registry import list_documented_fermion_qubit_mappings
assert 'jordan_wigner' in list_documented_fermion_qubit_mappings()
print('ok', len(list_documented_fermion_qubit_mappings()))
"
```

### 期望输出

- `ok` 与正整数映射数  

---

## 8. 调参与排错

| 现象 | 处理 |
|------|------|
| UCCSD 断言 $n_{\mathrm{so}}=n_{\mathrm{qubits}}$ | 勿用 SCBK/HCB；改 JW/BK |
| BK 与 JW 能量「差很多」 | 先确认是否同映射对照；指纹不同不可直接比 |
| ADAPT 梯度异常 | 池映射与哈密顿映射不一致 |
| 别名不识别 | 查 `public_mapping_alias_surface_v1()` |

---

## 9. 相关

- [哈密顿量构建](./hamiltonian) · [UCCSD](/modules/quantum/algorithms/uccsd) · [算符池](/modules/quantum/algorithms/operator-pools) · 仓库 `docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md`
