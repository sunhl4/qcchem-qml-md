---
sidebar_position: 48
---

# 分解插件最小 demo（P2-W2 轨 A）

本教程对应仓库 ADR：`docs/ADR_P2_decomposition_scope.md`（轨 A：`embedding.mode: plugin` + 玩具 JSON）。

## 配置

- **`configs/example_decomposition_plugin_toy.yaml`**：

```yaml
embedding:
  mode: plugin
  plugin:
    name: uniform_fragment_guess
    json_path: configs/decomposition_plugin_toy_integrals.json
```

- **积分 JSON**：`configs/decomposition_plugin_toy_integrals.json`（`schema: decomposition_plugin_toy_v1`）

完整 nested 键说明见仓库 [`docs/说明_embedding配置.md`](https://github.com/NVIDIA/qcchem-qml-md/blob/main/docs/说明_embedding配置.md)。

## 验收

- `pytest tests/test_decomposition_plugin_pipeline.py`（端到端 `run_pipeline_sync`）
- `python scripts/export_parity_criteria_table.py configs/example_decomposition_plugin_toy.yaml`
- 检查 `run_summary` 与导出结果中的分解插件字段

## 另见

- [案例：H2 家族](./case-study-h2-family.md)（索引互链）
