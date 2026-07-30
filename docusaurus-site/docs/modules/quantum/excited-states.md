---
title: quantum · 激发态（摘要）
description: VQD / QSE / SCEOM 导航；详细文献与数学见算法深读。
---

# quantum · 激发态（摘要）

激发态工作流的**导航页**。理论、参数表与端到端验证见各深读，本页不重复薄内容。

:::info 请读深读页
→ [VQD](./algorithms/vqd) · [QSE](./algorithms/qse) · [SCEOM](./algorithms/sceom)
:::

## 速查

| 算法 | YAML 线索 | 深读 |
|------|-----------|------|
| VQD | `excited.vqd` | [vqd](./algorithms/vqd) |
| QSE | `excited.qse` | [qse](./algorithms/qse) |
| SCEOM | `excited.sceom` | [sceom](./algorithms/sceom) |

全目录：[算法深读索引](./algorithms/) · 选型：[激发态 VQD / QSE / SCEOM](/guide/excited-states-vqd-qse-sceom)。

## 公开 API

```python
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids

print(list_registered_excited_ids())
```

基态前置常先跑 VQE / UCCSD，再挂激发插件——见 [VQE / HEA](./algorithms/vqe-hea) 与 chem [hamiltonian](/modules/chem/hamiltonian)。
