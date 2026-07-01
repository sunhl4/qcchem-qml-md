# Week 1 Regression Report (2026Q2)

## 执行目标

- 验证导出稳定键在扩样配置集下无回归。
- 验证 P2-W1（Methods/export）与 P2-W2（plugin 分解）相关测试可通过。
- 同步执行文档，建立 Day1/Day2/Month1 的证据链。

## 执行命令与结果

1. `.venv/bin/python scripts/check_parity_export_sample.py`
   - 结果：通过（22 配置样例）
2. `.venv/bin/pytest tests/repro/test_methods_resource_unified_export.py tests/repro/test_export_parity_golden.py -q`
   - 结果：`18 passed`
3. `.venv/bin/pytest tests/chem/test_decomposition_plugin_pipeline.py tests/repro/test_methods_resource_unified_export.py -q`
   - 结果：`5 passed`

## 文档同步

- Day1 盘点：`docs/execution/day01_gap_inventory_2026Q2.md`
- Day2 审计：`docs/execution/day02_export_keys_audit_2026Q2.md`
- Month1 签字：`docs/execution/month1_baseline_signoff_2026Q2.md`

## 备注

- 本轮回归使用仓库本地虚拟环境：`.venv/`。
- 继续遵循“稳定键不破坏，扩展键可演进”原则。
