# `embedding` — 嵌入 / 分片怎么搞

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**源码：** `embedding.py`, `embedding_specs.py`, `embedding_enums.py`  
**详细说明：** [说明_embedding配置.md](说明_embedding配置.md)

**用 `mode` 选分支：** `none` | `dmet` | `projection` | `plugin`

## 各 mode 共有字段（`EmbeddingBase`）

| 字段 | 说明 |
|------|------|
| `embedding_input_representation` | 输入用 MO / AO / Lowdin 正交 AO |
| `n_scf_cycles_embedding` | 嵌入 SCF 循环数 |
| `classical_reference_method` | 经典参考方法标签 |
| `oniom_layers_v1` | ONIOM 层 sidecar |

## `mode: dmet`

| 子块 | 关键字段 |
|------|----------|
| `dmet.fragment_labels` | fragment 名字 |
| `dmet.hamiltonian_source` | 哈密顿量从哪来（含 Schmidt 生产路径） |
| `dmet.schmidt.*` | Schmidt：原子索引、多 fragment、bath 轨道数、DMET 循环等 |
| `dmet.fragment_solver.*` | fragment 上跑 ED 还是 VQE |

### Schmidt 常用字段（`dmet.schmidt`）

| 字段 | 说明 |
|------|------|
| `fragment_atom_indices` | 单 fragment 的原子编号 |
| `multi_fragment_atom_groups` | 多 fragment 分组 |
| `multi_primary_fragment_index` | 主 fragment 是第几个 |
| `n_bath_spatial` | bath 空间轨道数 |
| `dmet_max_cycles` | DMET 外循环（≤ `SCHMIDT_DMET_MAX_CYCLES_LIMIT`） |
| `run_vqe_on_all_fragments` | 是否每个 fragment 都跑 VQE |
| `per_fragment_vqe_maxiter` | 覆盖全局 `quantum.vqe.maxiter` |

## `mode: projection`

| 字段 | 说明 |
|------|------|
| `projection.low_level` / `high_level` | 低/高水平方法 |
| `projection.quantum_hamiltonian` | 量子哈密顿量作用范围 |
| `projection.fragment_atom_indices` | 投影涉及的原子 |

## `mode: plugin`

| 字段 | 说明 |
|------|------|
| `plugin.name` | 插件名 |
| `plugin.json_path` | 可选 JSON 配置 |

**谁在用：** pre-quantum 建哈密顿量、embedding_workflow 阶段等。
