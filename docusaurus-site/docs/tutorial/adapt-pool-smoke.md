---
title: ADAPT singles 池烟测
description: 用 example_h2_adapt_singles_pool.yaml 验证 ADAPT 算符池配置可加载并跑通最小路径。
---

# ADAPT singles 池烟测

本教程验证 **ADAPT-VQE + singles 算符池** 的代表配置可加载，并给出可选的 pipeline 烟测入口。

## 目标

- 确认 `configs/example_h2_adapt_singles_pool.yaml` 可被 `load_experiment_config` 解析
- 理解 `quantum.algorithm: adapt` 与池字段的位置
- （可选）跑通短 pipeline 并检查 summary 键

## 前置

```bash
pip install -e ".[chem]"
```

配置：`configs/example_h2_adapt_singles_pool.yaml`。

## 配置要点

| 键 | 期望 |
|----|------|
| `quantum.algorithm` | `adapt` |
| 池相关 | singles 池（见 YAML 内 `adapt` / pool 字段） |
| `backend.provider` | `statevector`（烟测） |

选型背景：[算符池](../guide/operator-pools-adapt-iqeb) · [ADAPT 深读](/modules/quantum/algorithms/adapt-vqe)。

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2_adapt_singles_pool.yaml')
print(c.experiment_id)
print(c.quantum.algorithm)
"
```

## 期望输出

- 退出码 `0`
- 第一行含 `h2_adapt_singles_pool`（或配置内 `experiment_id`）
- 第二行含 `adapt`

## 可选：短 pipeline

```bash
python3 scripts/smoke_pipeline.py --config configs/example_h2_adapt_singles_pool.yaml
```

期望：退出码 `0`；若脚本支持该配置，结果含 `pre_quantum_input` / 能量相关摘要。

## 下一步

- [P2 程序构建](../guide/program-construction)
- [IQEB / 池全表](/modules/quantum/algorithms/operator-pools)
- [H2 家族案例](./case-study-h2-family)
