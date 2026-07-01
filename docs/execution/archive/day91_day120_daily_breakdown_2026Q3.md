# Day91–Day120 Daily Breakdown (2026Q3)

角色：把 `day91_next_phase_plan_2026Q3.md` 的周粒度计划细化到按天执行。

## 范围边界

- 继续执行 P2 深化，不跨越 L0 边界。
- 新增键遵循同源链：`contract -> export -> tests -> docs`。（`contract` = **`protocols/product_contract.py`** / **`qchem_stack.protocols.product_contract`**：`product_gap_categories()`、export 稳定键；见 [CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)。）
- `partial` / `n/a` 口径保持一致，不做闭源等价宣称。

## 日历拆分（Day91–Day120）

| Day | 主题 | 主要输入 | 当日输出（最小） | 验收要点 |
|-----|------|----------|------------------|----------|
| Day91 | W1 kickoff：字段盘点 | `day91_next_phase_plan_2026Q3.md` | `day91_*.md` 记录 + 字段候选清单 | 目标与边界明确 |
| Day92 | W1 字段草案 | `product_contract.py`、`export_parity_criteria_table.py` | 字段命名草案与映射表 | 命名与现有 schema 不冲突 |
| Day93 | W1 contract 预接入 | `product_contract.py` | run/export 预注册字段草案 | key 注册完整 |
| Day94 | W1 export 预接入 | `export_parity_criteria_table.py` | config-only / `--results` 对应镜像草案 | 字段可导出 |
| Day95 | W1 test 预接入 | `tests/repro/test_methods_resource_unified_export.py` | 新增断言草案 | 失败路径可定位 |
| Day96 | W1 文档同步 | `docs/*`、`docusaurus-site/*` | 键名口径同步说明 | docs/docusaurus-site 同源 |
| Day97 | Week1 小结 | Day91–96 记录 | 周总结页（可并入 day97） | 本周遗留滚动到 Day98 |
| Day98 | W1 收口：代码 | contract/export/tests | 第一批可运行改动 | 子集 pytest 可跑 |
| Day99 | W1 收口：导出 | export + fixtures | `--results` 断言稳定 | 导出键无漂移 |
| Day100 | W1 收口：测试 | methods/parity tests | 回归补齐 | 关键测试通过 |
| Day101 | W1 收口：文档 | 差距/路线图/矩阵 | 文档对齐更新 | 文字口径与代码一致 |
| Day102 | 周闸门预检 | pytest 子集 + parity sample | 预检报告 | 问题可复现 |
| Day103 | 周闸门修复 | 预检缺陷清单 | 修复提交记录（执行页） | 阻塞项清零 |
| Day104 | Week2 闸门 | 全周产出 | 周闸门结论 | 进入 W3/W4 |
| Day105 | W3 设计对齐 | AVAS/CASSCF 边界文档 | W3 执行说明 | `partial` 口径稳定 |
| Day106 | W3 代码/测试 | driver 表面与审计 | 回归记录 | 不引入越界宣称 |
| Day107 | W3 文档同步 | 矩阵/差距计划 | 边界更新 | 矩阵与 gap 一致 |
| Day108 | W4 方案选择 | mitigation 映射文档 | 进阶块选型记录 | 选型有 DoD |
| Day109 | W4 代码推进 | mitigation 路径 | 新字段或新节点 | 机读可追溯 |
| Day110 | W4 测试推进 | mitigation tests | 回归断言补齐 | 失败路径覆盖 |
| Day111 | W3/W4 合并复核 | 代码 + 文档 | 联合阶段记录 | 口径一致 |
| Day112 | W3/W4 闸门 | pytest + parity sample | 阶段结论 | 进入 W7 收口 |
| Day113 | W7 索引规划 | docusaurus-site + examples | 索引任务表 | 覆盖三路径 |
| Day114 | W7 文档更新 | docusaurus-site guides | 更新记录 | 链接有效 |
| Day115 | W7 示例更新 | examples/README/索引 | 示例入口更新 | 新用户可跟跑 |
| Day116 | 双站一致性校验 | docs + docusaurus-site | 校验记录 | 关键入口互链 |
| Day117 | 总闸门预检 | 全量测试前检查 | 预检问题清单 | 问题可修复 |
| Day118 | 总闸门修复 | 预检问题 | 修复记录 | 关键阻塞清零 |
| Day119 | 总闸门执行 | 全量 `pytest` + parity sample | 总闸门结果 | 全绿或有明确例外 |
| Day120 | 月度封板 | 全部执行页 | 月度封板结论页 | 可进入下一周期 |

## 周闸门（每周固定）

1. 运行与记录：
   - `pytest`（当周相关子集）
   - `python scripts/check_parity_export_sample.py`
2. 一致性复核：
   - `src/qchem_stack/protocols/product_contract.py`（**`qchem_stack.protocols.product_contract`**：[CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)）
   - `scripts/export_parity_criteria_table.py`
   - 文档口径（`docs/` + `docusaurus-site/`）
3. 执行页更新：
   - 当周每天均有 `目标/实现/验证/结论`
   - 周末页给出“完成项/遗留项/下周入口”

## Day120 月度封板清单

- 全量 `pytest` 通过（或 skip 有记录）。
- parity 抽样脚本通过。
- 新增键全部完成同源链更新（contract/export/tests/docs）。
- `partial` / `n/a` 口径无越界。
- `docs/execution/README.md` 已收录 Day91–Day120 关键产物。

详单见：`docs/execution/day120_gate_checklist_2026Q3.md`。
