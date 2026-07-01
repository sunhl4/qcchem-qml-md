# Day 9 Execution: plugin 输入 schema 与校验增强

目标：强化 `embedding.mode=plugin` 的输入校验，避免仅在主片段解析时才暴露错误。

## 本日实现

- `src/qchem_stack/chem/embedding/decomposition_plugin.py`
  - 新增 `_validate_fragment_block()`：
    - 校验 `n_qubits` 必填且 `>=1`
    - 校验 `pauli_coefficients` 为非空列表
    - 校验每项包含 `label` 与 `coeff`
    - 校验 `coeff` 可转数值
    - 校验 `label` 与 `n_qubits` 长度及字符集匹配（复用 `_pauli_label_to_operator`）
  - 在 `_resolve_decomposition_plugin_payload()` 中：
    - 对 **全部 fragments** 执行上述校验（不只主片段）
    - 强制 `primary_fragment_id` 必须命中 fragments map

- `tests/chem/test_decomposition_plugin_pipeline.py`
  - 新增失败路径回归：
    - `primary_fragment_id` 缺失于 fragments map
    - 次片段 Pauli 标签长度与 `n_qubits` 不匹配

## 验证

- `.venv/bin/pytest tests/chem/test_decomposition_plugin_pipeline.py -q`
  - 结果：`4 passed`
- `.venv/bin/python scripts/check_parity_export_sample.py`
  - 结果：通过

## 结论

- Day 9 完成：plugin 路径输入校验更早失败、更可读，降低配置问题在运行后期才暴露的风险。
