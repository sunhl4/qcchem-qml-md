# Day 25 Milestone: P2-W2 最小可跑闭环签字

范围：Day8–Day25 的 plugin 主路径深化（多片段、输入校验、run_summary/export 对齐）。

## 交付核对

- Plugin 多片段摘要：`decomposition_primary_fragment_id`、`decomposition_fragment_count`、`decomposition_fragment_ids`。
- Plugin 术语深化：`decomposition_fragment_pauli_term_counts`、`decomposition_total_pauli_terms`。
- 机读契约：`RUN_SUMMARY_DOCUMENTED_KEYS` 与导出镜像同步。
- 抽样覆盖：`configs/example_decomposition_plugin_two_fragment.yaml` 已纳入 parity 样本脚本。

## 闸门结果

- `pytest`（plugin/export 相关）通过。
- `scripts/check_parity_export_sample.py` 通过。
- 矩阵/差距口径维持 `partial` 与 ADR（轨A）一致，无越界宣称。

## 结论

- P2-W2 在“最小可跑 + 可审计 + 可回归”口径下完成 Day25 里程碑。
