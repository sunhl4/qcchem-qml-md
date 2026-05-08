# Day 2 Audit: Export Stable Keys (2026Q2)

目标：审计 `PARITY_EXPORT_V2_STABLE_KEYS` 在代表配置集上的完整性，确认 90 天推进不会破坏 Methods 最小契约。

## 审计范围

- 脚本：`scripts/export_parity_criteria_table.py`
- 稳定键集合：`qchem_stack.protocols.inquanto_contract.PARITY_EXPORT_V2_STABLE_KEYS`
- 样例配置：`scripts/check_parity_export_sample.py` 的 22 个配置（含 `example_h2o_sto3g_cas44.yaml`、`example_n2_sto3g_cas44.yaml`）

## 结果摘要

- 审计配置数：`22`
- 缺失稳定键配置数：`0`
- `missing` 明细：空
- 非稳定扩展键数量区间：`60 ~ 61`（符合“稳定键是最小契约，其余可扩展”的设计）
- 含 `resource_estimation_preview_v1` 的配置：
  - `configs/example_h2_qpe_track_parity_integrations.yaml`

## 稳定键清单（当前）

- `parity_export_schema_version`
- `experiment_id`
- `computable_abstract`
- `excited_resource_from_config`
- `inquanto_gap_categories`
- `iqeb_implementation_path`
- `pauli_protocol_expectation_path`
- `protocol_expectation_semantics_v1`
- `embedding`

## 结论

- Day 2 审计通过：当前样例集未出现稳定键回归。
- 后续若新增导出能力，应继续维持“稳定键不破坏、扩展键可演进”的策略。
