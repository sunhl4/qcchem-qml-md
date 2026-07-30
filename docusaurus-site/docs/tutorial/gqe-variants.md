---
title: GQE 变体配置加载
description: 对四个 GQE 代表 YAML 分别 load_experiment_config，确认顶层 gqe 块可解析。
---

# GQE 变体配置加载

本教程**不**要求跑满训练；只验证四个 GQE YAML 均可被配置层加载，且顶层存在 `gqe` 块。

## 四个代表 YAML

| 文件 | 角色（摘要） |
|------|----------------|
| `configs/example_h2_gqe_plan_b.yaml` | Plan B / Nakaji 短路径主烟测 |
| `configs/example_h2_gqe_condition.yaml` | condition 变体 |
| `configs/example_h2_gqe_gpt.yaml` | GPT 相关变体 |
| `configs/example_h2_gqe_prefill.yaml` | prefill 变体 |

权威手册：[GQE](../guide/gqe-generative-eigensolver) · [算法深读](/modules/quantum/algorithms/gqe)。完整训练见 [GQE Nakaji H₂](./gqe-nakaji-h2)。

## 前置

```bash
pip install -e ".[chem]"
# 实际训练另需: pip install -e ".[gqe]"
```

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
paths = [
  'configs/example_h2_gqe_plan_b.yaml',
  'configs/example_h2_gqe_condition.yaml',
  'configs/example_h2_gqe_gpt.yaml',
  'configs/example_h2_gqe_prefill.yaml',
]
for p in paths:
  c = load_experiment_config(p)
  g = getattr(c, 'gqe', None)
  print(p, c.experiment_id, type(g).__name__, getattr(g, 'enabled', None))
"
```

## 期望输出

- 退出码 `0`
- 四行均打印：路径、`experiment_id`、`GqeSpec`（或等价类型名）、以及 `enabled` 布尔值
- 无 `AttributeError` / 校验异常

## 常见误区

- 把 GQE 写成 `quantum.algorithm: gqe`（无效；必须用顶层 `gqe:`）
- 未装 `.[gqe]` 却期望本页验证命令完成训练（本页只验证 load）

## 下一步

- [GQE Nakaji 教程](./gqe-nakaji-h2)
- [integrations 模块](/modules/integrations)
- [P2 程序构建](../guide/program-construction)
