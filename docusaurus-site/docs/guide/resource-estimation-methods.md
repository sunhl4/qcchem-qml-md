---
title: 资源估计与 Methods 导出
description: resource_estimation_preview 与 methods 统一导出在配置与管线中的用法。
---

# 资源估计与 Methods 导出

:::tip 模块手册
[integrations](/modules/integrations) · [repro / parity](/modules/repro) · [P3 执行](./execution-and-analysis) · [parity 契约](./parity-repro-contract)
:::

面向论文 Methods / 工程预估的 **代理量**，不是完整 fault-tolerant 编译器。实现：

- `integrations.resource_estimation_preview` — `resource_estimation_preview_v1`
- `integrations.methods_resource_unified` — 与算法注册表、MD/ML 冻结字段等并列导出

## 何时启用

- 需要在 **不跑满 shots** 时导出测量代理（shots、两比特门、深度、T 门代理等）。
- 配置中打开 `parity_integrations.resource_estimation_preview`（见 AVAS / QPE parity 示例）。

## 典型字段（预览）

| 字段 | 含义 |
|------|------|
| `ft_total_measurement_shots_proxy` | 总测量 shots 代理 |
| `ft_shots_per_circuit_effective_proxy` | 每线路有效 shots |
| `ft_t_gate_count_proxy` | T 门计数代理 |
| YAML 回显 | `quantum_algorithm_yaml`、`backend_provider_yaml`、`fermion_qubit_mapping_yaml`、ZNE 开关等 |

config-only 模式也可从 YAML 填充；带 `pipeline_row` 时从 `resource_summary` 深化。

## 代表配置

- `configs/example_h2_qpe_track_parity_integrations.yaml`
- `configs/example_h2_avas_casscf_workflow.yaml`

```bash
python scripts/export_parity_criteria_table.py configs/example_h2_qpe_track_parity_integrations.yaml
```

## 相关

- [可复现性与 parity 契约](./parity-repro-contract)
- [AVAS → CASSCF 工作流](./avas-casscf-workflow)
- [读 repro 关键键](../tutorial/read-repro-keys)
