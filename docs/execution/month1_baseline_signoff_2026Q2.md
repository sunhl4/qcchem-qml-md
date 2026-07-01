# Month 1 Baseline Signoff (2026Q2)

范围：P2-W1 / P2-W2 的“最小闭环”基线，作为 90 天计划的首月签字页。

## P2-W1（资源叙事）基线

- `resource_estimation_preview_v1` 已具备 config-only 与 pipeline 两模式：
  - 实现：`src/qchem_stack/integrations/resource_estimation_preview.py`
  - 导出：`scripts/export_parity_criteria_table.py`
  - 测试：`tests/repro/test_methods_resource_unified_export.py`
- parity 抽样已覆盖 22 份配置（含 H2O/N2 CAS 样例）：
  - `scripts/check_parity_export_sample.py`

## P2-W2（分解路径）基线

- plugin 最小可跑链路已形成并可回归：
  - 配置：`configs/example_decomposition_plugin_toy.yaml`
  - 执行：`embedding.mode=plugin`
  - 测试：`tests/chem/test_decomposition_plugin_pipeline.py`
- 新增可检证元数据（本轮）：
  - `embedding_workflow.decomposition_plugin_json_resolved_path`
  - `embedding_workflow.integral_source`
  - `embedding_workflow.epistemic_bound`

## Day 1 / Day 2 产出链接

- Day 1 差距盘点：`docs/execution/day01_gap_inventory_2026Q2.md`
- Day 2 键审计：`docs/execution/day02_export_keys_audit_2026Q2.md`

## 回归记录（本轮）

- `pytest`：
  - `.venv/bin/pytest tests/chem/test_decomposition_plugin_pipeline.py tests/repro/test_methods_resource_unified_export.py -q`
  - 结果：`5 passed`
- parity 导出抽样：
  - `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 结论

- Month 1 的基线目标已建立：P2-W1 有可检证导出路径，P2-W2 有最小分解主线与回归锚点。
- 下一步进入 Month 2：P2-W3 / W4 / W5 的深度推进与矩阵联动收口。
