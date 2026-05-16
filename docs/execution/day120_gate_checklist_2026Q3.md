# Day120 Gate Checklist (2026Q3)

用途：为 Day91–Day120 执行周期提供固定周闸门与最终封板检查表。

## Weekly gate checklist

每周结束至少完成一次：

- [ ] `pytest`（当周相关子集）通过并记录命令。
- [ ] `python scripts/check_parity_export_sample.py` 通过。
- [ ] 新增/改名键完成同源链：
  - [ ] `src/qchem_stack/protocols/product_contract.py`（`product_gap_categories()`、`PARITY_EXPORT_V3_STABLE_KEYS` 等 — [CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)）
  - [ ] `scripts/export_parity_criteria_table.py`
  - [ ] `tests/*`
  - [ ] `docs/*` 与 `docusaurus-site/*`
- [ ] `partial` / `n/a` 口径与矩阵一致，无越界宣称。
- [ ] 当周执行记录齐全（目标/实现/验证/结论）。

## Day120 closeout checklist

- [ ] 全量 `pytest` 通过（或 skip 原因已记录）。
- [ ] parity 抽样脚本通过。
- [ ] 关键文档三方一致：
  - [ ] `docs/public_parity_matrix.md`
  - [ ] `docs/public_parity_matrix.md`
  - [ ] `docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md`
- [ ] 下一阶段入口文档已更新（Day121+）。
- [ ] `docs/execution/README.md` 收录本周期产物。

## 记录模板

- 周次：`YYYY-Wxx`
- Gate 结论：通过 / 有条件通过 / 未通过
- 阻塞项：
  - （填写）
- 负责人：
  - （填写）
