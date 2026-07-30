---
title: 激发态侧车（VQD / QSE / SCEOM）
description: 变分之后的激发态插件、资源导出与代表 YAML。
---

# 激发态侧车（VQD / QSE / SCEOM）

:::tip 模块手册
[quantum · 激发态](/modules/quantum/excited-states) · 论文与参数 → [VQD](/modules/quantum/algorithms/vqd) · [QSE](/modules/quantum/algorithms/qse) · [SCEOM](/modules/quantum/algorithms/sceom)
:::

## 决策块

| | |
|--|--|
| **何时用** | 基态变分已稳定，需要亏损/子空间/对称 EOM 类激发态侧车 |
| **何时不用** | 尚未收敛基态；期望完整光谱产品级精度 |
| **互斥 / 注意** | 侧车挂在 Variational 之后；与纯基态 smoke 配置分开维护 |
| **链教程 + 深读** | [excited-states 手册](/modules/quantum/excited-states) · [VQD](/modules/quantum/algorithms/vqd) · [QSE](/modules/quantum/algorithms/qse) · [SCEOM](/modules/quantum/algorithms/sceom) |

基态变分完成后，管线可选运行 **激发态侧车**（`orchestration.excited_stages`），实现位于 `quantum.excited_plugins`。

## 方法概览

| 方法 | 作用 | 代表配置 |
|------|------|----------|
| **VQD** | 变分量子亏损：惩罚已收敛态重叠 | `example_h2_vqd_uccsd.yaml`、`example_h2_vqd_deflation_circuit.yaml` |
| **QSE** | 量子子空间展开 | `example_h2_uccsd_qse_pauli_qiskit.yaml`、`example_h4_adapt_qse_benchmark.yaml` |
| **SCEOM** | 对称性约束 EOM 类路径 | `example_h2_sceom_symmetry_filtered.yaml` |
| **Smoke** | 最小激发态开关 | `example_h2_excited_smoke.yaml` |

## 在管线中的位置

```
SCF → PreQuantum → Variational → [Excited stages] → Protocol / Finalize
```

激发态结果进入 `repro` / parity 导出的 excited 相关块；资源侧见 `protocols.excited_resource_export`。

## 选型建议

1. 先跑通基态（HEA 或 UCCSD）再开 VQD。
2. 需要子空间对角化语义时用 QSE；采样路径配合 Pauli/Qiskit。
3. SCEOM / 对称过滤用于研究级光谱，检查配置中的 symmetry 过滤开关。

## 边界

- 侧车不替代完整量子光谱学产品；以开放可复现路径为准。
- 部分路径依赖 Qiskit shots 或额外计算预算，CI 中用 smoke / `l1_excited` marker。

## 相关

- [算法与 ansatz 菜单](./algorithm-and-ansatz-menu)
- [Pauli 协议与采样](./pauli-protocol-and-shots)
- [资源估计与 Methods 导出](./resource-estimation-methods)
