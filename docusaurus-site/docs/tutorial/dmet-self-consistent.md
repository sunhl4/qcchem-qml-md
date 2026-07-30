---
title: DMET 自洽烟测
description: 用 example_h4_dmet_self_consistent.yaml 验证自洽 DMET 演示配置。
---

# DMET 自洽烟测

本教程使用已存在的 **H₄ DMET 自洽演示** 配置：`configs/example_h4_dmet_self_consistent.yaml`。

## 目标

- 确认 `embedding.mode: dmet` 与自洽相关字段可解析
- 区分「演示 / audit」与论文级自洽生产结果
- 为后续对照 `example_h2_dimer_dmet_self_consistent.yaml` 做准备

## 前置

```bash
pip install -e ".[chem]"
```

## 配置要点

| 键 | 本示例 |
|----|--------|
| `embedding.mode` | `dmet` |
| 分子 | H₄ 链（STO-3G） |
| 自洽相关 | `dmet_max_cycles` / mixing / tol（见 YAML） |

边界说明见 [P1 化学与嵌入](../guide/chemistry-and-embedding) 与 [DMET 模块](/modules/chem/embedding-dmet)。

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h4_dmet_self_consistent.yaml')
print(c.experiment_id)
print(c.embedding.mode)
print(getattr(c.embedding.dmet, 'fragment_labels', None) or c.embedding.dmet)
"
```

## 期望输出

- 退出码 `0`
- `experiment_id` 含 `dmet_self_consistent`
- `embedding.mode` 为 `dmet`
- 打印 fragment 标签或 dmet 配置摘要

## 可选：对照 dimer 配置

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for p in [
  'configs/example_h4_dmet_self_consistent.yaml',
  'configs/example_h2_dimer_dmet_self_consistent.yaml',
]:
  c = load_experiment_config(p)
  print(c.experiment_id, c.embedding.mode)
"
```

期望：两行均为 `… dmet`。

## 下一步

- [Projection 嵌入深读](./projection-embedding-deep-dive)
- [DMET parity 快照](../reference/dmet-parity-snapshot)
- [embedding 模块](/modules/chem/embedding)
