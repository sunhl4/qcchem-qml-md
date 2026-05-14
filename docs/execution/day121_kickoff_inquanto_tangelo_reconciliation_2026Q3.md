# Day121 Kickoff — InQuanto / Tangelo 再对照（2026Q3）

## 元数据

- **PLAN_START_DATE**：（在此填入 ISO 8601 日期，建议 = Day120 封板次日）
- **负责人**：（可选）
- **配套日历**：[`day121_day180_inquanto_tangelo_calendar_2026Q3.md`](day121_day180_inquanto_tangelo_calendar_2026Q3.md)

## 目标（当日）

1. 冻结本 60 天周期的 **对照范围**：[`docs/inquanto_public_parity_matrix.md`](../inquanto_public_parity_matrix.md) §1–§4 中与 **公开文档可检证**相关的行 + [`docs/算法面广度_InQuanto_Tangelo对照索引.md`](../算法面广度_InQuanto_Tangelo对照索引.md) §2–§4。
2. 拉一条 **机读锚点清单**（勾选已有 / 待补文档 / 待补测试）：

| 锚点 | 已有证据 | 缺口动作 |
|------|----------|----------|
| `GET /v1/meta/capability-surface` | `tests/test_api_runs.py::test_capability_surface_*` | |
| `tangelo_public_mapping_alias_surface_v1` | `tests/test_fermion_qubit_mapping.py` 等 | |
| `operator_pool_registry_export_v1` | `tests/test_operator_pool_registry_export.py` | |
| `algorithm_registry_export_v1` | `algorithm_registry` / contract | |
| `variational_registry_export_v1` | `variational_plugins/registry` | |
| `inquanto_gap_categories()` | `tests/test_inquanto_contract.py` | |

3. 确认 **排除项** 仍成立：Nexus IAM、HQC 货币、商业 Qermit、cuTensorNet L0、JKMN/HCB 可执行映射。

## 验证（当日最小）

```bash
pytest tests/test_api_runs.py::test_capability_surface_v1 \
  tests/test_api_runs.py::test_capability_surface_matches_inquanto_contract \
  tests/test_inquanto_contract.py tests/test_fermion_qubit_mapping.py -q --tb=short
```

（需 `pip install -e ".[dev]"` 或等价环境。）

## 结论

- **状态**：（进行中 / 已完成 Day121）
- **遗留滚动到 Day122**：（列出）
