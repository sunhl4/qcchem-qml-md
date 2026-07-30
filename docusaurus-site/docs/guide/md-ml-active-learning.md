---
title: MD/ML 主动学习闭环
description: md_bridge 验证环、QMEF、力场后端与 UQC 联调选型（手册摘要）。
---

# MD/ML 主动学习闭环

:::tip 模块手册
[md_bridge 模块](/modules/md-bridge) · [P3 执行](./execution-and-analysis) · 教程 → [MD/ML](../tutorial/md-ml-active-learning)
:::

`qchem_stack.md_bridge` 把 **量子化学标注 → 力场训练 → JAX-MD 轨迹 → 再标注** 串成可复现环。逐步操作见 [教程：MD/ML](../tutorial/md-ml-active-learning)；本页给出选型与模块地图。

## 组件

| 组件 | 模块 | 作用 |
|------|------|------|
| 验证环 | `md_validation_loop`、`md_loop_rounds` | 多轮主动学习 |
| 配置 | `MdValidationLoopConfig` | `max_rounds`、`force_field_backend`、… |
| 数据集 | `QMEFDataset` / `QMFrame` | 能量–力帧 |
| 力场 | `qmlff_*`、`classical_h2` | 预设 / 角度 / QMP / Morse stub |
| HTTP | `api.routers.ml_md` | 服务化入口 |

## 力场后端

| `force_field_backend` | 说明 |
|-----------------------|------|
| `classical_h2` | 解析 Morse，适合 H₂ KPI 与无 qmlff 环境 |
| `qmlff_preset` / `qmlff_angle` / `qmlff_qmp_h2` / `qmlff_quantum` | 需本地 QML-FF 可编辑安装 |

H₄ 等非双原子体系不要用 `classical_h2` 拟合；用 mock / qmlff 路径。

## 代表配置

- `configs/example_h2_qmlff_md.yaml`、`example_h2_classical_md.yaml`
- `configs/example_h2_uqc_mock_qmlff_loop.yaml`、`example_h2_uqc_cloud_sim_md_ml.yaml`
- `configs/example_h4_classical_md_stub.yaml`（第二体系 stub）
- MD loop YAML（无 `molecule` 块）：见 [配置目录](../reference/configs-catalog) MdValidation 段

## 验收

```bash
python -m pytest tests/md_bridge/test_p4_md_ml_kpi.py -q --no-cov -m l1_md_ml
python examples/run_all_smoke.py   # 视环境跳过 qmlff
```

## 相关

- [P3 执行与分析](./execution-and-analysis)
- [UQC 后端](../cloud/uqc-backend)
- [示例馆](../examples/)
