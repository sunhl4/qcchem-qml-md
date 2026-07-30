---
title: Pauli 协议与采样
description: PauliAveragingProtocol 阶段、shot 模式、CircuitIR 与后端期望路径。
---

# Pauli 协议与采样

:::tip 模块手册
[Pauli 协议深读](/modules/quantum/algorithms/pauli-protocol) · [protocols 模块](/modules/protocols)
:::

当配置启用 Pauli 协议后，管线在变分之后进入 **构建 → 编译 → 发射 → 消费 → 评估** 阶段。实现位于 `qchem_stack.protocols`（`protocol.py`、`protocol_run.py`、`protocol_run_shot_modes.py`）。

## 何时需要协议路径

| 路径 | 适用 | 配置线索 |
|------|------|----------|
| 精确期望（executor） | 状态向量 / 小体系验证 | `backend.provider: statevector`，协议可关 |
| Pauli 分组 + shots | Qiskit Aer / 采样后端 | `example_h2_qiskit_shots.yaml`、`example_h2_uccsd_pauli_protocol.yaml` |
| 作业队列 | 异步 drain / worker | `job_db` + `qchem-jobs-worker` |

## 阶段语义（概念）

1. **Build**：按 ansatz 准备与泡利分组生成可执行 IR（含 CircuitIR）。
2. **Compile**：可选编译束（如 TKET pass bundle）。
3. **Launch**：写入作业存储或内存执行。
4. **Process**：拉取计数 / 期望。
5. **Evaluate**：组装能量与 meta，写入 pipeline 结果。

作业序列化使用 HMAC 签名 blob（`protocols.secure_serialization`）；遗留 unsigned pickle 会 DeprecationWarning。

## Shot 模式

`protocol_run_shot_modes` 区分精确路径与直方图路径。Qiskit shots 细节见 [Qiskit shot counts](../reference/qiskit-shot-counts)；CircuitIR / TKET 见 [CircuitIR & jobs](../reference/circuitir-tket-jobs)。

## 代表配置

- `configs/example_h2_uccsd_pauli_protocol.yaml`
- `configs/example_h2_qiskit_shots.yaml`
- `configs/example_h2_sampled.yaml`
- `configs/example_h2_uccsd_qse_pauli_qiskit.yaml`（QSE + Pauli）

## 与缓解的关系

ZNE / shadows 可挂在协议运行路径上（`protocol_run_mitigation`）。选型见 [误差缓解](./mitigation-zne-shadows)。

## 相关

- [P3 执行与分析](./execution-and-analysis)
- [后端与 profile](./backends-and-profiles)
- [教程：UCCSD Trotter 导出](../tutorial/uccsd-trotter-export)
