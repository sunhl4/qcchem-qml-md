# Day 65 Stage Report: P2-W5 / P2-W6

范围：registry 对齐（W5）与 MD/ML 可检证字段冻结（W6）。

## W5（registry）

- config-only 导出新增 `algorithm_registry_alignment_v1`：
  - `algorithm_registry_ids`
  - `ansatz_registry_ids`
  - `documented_fermion_qubit_mappings`
- 目标：把算法/ansatz/mapping 对齐从“文档叙事”提升到“机读快照”。

## W6（MD/ML）

- config-only 导出新增 `md_ml_repro_freeze_fields_v1`：
  - `qmframe_fields` 来自 `QMFrame.model_fields`。
- 目标：维持 P2-W6 的可审计冻结字段基线，避免文档与代码漂移。

## 验证

- `tests/test_methods_resource_unified_export.py::test_registry_and_mdml_blocks_in_config_only_export` 覆盖新增块。

## 结论

- W5/W6 达成“可导出、可断言、可回归”的阶段签字要求。
