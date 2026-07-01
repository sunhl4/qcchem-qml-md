# Day 8 Execution: P2-W2 plugin 主路径切片（最小可跑数据结构）

目标：把 `embedding.mode=plugin` 从单片段 toy 进一步推进到“多片段载荷可检证摘要”。

## 本日实现

- 代码增强：`src/qchem_stack/chem/embedding/decomposition_plugin.py`
  - 提取 `_resolve_decomposition_plugin_payload()` 统一解析与校验。
  - 在 `QubitHamiltonian.meta` 增加：
    - `decomposition_primary_fragment_id`
    - `decomposition_fragment_count`
    - `decomposition_fragment_ids`
- 管线增强：`src/qchem_stack/orchestration/pipeline.py`
  - `embedding_workflow`（plugin 分支）同步暴露上述三项摘要字段。
- 新增两片段示例：
  - `configs/decomposition_plugin_two_fragment_integrals.json`
  - `configs/example_decomposition_plugin_two_fragment.yaml`
- 测试增强：
  - `tests/chem/test_decomposition_plugin_pipeline.py` 新增两片段摘要断言。
  - `tests/repro/test_export_parity_golden.py` 与 `scripts/check_parity_export_sample.py` 纳入新配置。

## 验证

- `.venv/bin/pytest tests/chem/test_decomposition_plugin_pipeline.py tests/repro/test_export_parity_golden.py tests/repro/test_methods_resource_unified_export.py -q`
  - 结果：`21 passed`
- `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 结论

- Day 8 完成：plugin 主路径已具备“多片段载荷摘要”的最小可跑数据结构，为 Day9/Day10 的 schema/执行链深化打下基础。
