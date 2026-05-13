---
sidebar_position: 48
---

# 分解插件最小 demo（P2-W2 轨 A）

本教程对应仓库 ADR：`docs/ADR_P2_decomposition_scope.md`（轨 A：`embedding.mode: plugin` + 玩具 JSON）。

## 配置

- **`configs/example_decomposition_plugin_toy.yaml`**：`embedding.mode: plugin`、`decomposition_plugin: uniform_fragment_guess`
- **积分 JSON**：`configs/decomposition_plugin_toy_integrals.json`（`schema: decomposition_plugin_toy_v1`）

## 验收

- `pytest tests/test_decomposition_plugin_pipeline.py`（端到端 `run_pipeline_sync`）
- `python scripts/export_parity_criteria_table.py configs/example_decomposition_plugin_toy.yaml`
- Parity 矩阵 §3「分解插件」行 — [公开矩阵](../parity/public-matrix)

## 另见

- [案例：H2 家族](./case-study-h2-family.md)（索引互链）
