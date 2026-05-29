# Day 6 Execution: 回归日（导出与命名一致性）

目标：执行 Day1–Day5 相关回归并确认命名/契约无回退。

## 本日执行

- `.venv/bin/pytest tests/test_export_parity_golden.py tests/test_methods_resource_unified_export.py -q`
  - 结果：`18 passed`
- `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 命名/契约检查

- `resource_estimation_preview_v1` 保持：
  - config-only：`mode=config_only`
  - results 合并：`mode=pipeline`
- 稳定键集合 `PARITY_EXPORT_V3_STABLE_KEYS` 在抽样配置上无缺失。

## 结论

- Day 6 目标完成：前 5 天改动通过回归，导出命名与契约保持稳定。
