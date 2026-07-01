# Day 3 Execution: resource_estimation_preview_v1 results 一致性

目标：确保 `--results` 导出时，`resource_estimation_preview_v1` 与运行态 `resource_summary` 字段逐项一致。

## 本日实现

- 测试增强：`tests/repro/test_methods_resource_unified_export.py`
  - 在 `test_methods_resource_unified_qpe_plus_tket_probe_schema` 中新增逐字段一致性断言：
    - `n_circuits`
    - `n_qubits`
    - `sum_shots`
    - `max_depth`
    - `sum_twoq`
    - `n_pauli_terms`
    - `n_pauli_groups`
  - 规则：当运行态字段非空时，`resource_estimation_preview_v1.resource_summary_*` 必须与运行态值一致。

## 验证

- `.venv/bin/pytest tests/repro/test_methods_resource_unified_export.py -q`
- 结果：通过（本地环境中按依赖可运行项执行）。

## 结论

- Day 3 目标完成：`resource_estimation_preview_v1` 从“存在性检查”提升到“字段一致性检查”。
