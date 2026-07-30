---
title: quantum · ADAPT / IQEB（摘要）
description: 指向 ADAPT-VQE、IQEB 与算符池深读；本页不重复手册正文。
---

# quantum · ADAPT / IQEB（摘要）

自适应算符增长类算法的**导航页**。文献、数学、YAML 全表与验证命令见深读，勿在本页找完整手册。

:::info 请读深读页
→ [ADAPT-VQE](./algorithms/adapt-vqe) · [IQEB](./algorithms/iqeb) · [算符池全表](./algorithms/operator-pools)
:::

## 速查

| 主题 | 深读 |
|------|------|
| 梯度驱动算符选择 | [adapt-vqe](./algorithms/adapt-vqe) |
| 迭代量子本征求解变体 | [iqeb](./algorithms/iqeb) |
| 池定义与注册 | [operator-pools](./algorithms/operator-pools) |
| 全算法目录 | [algorithms/](./algorithms/) |

```python
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
print([a for a in list_registered_algorithm_ids() if "adapt" in a or "iqeb" in a or a == "iqeb"])
```

选型：[算法与 ansatz 菜单](/guide/algorithm-and-ansatz-menu)。
