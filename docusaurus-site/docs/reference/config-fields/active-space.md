---
title: active_space 配置字段
description: strategy（manual/cas/avas）、轨道电子数与费米子–量子比特映射。
---

# `active_space` — 活性空间选多大

> **返回索引：** [配置字段](./) · 仓库 [说明_config模块技术参考手册.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_config模块技术参考手册.md)

**源码：** `active_space.py`, `active_space_specs.py`, `active_space_mapping_specs.py`  
**详细说明：** [说明_active_space配置.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_active_space配置.md)

**用 `strategy` 选分支：** `manual` | `cas` | `avas_stub` | `avas`

```yaml
active_space:
  strategy: cas
  mapping:
    fermion_qubit: jordan_wigner
  cas:
    n_orbitals: 4
    n_electrons: 4
```

**读轨道/电子数请用 helpers，别自己 if/else：**

```python
from qchem_stack.config import resolve_n_orbitals, resolve_n_electrons, resolve_fermion_qubit_mapping

n_orb = resolve_n_orbitals(cfg.active_space)
n_el = resolve_n_electrons(cfg.active_space)
mapping = resolve_fermion_qubit_mapping(cfg.active_space)
```

**谁在用：** SCF 后的活性空间处理、pre-quantum 积分、qubit 映射。

相关：[映射手册](/modules/chem/mappings) · [AVAS/CASSCF](/modules/chem/avas-casscf)。
