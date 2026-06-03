# Day 5 Execution: parity sample 覆盖扩展与稳定性修复

目标：扩大 `check_parity_export_sample.py` 覆盖并降低抽样列表维护风险。

## 本日实现

- 扩样：
  - 新增 `configs/example_fe_sto3g_helike_rhf_cas22.yaml` 到 `SAMPLE_CONFIGS_REL`。
- 稳定性防护：
  - 新增 `_sample_configs_unique_or_raise()`，对抽样列表做重复项检测。
  - 如果出现重复配置，脚本直接报错并退出（避免“看似通过、实际重复覆盖”）。

## 验证

- `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 结论

- Day 5 目标完成：抽样覆盖进一步扩展，列表维护具备显式去重防护。
