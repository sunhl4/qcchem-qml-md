---
title: ZNE × Qiskit Pauli 与 repro 键
description: zne_qiskit_unification_v1 在 parity_snapshot 中的含义与代表 YAML
---

对应广义 P1 **波次 G2**：把 **零噪声外推（ZNE）** 在开放栈里如何与 **Qiskit Pauli 协议路径**对表，写成 Methods 可引用的 **机读块**，而不是声称与商业 Qermit 数值同构。

## 机读块：`zne_qiskit_unification_v1`

当同时满足：

- `mitigation.zne_enabled: true`
- `quantum.run_qiskit_shots_pauli_protocol: true`（或管线等价开关）

管线在 `repro.parity_snapshot` 写入 **`zne_qiskit_unification_v1`**（固定 `schema`），串联：

- YAML 里的 `mitigation_zne_mode`
- 协议摘要 `protocol_counts` 中的 ZNE 相关字段（若存在）
- 诚实 **`epistemic_bound`** 文案（开放栈 fold 与 shot 能量 stub 的边界）

代表配置：**`configs/example_h2_zne_circuit_fold.yaml`**。

## 叙事文档

仓库 `docs/mitigation_PMSV_ZNE_Qermit_mapping.md`（本站若已镜像则见 [mitigation 映射](/concept/mitigation-mapping)）。

## 相关

- [公开 parity 矩阵](/product/roadmap) §1 Qermit 行
- [read repro 键](/tutorial/read-repro-keys)
