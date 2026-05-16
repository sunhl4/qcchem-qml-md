# Day 4 Execution: resource_estimation_preview_v1 文档与 caveat 同步

目标：把 Day 3 的结果态一致性与资源切片边界明确写入对外矩阵文档。

## 本日实现

- 更新 `docs/public_parity_matrix.md` 的资源行（§1）：
  - 增补 `resource_estimation_preview_v1` 的可选导出入口：
    - 开关：`parity_integrations.resource_estimation_preview: true`
  - 明确 caveat：
    - 非云计价（不对齐 Nexus/HQC 商业计费）
    - 非闭源 L0 resource estimator

## 验证

- 文档口径与代码一致：
  - 导出实现：`scripts/export_parity_criteria_table.py`
  - 生成函数：`src/qchem_stack/integrations/resource_estimation_preview.py`
  - 测试：`tests/test_methods_resource_unified_export.py`

## 结论

- Day 4 目标完成：资源导出切片的“能力 + 边界”在矩阵文档中完成显式对齐。
