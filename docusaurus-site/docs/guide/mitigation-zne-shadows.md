---
title: 误差缓解（ZNE / classical shadows / PMSV）
description: mitigation 模块、YAML 键与协议挂载方式。
---

# 误差缓解（ZNE / classical shadows / PMSV）

:::tip 模块手册
[mitigation 模块](/modules/mitigation) · [P3 执行](./execution-and-analysis) · [backends](/modules/backends)
:::

## 决策块

| | |
|--|--|
| **何时用** | 需要对照噪声缩放外推（ZNE）、或契约级 shadows/PMSV 开关时 |
| **何时不用** | 第一次跑通基线能量；把 stub 路径当生产测量学 |
| **互斥 / 注意** | classical shadows / PEC literature stub 为可追踪 stub；ZNE 与无噪 statevector 对照时外推意义有限 |
| **链教程 + 深读** | [ZNE 教程](../tutorial/zne-qiskit-repro) · [mitigation 手册](/modules/mitigation) · [能力 SLA](/product/capability-sla) |

缓解实现位于 `qchem_stack.mitigation`，可在协议运行中挂载（`protocols.protocol_run_mitigation`）。配置块：`config.mitigation`。

## 能力矩阵

| 技术 | 模块 | 状态 | 代表配置 / 教程 |
|------|------|------|-----------------|
| **ZNE**（circuit fold + 外推） | `zne.py`、`zne_fold`、外推（linear / poly / Richardson / exponential） | 可执行 | `example_h2_zne_circuit_fold.yaml`、`example_h2_zne_qiskit_fold.yaml`；[教程](../tutorial/zne-qiskit-repro) |
| **Classical shadows** | `classical_shadows.py` | stub / 可追踪 runtime | `example_h2_classical_shadows_stub.yaml` |
| **PMSV** | 对称性过滤相关 | 配置开关 | 见 mitigation YAML / capability-surface |
| **SPAM 校准** | mitigation 包内 | 可选 | 维护者扩展路径 |

## ZNE 使用要点

1. 在 statevector 或可控噪声模型上先验证外推稳定性。
2. 噪声尺度列表（如 `1.0, 1.5, 2.0`）与阶数匹配；点数不足时多项式外推应跳过协方差奇异路径（实现已处理）。
3. UQC 后端另有 fold 辅助：`backends.uqc_zne_fold`。

## Classical shadows

管道中以 computable / DAG 节点形式出现；estimator schema 可能为 `…_median_of_means_v1`。用于对照与契约测试，勿当作生产级测量学产品。

## 相关

- [Pauli 协议与采样](./pauli-protocol-and-shots)
- [P3 执行与分析](./execution-and-analysis)
- [后端与 profile](./backends-and-profiles)
