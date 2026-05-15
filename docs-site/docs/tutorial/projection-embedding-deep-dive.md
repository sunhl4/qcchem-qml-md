---
title: Projection 嵌入：轨迹键与 Mulliken 变分哈密顿量
description: 读懂 embedding.mode=projection 时 parity_snapshot 与可选 fragment_mulliken_mo 路径
---

本页对应广义 P1 **教程波次 G** 的可选第三条：**projection trace「深度」**——不只列出 YAML 文件名，而是说明「变分层到底用什么 Hamiltonian」与 **机读键**落在哪里。

## 两条 projection 量子哈密顿量路径

配置键：`embedding.projection_quantum_hamiltonian`。

| 取值 | 变分阶段 `QubitHamiltonian` | 典型 YAML |
|------|-----------------------------|-----------|
| `global_active_space`（默认） | 与全局 `active_space` + `fermion_qubit_mapping` 一致；projection 块主要提供 **L1 轨迹元数据** | `configs/example_h2_projection_trace.yaml` |
| `fragment_mulliken_mo` | 在 RHF MO 上按 **片段 Mulliken 权重**选活性轨道，再 **CASCI 活性积分** + 所选映射构建哈密顿量（**非**全文 many-body projection DMRG 类产品深度） | `configs/example_h4_projection_mulliken.yaml` |

诚实边界写在管线快照的 **`epistemic_bound`**（若存在）：_open stack_ 只保证 **命名、轨道来源与 integral_source** 可审计，不与闭源默认数值对齐。

## 你应在 `repro` 里盯住的键

- **`repro.embedding_config`**：完整 `EmbeddingSpec`（含 `projection_*` 字段）。
- **`repro.parity_snapshot.projection_embedding_open_trace`**（或同类 **`projection_*`** 轨迹）：L1 闭合用 flat 字段；字段表见 [DMET / parity_snapshot 参考](/reference/dmet-parity-snapshot)（母稿在仓库 `docs/技术文档_DMET与parity_snapshot开放契约.md`）。
- **`embedding_workflow`**（pipeline 输出顶层）：`mode: projection`、`projection_quantum_hamiltonian`、`projection_selected_mo_indices`（Mulliken 路径若有审计）等。

导出：`scripts/export_parity_criteria_table.py` 对 projection 样例 YAML 跑 config-only 即可看到 gap 行与稳定 export 键（见 `check_parity_export_sample.py` 抽样列表）。

## Smoke

```bash
python scripts/smoke_pipeline.py --projection-trace
```

## 相关

- [工作流与 YAML](/tutorial/workflow-overview)
- `configs/example_h2_projection_trace.yaml`、`configs/example_h4_projection_mulliken.yaml`
- [公开 parity 矩阵](/product/roadmap) §3 Projection 行
