---
title: ONIOM 烟测
description: 用 example_oniom_toy.yaml 验证 ONIOM 玩具层配置可加载。
---

# ONIOM 烟测

仓库已提供 ONIOM 相关示例；本教程以 **`configs/example_oniom_toy.yaml`** 为主，并列出可对照文件。

## 目标

- 确认 ONIOM 玩具配置可被 `load_experiment_config` 解析
- 理解该路径多为 **嵌入 / 层叠元数据演示**，不是完整生产 QM/MM 能量主路径

## 已存在的 ONIOM YAML

| 文件 | 说明 |
|------|------|
| `configs/example_oniom_toy.yaml` | 玩具层叠（本教程主配置） |
| `configs/example_oniom_qm_mm_demo.yaml` | QM/MM 演示 |
| `configs/example_h2o_oniom_qmmm.yaml` | H₂O / ONIOM-QM/MM 相关示例 |

选型边界见 [P1 化学与嵌入](../guide/chemistry-and-embedding)。

## 配置要点

本仓库的 ONIOM 玩具示例通过 **`embedding.oniom_layers_v1`** 描述 QM/MM 层；`embedding.mode` 可能仍为 `dmet` / `none`（以 YAML 为准），不要假设存在独立的 `mode: oniom` 字面量。

| 键 | `example_oniom_toy.yaml` |
|----|--------------------------|
| `experiment_id` | `h4_oniom_toy_layers_001` |
| `embedding.oniom_layers_v1` | QM + MM 两层玩具 |
| `embedding.mode` | `dmet`（与共享哈密顿演示路径共用） |

## 前置

```bash
pip install -e ".[chem]"
```

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_oniom_toy.yaml')
print(c.experiment_id)
print(c.embedding.mode)
layers = c.embedding.oniom_layers_v1 or []
print('layers', len(layers))
"
```

## 期望输出

- 退出码 `0`
- `h4_oniom_toy_layers_001`
- `dmet`
- `layers 2`

## 可选：三份配置批量加载

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for p in [
  'configs/example_oniom_toy.yaml',
  'configs/example_oniom_qm_mm_demo.yaml',
  'configs/example_h2o_oniom_qmmm.yaml',
]:
  c = load_experiment_config(p)
  n = len(c.embedding.oniom_layers_v1 or [])
  print(c.experiment_id, c.embedding.mode, n)
"
```

期望：三行均可打印，且 `oniom_layers_v1` 长度大于等于 1（或按各文件实际层数）。

## 下一步

- [embedding 模块](/modules/chem/embedding)
- [DMET 自洽烟测](./dmet-self-consistent)
- [分解插件教程](./decomposition-plugin-minimal)
