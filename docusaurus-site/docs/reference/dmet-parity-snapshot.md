# DMET 形流程与 parity_snapshot 契约

本文说明嵌入相关配置在 pipeline 与 `parity_snapshot` 中的可观测语义。

Nested 配置字段见仓库 [`docs/说明_embedding配置.md`](https://github.com/NVIDIA/qcchem-qml-md/blob/main/docs/说明_embedding配置.md)。

## 适用场景

- 你要确认 embedding 配置是否被正确记录
- 你要在验收中区分“结构对齐”和“数值求解深度”
- 你要把嵌入相关字段纳入 `repro` 检查

## 核心配置（nested YAML）

| 路径 | 说明 |
|------|------|
| `embedding.mode` | `none` / `dmet` / `projection` / `plugin` |
| `embedding.dmet.fragment_labels` | DMET 片段标识 |
| `embedding.dmet.hamiltonian_source` | 杂质哈密顿量来源策略 |
| `embedding.projection.quantum_hamiltonian` | projection 变分 Hamiltonian 策略 |
| `embedding.plugin.name` / `json_path` | 分解插件模式 |

`repro` / `embedding_workflow` 输出仍使用历史键名（如 `dmet_hamiltonian_source`），与 YAML nested 路径对应。

## pipeline 行为摘要

- 先构造主 Hamiltonian
- 若 `mode=dmet`，写入 embedding 工作流字段
- 可在 `repro` 中记录片段求解与快照元数据

## parity_snapshot 关键键

- `dmet_solver_mode`
- `dmet_one_shot_open_ledger`
- `schmidt_embedding_production`
- `open_stack_contract_schema`

## 最小验证流程

1. 运行最小 embedding 配置  
2. 检查 `run_summary` 与 `repro.parity_snapshot`  
3. 确认关键键存在且语义与配置一致  

## 使用建议

- 教程和烟测可先用最小 dmet stub 路径
- 对外报告时明确“结构对齐”与“数值求解”边界

## 关联页面

- [Parity 契约与 workflow-preview（稳定 import）](/reference/parity-contract-import-paths)
- [Projection 嵌入深入](/tutorial/projection-embedding-deep-dive)
- [P1 化学与嵌入](/guide/chemistry-and-embedding)
- [工程架构](/concept/engineering-architecture)
