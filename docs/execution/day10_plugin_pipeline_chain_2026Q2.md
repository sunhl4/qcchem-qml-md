# Day 10 Execution: plugin 路径最小执行链补强（run_summary 对齐）

目标：让 `embedding.mode=plugin` 在 `run_summary` 中具备可检证摘要，补齐“配置 -> workflow -> run_summary”闭环。

## 本日实现

- 更新 `src/qchem_stack/orchestration/pipeline.py` 的 `_attach_run_summary`：
  - 当 `embedding.mode == "plugin"` 时写入：
    - `decomposition_plugin_yaml`
    - `decomposition_primary_fragment_id`
    - `decomposition_fragment_count`
  - 数据来源为 YAML 与 `embedding_workflow` 摘要字段（Day8 已接入）。

- 更新 `src/qchem_stack/protocols/inquanto_contract.py`：
  - 将上述三个字段加入 `RUN_SUMMARY_DOCUMENTED_KEYS`，保持键注册 CI 一致。

- 更新 `tests/test_decomposition_plugin_pipeline.py`：
  - 对两片段示例新增 `run_summary` 断言，验证最小执行链完整闭合。

## 验证

- `.venv/bin/pytest tests/test_decomposition_plugin_pipeline.py tests/test_run_summary_key_registry.py -q`
  - 结果：`7 passed`
- `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 结论

- Day 10 完成：plugin 主路径在 `run_summary` 中可直接被 Methods/审计消费，执行链从配置到导出语义更完整。
