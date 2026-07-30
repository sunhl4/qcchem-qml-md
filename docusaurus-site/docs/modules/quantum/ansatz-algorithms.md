---
title: quantum · 算法与 ansatz（摘要）
description: 速查入口；完整文献/数学/参数一律指向算法深读。
---

# quantum · 算法与 ansatz（摘要）

本页是**速查枢纽**，不复制深读正文。完整「文献 / 思想 / 数学 / YAML / 调用 / 验证」见算法分册。

:::info 请读深读页
→ **[算法深读索引](./algorithms/)** · **[按任务阅读](/modules/reading-paths)** · 选型：[算法菜单](/guide/algorithm-and-ansatz-menu)
:::

## 深读地图

| 类别 | 入口 |
|------|------|
| 基态 VQE / UCC / ADAPT / … | [algorithms/](./algorithms/) 第二节表 |
| 激发态 | [excited-states](./excited-states) → VQD / QSE / SCEOM |
| ADAPT / IQEB | [adapt-iqeb](./adapt-iqeb) |
| 测量与池 | [pauli-protocol](./algorithms/pauli-protocol) · [operator-pools](./algorithms/operator-pools) |
| 化学前置 | [chem](/modules/chem/) |
| 后端 | [backends](/modules/backends) |

## 注册表

```python
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids

print(list_registered_ansatz_ids())
print(list_registered_algorithm_ids())
```

## 最小验证

```bash
python -c "from qchem_stack.sdk import run_pipeline_from_config; print(run_pipeline_from_config('configs/example_h2.yaml').get('energy_after_variational'))"
```
