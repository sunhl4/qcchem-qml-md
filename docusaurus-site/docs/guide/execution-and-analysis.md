---
title: P3 执行与分析
description: 后端、缓解、MD/ML、资源估计与结果解释的决策指南。
---

# P3 执行与分析

:::tip 模块手册
[backends](/modules/backends) · [mitigation](/modules/mitigation) · [md_bridge](/modules/md-bridge) · [protocols](/modules/protocols)
:::

P3 回答「在哪执行、如何采样、如何缓解、如何解释」：后端抽象、协议消费、缓解挂载、可选 MD/ML 闭环与资源预览。

## 决策总表

| 决策 | 选项 | 默认建议 | 何时不要 |
|------|------|----------|----------|
| 后端 | `statevector` / `qiskit` / `uqc` / 其他 | 开发与 CI 用 statevector | 未跑通化学就上云 |
| 采样 | 精确期望 / Pauli shots | 先精确期望，再 shots | 同时开多缓解 + 高 shots 首次调试 |
| 缓解 | ZNE / shadows stub / PMSV | 需要噪声对照再开 ZNE | 把 shadows stub 当生产误差棒 |
| MD/ML | 独立 loop YAML | 与最小 VQE 分开 | 塞进同一「超级 YAML」难审计 |
| 资源估计 | `resource_estimation_preview` | Methods / 论文表需要时 | 当作精确 FT 编译结果 |

## 推荐执行顺序

1. `statevector` 跑通化学 + 算法。
2. 打开 Pauli / Qiskit shots，对照能量与 `resource_summary`。
3. 需要时加 ZNE；shadows 仅作契约路径。
4. 云路径：`uqc` mock → cloud-sim（见 [UQC](../cloud/uqc-backend)）。
5. MD/ML：独立 loop YAML + 标注配置。

## 后端选型

| Provider | 用途 | 代表 YAML |
|----------|------|-----------|
| `statevector` | 参考精确期望 | `example_h2.yaml` |
| `qiskit` | Aer / shots 路径 | `example_h2_qiskit_shots.yaml` |
| `uqc` | 云 / mock 离子阱风格 | `example_h2_uqc_mock_md_ml.yaml` |

深读：[backends-and-profiles](./backends-and-profiles) · [backend-adapter-quickstart](./backend-adapter-quickstart)。

## 缓解选型

| 能力 | 何时用 | 何时不要 | 选型页 |
|------|--------|----------|--------|
| ZNE | 噪声缩放对照、Qiskit fold | 无噪声 statevector 基线对比 | [mitigation-zne-shadows](./mitigation-zne-shadows) |
| Classical shadows stub | 契约 / Methods 占位 | 当作已验证方差估计 | 同上 |
| PMSV | 稳定子保留实验 | 默认生产路径 | 模块 mitigation |

代表：`configs/example_h2_zne_qiskit_fold.yaml`、`example_h2_classical_shadows_stub.yaml`。

## MD / ML 与资源估计

| 主题 | 选型页 | 代表 YAML |
|------|--------|-----------|
| MD/ML 闭环 | [md-ml-active-learning](./md-ml-active-learning) | `example_h2_md_ml_trajectory_full_pipeline.yaml` |
| 资源 / Methods | [resource-estimation-methods](./resource-estimation-methods) | `example_h2_qpe_track_parity_integrations.yaml` |

## 本柱子页

| 主题 | 页面 |
|------|------|
| 后端与 profile | [backends-and-profiles](./backends-and-profiles) |
| Pauli 协议与采样 | [pauli-protocol-and-shots](./pauli-protocol-and-shots) |
| 误差缓解 | [mitigation-zne-shadows](./mitigation-zne-shadows) |
| MD/ML 闭环 | [md-ml-active-learning](./md-ml-active-learning) |
| 资源估计 / Methods | [resource-estimation-methods](./resource-estimation-methods) |
| UQC 详情 | [cloud/uqc-backend](../cloud/uqc-backend) |

## 何时不要用（边界）

- 不要用 UQC real 模式做「第一次能不能跑」测试（先 mock）。
- 不要在未固定 `hamiltonian_fingerprint` 时比较跨后端能量差。
- 不要把 `resource_estimation_preview` 的 proxy 字段写成实测 wall-time SLA。
- 不要假设 MD/ML loop 会自动写入与 VQE 相同的 `energy_after_variational` 语义。

## 源码锚点

| 关注点 | 模块 |
|--------|------|
| 后端工厂 | `backends.factory` |
| 缓解 | `mitigation.*` |
| MD/ML | `md_bridge.*` |
| 资源预览 | `integrations.resource_estimation_preview` |

## 验证命令

```bash
python3 -c "
from qchem_stack.backends.factory import registered_backend_provider_ids
print(sorted(registered_backend_provider_ids()))
"
```

期望：列表含 `statevector`（及已安装的可选 provider）。

配置烟测：

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for p in [
  'configs/example_h2.yaml',
  'configs/example_h2_qiskit_shots.yaml',
  'configs/example_h2_zne_qiskit_fold.yaml',
]:
  c = load_experiment_config(p)
  print(c.experiment_id, c.backend.provider, getattr(c.mitigation.zne, 'enabled', None))
"
```

期望：三行均可打印，无异常。

## 结果解释检查清单

1. `status` / 作业终态是否成功
2. `pre_quantum_input` 的 fingerprint 是否与基线一致
3. `energy_after_variational` vs 参考能量（HF / CASCI）差是否合理
4. 若开了协议：`resource_summary` / shot 相关键是否出现
5. 若开了缓解：ZNE 报告键是否写入 repro / summary
6. 若开了 MD/ML：导出帧与 loop round 是否可追溯

## 相关教程

- [切换后端对比](../tutorial/switch-backend-compare)
- [ZNE Qiskit repro](../tutorial/zne-qiskit-repro)
- [MD/ML 主动学习](../tutorial/md-ml-active-learning)

## 下一步

进入 [P4 作业与可复现](./jobs-and-reproducibility)。
