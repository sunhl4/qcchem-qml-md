# Day 12 Execution: plugin/export/contract 字段对齐

目标：完成 P2-W2 的“插件链路 + export + contract + 测试”同步闭环，避免键漂移。

## 本日实现

- `src/qchem_stack/chem/embedding/decomposition_plugin.py`
  - 新增 `decomposition_fragment_pauli_term_counts` 元数据（每片段 Pauli 项数）。
- `src/qchem_stack/orchestration/pipeline.py`
  - `embedding_workflow`（plugin）新增：
    - `decomposition_fragment_pauli_term_counts`
    - `decomposition_total_pauli_terms`
  - `run_summary` 新增：
    - `decomposition_total_pauli_terms`
    - `mitigation_zne_mode_yaml`
    - `mitigation_zne_scales_yaml`
    - `protocol_zne_mode`
- `src/qchem_stack/protocols/inquanto_contract.py`
  - 将上述 `run_summary` 新键注册到 `RUN_SUMMARY_DOCUMENTED_KEYS`。
- `scripts/export_parity_criteria_table.py`
  - 新增 `algorithm_registry_alignment_v1` 与 `md_ml_repro_freeze_fields_v1`（W5/W6 证据块）。
  - `--results` 路径镜像新增 plugin 与 ZNE 相关 `run_summary` 键。
- 测试增强：
  - `tests/test_decomposition_plugin_pipeline.py`
  - `tests/test_export_parity_golden.py`
  - `tests/test_methods_resource_unified_export.py`

## 验证（计划）

- `pytest tests/test_decomposition_plugin_pipeline.py -q`
- `pytest tests/test_export_parity_golden.py tests/test_methods_resource_unified_export.py -q`
- `python scripts/check_parity_export_sample.py`

## 结论

- Day12 形成“代码键名 = contract 注册 = export 暴露 = 测试断言”的最小闭环，满足 W2 连续推进要求。
