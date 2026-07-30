---
title: 算符池全表
description: operator_pool_registry 完整手册：每个 ID 的构造、数学、别名、能力与 ADAPT/IQEB 用法。
---

# 算符池全表

本页是自适应算法 **算符池** 的注册表手册：每个规范 ID 如何从费米子/比特生成元构造、与映射如何匹配、YAML/API 如何调用。

实现：`qchem_stack.quantum.operator_pool_registry`。消费者：[ADAPT](./adapt-vqe)、[IQEB](./iqeb)、[QCC](./qcc-paired)、部分研究插件。

---

## 1. 文献

| 主题 | 文献 |
|------|------|
| ADAPT 池生长 | Grimsley et al., [Nat. Commun. **10**, 3007 (2019)](https://doi.org/10.1038/s41467-019-10988-2) |
| Qubit excitation 池 | Yordanov et al., [Commun. Phys. **4**, 228 (2021)](https://doi.org/10.1038/s42005-021-00730-0) |
| UCC / UCCGD 生成元 | Romero et al.；Lee et al. k-UpCCGSD / 广义激发 |

---

## 2. 理论思想

自适应方法维护池 $\mathcal{A}=\{A_\mu\}$。梯度

$$
g_\mu=\bigl|\mathrm{Re}\,\langle\psi|[H,A_\mu]|\psi\rangle\bigr|
$$

决定本轮选谁。池内容决定：

- 可达流形（singles / doubles / 广义 / 比特激发）  
- 与 `fermion_to_qubit_map` 是否一致（JW 池 ↔ JW 哈密顿）  
- 池大小（梯度评次数）

无 `fermion_space` 时，多数化学池 **回退** 到玩具 `XX` 对（`toy_pair_xx`），仅烟雾可用。

---

## 3. 注册表 API

```python
from qchem_stack.quantum.operator_pool_registry import (
    list_registered_operator_pool_ids,
    operator_pool_registry_export_v1,
    resolve_operator_pool_id,
    build_registered_operator_pool,
    is_registered_operator_pool_id,
)

export = operator_pool_registry_export_v1()
assert export["schema"] == "operator_pool_registry_export_v1"
print(export["canonical_operator_pool_ids"])
print(export["pool_id_aliases"])
print(export["adapt_pool_yaml_field"], export["iqeb_pool_yaml_field"])
# pool = build_registered_operator_pool("fermionic_uccsd_singles", qh)
```

YAML：

- ADAPT / tetris：`quantum.adapt.pool_id`  
- IQEB：`quantum.iqeb.pool_id`  
- QCC 默认硬编码池：`iqeb_qubit_excitation`（类参数可改）

---

## 4. 规范 ID 详表

运行时以 `operator_pool_registry_export_v1()` 为准。下列与源码 `OPERATOR_POOL_REGISTRY` 对齐。

### 4.1 玩具

| ID | 构造 | 能力 |
|----|------|------|
| `toy_pair_xx` | 所有 $i \lt j$ 的 $X_i X_j$ | `smoke_only` |

### 4.2 Jordan–Wigner 化学池

费米子生成元来自 `chem.kernels.spin_ucc`，再 `jordan_wigner(·)`。

| ID | 费米子内容 | 能力位 |
|----|------------|--------|
| `fermionic_uccsd` | 闭壳层 UCCSD singles+doubles | `chemistry_aware` |
| `fermionic_uccsd_singles` | 仅 singles | + `singles_only` |
| `fermionic_uccsd_doubles_only` | 仅 doubles | + `doubles_only` |
| `fermionic_singles_doubles_staggered` | singles/doubles **交错拼接** | + `staggered_slices` |
| `fermionic_generalized_doubles` | UCCGD 风格 singles + 广义 doubles | + `generalized_doubles` |

### 4.3 Bravyi–Kitaev 化学池

同一套费米子生成元，映射用 `bravyi_kitaev(·)`。**必须**与 BK 哈密顿一起用。

| ID | 内容 | 能力 |
|----|------|------|
| `fermionic_uccsd_bravyi_kitaev` | 全 UCCSD | `bravyi_kitaev` |
| `fermionic_uccsd_singles_bravyi_kitaev` | BK singles | |
| `fermionic_uccsd_doubles_bravyi_kitaev_only` | BK doubles | |
| `fermionic_uccsd_singles_then_doubles_bk_concat` | BK singles **再** BK doubles 扁平拼接 | `sequenced_slices` |

### 4.4 IQEB 比特激发池

| ID | 构造 | 能力 |
|----|------|------|
| `iqeb_qubit_excitation` | $A_{ij}=\frac{i}{2}X_iY_j-\frac{i}{2}Y_iX_j$ | `iqeb_style` |

---

## 5. 别名

`resolve_operator_pool_id` / `OPERATOR_POOL_ID_ALIASES`：

| 别名 | 规范 ID |
|------|---------|
| `qubit_excitation` | `iqeb_qubit_excitation` |
| `uccsd_jw` | `fermionic_uccsd` |
| `uccsd_singles` | `fermionic_uccsd_singles` |
| `uccsd_doubles_only` | `fermionic_uccsd_doubles_only` |
| `uccsd_bravyi_kitaev` / `uccsd_bk` | `fermionic_uccsd_bravyi_kitaev` |
| `uccsd_bk_singles` | `fermionic_uccsd_singles_bravyi_kitaev` |
| `uccsd_bk_doubles_only` | `fermionic_uccsd_doubles_bravyi_kitaev_only` |
| `uccsd_bk_singles_then_doubles` | `fermionic_uccsd_singles_then_doubles_bk_concat` |

`list_registered_operator_pool_ids()` = 规范 ∪ 别名。

---

## 6. 选型建议

| 目标 | 推荐池 |
|------|--------|
| 最快烟雾 ADAPT | `fermionic_uccsd_singles` |
| 标准 JW 化学 | `fermionic_uccsd` |
| BK 分子 | `fermionic_uccsd_bravyi_kitaev`（+ BK 映射配置） |
| 广义相关 | `fermionic_generalized_doubles` |
| IQEB / QCC | `iqeb_qubit_excitation` |
| 调试交错生长 | `fermionic_singles_doubles_staggered` |

---

## 7. YAML 与配置样例

```yaml
quantum:
  algorithm: adapt
  adapt:
    pool_id: fermionic_uccsd_singles
    max_iter: 5
    grad_tol: 1.0e-2
```

| 代表配置 |
|----------|
| `configs/example_h2_adapt_singles_pool.yaml` |
| `configs/example_h2_adapt_bk_pool.yaml` |
| `configs/example_h2_adapt_generalized_doubles_pool.yaml` |
| `configs/example_h2_iqeb.yaml` |
| `configs/example_h2_iqeb_qubit_excitation_alias.yaml` |

---

## 8. 验证命令

```bash
python3 -c "
from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1
e=operator_pool_registry_export_v1()
assert e['schema']=='operator_pool_registry_export_v1'
print(len(e['canonical_operator_pool_ids']), len(e['pool_id_aliases']))
print(sorted(e['pools']['fermionic_uccsd']['capabilities']))
"
```

### 期望输出

- 规范 ID 数、别名数为正整数  
- `chemistry_aware` 出现在 `fermionic_uccsd` 能力中  

---

## 9. 边界与相关

- **不是** 厂商完整激发分类法；见 export 的 `export_alignment_note`。  
- SCBK / HCB 截断空间：勿假设 JW 池可直接套用。  
- [ADAPT](./adapt-vqe) · [IQEB](./iqeb) · [映射](/modules/chem/mappings) · [选型](/guide/operator-pools-adapt-iqeb)
