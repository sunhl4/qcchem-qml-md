# P2 缓冲周模板（计划 D83–D87）

**用途**：缓冲周不是「空档」，而是 **与主链路同一闸门** 下的维护窗口：矩阵/gap/导出/schema 的小幅漂移修补。

## 最小闸门（每日或每周两次）

1. `python -m pytest`
2. `python scripts/check_parity_export_sample.py`
3. `python scripts/sample_pipeline_configs.py`（可选：`--pipeline`，依赖 PySCF 环境）
4. `bash scripts/verify_ninety_day_gates.sh`（可选聚合脚本；超时环境请分项跑）

## 缓冲周内允许的范围

- 更新 [`P2_execution_alignment_notes.md`](P2_execution_alignment_notes.md) 滚动表一行（公开文档钉扎 / Tangelo registry）。
- 对齐 [`inquanto_public_parity_matrix.md`](inquanto_public_parity_matrix.md) 与 `inquanto_gap_categories()`（已有 `tests/test_gap_parity_matrix_anchors.py` 守门）。
- **不做**：版本号仪式化发布、CHANGELOG 条目堆砌（除非当月确有对外变更说明需求）。

台账对应：[`P2_ninety_day_execution_checklist.md`](P2_ninety_day_execution_checklist.md) D83–D87。
