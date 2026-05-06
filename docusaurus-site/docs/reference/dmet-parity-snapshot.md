# DMET 形流程与 parity_snapshot 契约

本文说明嵌入相关配置在 pipeline 与 `parity_snapshot` 中的可观测语义。

## 核心配置

| 字段 | 说明 |
|------|------|
| `embedding.mode` | `none` / `dmet` / `projection` |
| `fragment_labels` | 片段标识 |
| `dmet_hamiltonian_source` | 杂质哈密顿量来源策略 |

## pipeline 行为摘要

- 先构造主 Hamiltonian
- 若 `mode=dmet`，写入 embedding 工作流字段
- 可在 `repro` 中记录片段求解与快照元数据

## parity_snapshot 关键键

- `dmet_solver_mode`
- `dmet_one_shot_open_ledger`
- `schmidt_embedding_production`
- `open_stack_contract_schema`

## 使用建议

- 教程和烟测可先用最小 dmet stub 路径
- 对外报告时明确“结构对齐”与“数值求解”边界
