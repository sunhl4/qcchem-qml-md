---
title: 费米子—量子比特映射选型
description: JW / BK / SCBK / JKMN / HCB 的 YAML 字面量、可执行性与适用边界（对照 chem.fermion_mapping_registry）。
---

# 费米子—量子比特映射选型

:::tip 模块手册
[chem · 映射](/modules/chem/mappings) · [P1 化学](./chemistry-and-embedding) · [hamiltonian](/modules/chem/hamiltonian)
:::

哈密顿量从自旋轨道费米子算符落到量子比特算符时，映射决定 **量子比特数、泡利重量与门深**。本页对应源码 `qchem_stack.chem.fermion_mapping_registry` 与构建路径 `chem.hamiltonian_mapping`。

## 可执行 YAML 字面量

| YAML 字面量 | 别名 | 说明 | 代表配置 |
|-------------|------|------|----------|
| `jordan_wigner` | JW | 默认；UCCSD 主路径要求 JW | `configs/example_h2.yaml` |
| `bravyi_kitaev` | BK | 降低泡利重量；部分池有 BK 变体 | `configs/example_h2_uccsd_bk.yaml` |
| `symmetry_conserving_bravyi_kitaev` | SCBK | 粒子数守恒子空间 | `configs/example_h2_scbk_hea.yaml` |
| `jkmn` | JKMN | 三元树映射（arXiv:1910.10746）；空间 CAS 构建 | `configs/example_h2_jkmn.yaml` |
| `hard_core_boson` | HCB | 配对电子硬核玻色映射；空间 CAS | `configs/example_h2_hcb.yaml` |

HTTP 能力面可导出同一表：`GET /v1/meta/capability-surface` → mapping 相关字段；或 Python：

```python
from qchem_stack.chem.fermion_mapping_registry import (
    list_documented_fermion_qubit_mappings,
    public_mapping_alias_surface_v1,
)

print(list_documented_fermion_qubit_mappings())
print(public_mapping_alias_surface_v1()["tutorial_alias_rows"])
```

## 配置位置

```yaml
active_space:
  fermion_qubit_mapping: jordan_wigner   # 或 bravyi_kitaev / …
```

解析助手：`qchem_stack.config.active_space_helpers.resolve_fermion_qubit_mapping`。

## 选型建议

1. **默认跑通**：保持 `jordan_wigner`，先验证能量与 repro。
2. **泡利项偏多 / 想对照 BK 文献**：切 `bravyi_kitaev`，并换对应 UCCSD/池配置（`example_h2_uccsd_bk.yaml`、`example_h2_adapt_bk_pool.yaml`）。
3. **需要粒子数对称性约化**：试 `symmetry_conserving_bravyi_kitaev`。
4. **研究映射本身**：`jkmn` / `hard_core_boson` — 确认活性空间与积分路径支持空间 CAS。

## 边界

- UCCSD 变分主线（`variational.ansatz: uccsd`）在实现上标为 **JW-only**；BK 路径使用专门配置与算法变体，勿随意混搭。
- 映射变更会改变 `hamiltonian_fingerprint`；parity / Methods 表应对齐同一映射。

## 相关

- [P1 化学与嵌入](./chemistry-and-embedding)
- [算法与 ansatz 菜单](./algorithm-and-ansatz-menu)
- [算符池 ADAPT / IQEB](./operator-pools-adapt-iqeb)
- [配置目录](../reference/configs-catalog)
