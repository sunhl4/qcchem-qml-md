---
title: 后端与 profile
description: backend.provider 注册表、内置执行器与 profile 切换建议。
---

# 后端与 profile

:::tip 模块手册
[backends 模块](/modules/backends) · [P3 执行](./execution-and-analysis) · [UQC](../cloud/uqc-backend)
:::

## 决策块

| | |
|--|--|
| **何时用** | 切换 `backend.provider`、对照多执行器、挂云/硬件适配 |
| **何时不用** | 尚未固定化学 YAML / ansatz；先用 `statevector` 验证能量与 `repro` |
| **互斥 / 注意** | `uqc` 需 `[uqc]` / `all-cloud`；与核心 `dev` 安装面分离（见 [install profiles](../reference/install-profiles)） |
| **链教程 + 深读** | [切换后端](../tutorial/switch-backend-compare) · [backends 手册](/modules/backends) · [UQC](../cloud/uqc-backend) |

执行器由 `qchem_stack.backends.factory` 按 `backend.provider` 解析。内置与入口点可并存。

## 内置 provider

| Provider | 说明 | 依赖 |
|----------|------|------|
| `statevector` / `numpy` / `local` | 参考精确期望 | 核心 |
| `qiskit` | Aer statevector 或 shots | `[quantum]` |
| `cirq` | Cirq Simulator | `cirq` |
| `qulacs` | Qulacs | `qulacs` |
| `braket` | Amazon Braket 适配 | 可选 |
| `ionstack` / `ion_stack` | 离子阱风格注入点 | 自定义 meta |
| `uqc` | UQC 云 / mock | `qchem-stack-uqc` + `[uqc]` |

```python
from qchem_stack.backends.factory import registered_backend_provider_ids
print(sorted(registered_backend_provider_ids()))
```

## 选型

1. **开发与 CI**：`statevector`。
2. **采样路径验证**：`qiskit` + shots YAML。
3. **云 / 硬件对接**：`uqc`（详见 [UQC 后端](../cloud/uqc-backend)）或 IonStack 注入。
4. **多后端对照**：同一化学配置只改 `backend`，比较 `hamiltonian_fingerprint` 不变与能量偏差。

Profile 助手：`backends.profiles`（优先 `apply_backend_profile_immutable`）。经典化学驱动（PySCF / Psi4 / 自定义）见 [后端适配快速开始](./backend-adapter-quickstart) 与 [Psi4](./psi4-backend)。

## 代表配置

- `configs/example_h2.yaml` — statevector
- `configs/example_h2_qiskit_shots.yaml`
- `configs/uqc_h2.yaml`、`example_h2_uqc_mock_md_ml.yaml`

## 相关

- [P3 执行与分析](./execution-and-analysis)
- [Pauli 协议与采样](./pauli-protocol-and-shots)
- [切换后端对比（教程）](../tutorial/switch-backend-compare)
