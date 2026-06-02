# `chemistry_extended` — 溶剂、周期边界等扩展选项

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**源码：** `chemistry_extended.py`, `chemistry_extended_specs.py`

| 子块 | 关键字段 | 用在哪 |
|------|----------|--------|
| `solvent` | `model`, `epsilon` | 溶剂化 SCF |
| `pbc` | `cell_vectors_bohr`, `kpoint_mesh` | 周期体系 |
| `avas` | `ao_labels`, `threshold` | AVAS 活性空间 |
| `casscf` | 轨道优化相关 hook | CASSCF |
| `benchmarks` | `enabled`, `backend` | 经典 post-HF 对照 |
| `post_hf` | 积分交叉检验 / RDM | |
| `mo_transform` | MO 变换 hook | |
| `symmetry` | PySCF 对称性 | |
