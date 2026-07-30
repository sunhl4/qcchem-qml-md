---
title: 算符池（ADAPT / IQEB）
description: operator_pool_registry 中的池 ID、YAML 别名与代表配置。
---

# 算符池（ADAPT / IQEB）

:::tip 模块手册
选型摘要 → [ADAPT/IQEB 模块](/modules/quantum/adapt-iqeb) · 公式与池全表 → [ADAPT](/modules/quantum/algorithms/adapt-vqe) · [IQEB](/modules/quantum/algorithms/iqeb) · [算符池全表](/modules/quantum/algorithms/operator-pools)
:::

ADAPT-VQE 与 IQEB 从 **算符池** 中生长 ansatz。池定义在 `qchem_stack.quantum.operator_pool_registry`。

## 池 ID 与别名

| 注册 ID | 常用 YAML 别名 | 说明 |
|---------|----------------|------|
| `fermionic_uccsd` | `uccsd_jw` | 完整费米子 UCCSD（JW） |
| `fermionic_uccsd_singles` | `uccsd_singles` | 仅 singles |
| `fermionic_uccsd_doubles_only` | `uccsd_doubles_only` | 仅 doubles |
| `fermionic_uccsd_bravyi_kitaev` | `uccsd_bk` / `uccsd_bravyi_kitaev` | BK 编码 UCCSD |
| `fermionic_uccsd_singles_bravyi_kitaev` | `uccsd_bk_singles` | BK singles |
| `fermionic_uccsd_doubles_bravyi_kitaev_only` | `uccsd_bk_doubles_only` | BK doubles |
| `fermionic_uccsd_singles_then_doubles_bk_concat` | `uccsd_bk_singles_then_doubles` | BK singles→doubles 拼接 |
| `iqeb_qubit_excitation` | `qubit_excitation` | IQEB qubit-excitation 池 |
| `fermionic_singles_doubles_staggered` | — | 交错 singles/doubles |
| `fermionic_generalized_doubles` | — | 广义 doubles |
| `toy_pair_xx` | — | 测试用极小池 |

别名表：`OPERATOR_POOL_ID_ALIASES`。

## YAML 键

```yaml
quantum:
  algorithm: adapt          # 或 iqeb
  adapt:
    pool_id: fermionic_uccsd_singles   # 或别名 uccsd_singles
  # iqeb:
  #   pool_id: qubit_excitation
```

具体键名以当前 `ExperimentConfig` / 示例 YAML 为准；不确定时对照 `configs/example_h2_adapt_*.yaml`。

## 代表配置

| 场景 | 配置 |
|------|------|
| ADAPT singles | `configs/example_h2_adapt_singles_pool.yaml` |
| ADAPT doubles | `configs/example_h2_adapt_doubles_pool.yaml` |
| ADAPT BK | `configs/example_h2_adapt_bk_pool.yaml` |
| ADAPT staggered | `configs/example_h2_adapt_staggered_pool.yaml` |
| ADAPT generalized doubles | `configs/example_h2_adapt_generalized_doubles_pool.yaml` |
| IQEB 默认 | `configs/example_h2_iqeb.yaml` |
| IQEB fermionic doubles | `configs/example_h2_iqeb_fermionic_doubles_pool.yaml` |
| IQEB BK singles | `configs/example_h2_iqeb_bk_singles_pool.yaml` |

## 工程注意

- 池与 [费米子映射](./fermion-qubit-mappings) 必须一致：JW 池配 JW 哈密顿量，BK 池配 BK。
- `repro.run_summary` 会记录 `adapt_pool_id` / `iqeb_pool_id` 与梯度评估计数，便于 Methods 表。
- L3 基准 YAML 列表见 `integrations.l3_algorithm_benchmark`。

## 相关

- [算法与 ansatz 菜单](./algorithm-and-ansatz-menu)
- [P2 程序构建](./program-construction)
- [案例：H₂ 家族](../tutorial/case-study-h2-family)
