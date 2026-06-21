---
title: UQC 云平台后端
description: UQC ion-trap 云模拟器与硬件 backend 集成摘要。
---

# UQC 云平台后端

**权威文档**（中文完整版）：仓库 [`docs/UQC云平台集成技术报告.md`](https://github.com/yaozheng/qchem-stack/blob/main/docs/UQC云平台集成技术报告.md)。

## 快速配置

```yaml
backend:
  provider: uqc
  uqc_mode: mock   # mock | real
  shots_per_circuit: 200
```

Mock 模式无需 API token，使用 statevector 回退。真机/云模拟需 `UQC_API_TOKEN` 或 `backend.meta.uqc_token`。

## 示例 YAML

- `configs/uqc_h2.yaml` — 基础 H₂
- `configs/example_h2_uqc_mock_md_ml.yaml` — mock + QMEF 导出
- `configs/example_h2_uqc_cloud_sim_md_ml.yaml` — 云模拟 + MD/ML loop

## 代码模块

- `qchem_stack.backends.uqc_executor` — HEA 期望执行
- `qchem_stack.backends.uqc_transpiler` — rzz/rx/ry 原生门集
- `qchem_stack.backends.uqc_pauli_measurement` — 比特串 → 能量

## ZNE 能量后处理（可选）

云模拟/硬件 shot 能量可在 executor 层启用 open-stack ZNE 外推（与 `mitigation.zne` 语义对齐的 stub 曲线）：

```yaml
backend:
  provider: uqc
  meta:
    uqc_mitigation:
      zne:
        enabled: true
        scales: [1.0, 1.5, 2.0]
        mode: energy_stub   # circuit_scale_fold triggers per-scale UQC submissions (HEA depth fold)
```

实现：`qchem_stack.backends.uqc_zne_fold.run_uqc_zne_circuit_fold`（真提交多 scale）；`energy_stub` 走 `uqc_mitigation.apply_uqc_zne_mitigation`。trace 在 `UQCCloudHeaExecutor._last_mitigation_trace`，`protocol_counts` 在 `_last_protocol_counts`。

## 测试

```bash
pytest tests/quantum/test_uqc_backend_units.py tests/quantum/test_uqc_mock_md_ml_integration.py -q
```
