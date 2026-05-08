# 三个月执行计划：融合 InQuanto 与 Tangelo 长处（开放栈）

**目标**：在不宣称闭源 L0 等价、不绑定商业云/专有硬件的前提下，把 `qchem_stack` 推进为“可审计 workflow + 算法广度 + embedding-first + 多后端 + Methods 导出”一体化软件。

**边界**：
- 不承诺 Quantinuum Nexus/HQC/OAuth/配额与 H 系硬件专优。
- 不承诺闭源 Qermit / `inquanto-cutensornet` 二进制等价。
- 所有新增能力必须落地到：`YAML` 配置、`repro/parity_snapshot/run_summary` 键、测试与文档。

---

## 1) 未完成工作清单（按优先级）

1. **P2-W1 资源叙事深化**：在已存在 `resource_estimation_preview_v1` 上扩展可发表字段与 Methods 文案。
2. **P2-W2 分解主线**：把 ONIOM/plugin 或预计算 fragment 输入从 toy 推进到“最小可跑产品路径”。
3. **P2-W3 经典化学深度**：AVAS/CASSCF 路线保持 `partial` 诚实边界，同时补可检证扩展钩子。
4. **P2-W4 缓解进阶块**：在现有 `qermit_analog` + runtime trace 上加 shadows 或 ZNE 变体。
5. **P2-W5 registry 深化**：补 Tangelo/InQuanto 公开叙事的算法/ansatz/mapping 对照与 conformance。
6. **P2-W6 MD/ML 贯通**：`QMEFDataset` 到 trainer smoke，冻结跨模块 `repro` 字段。
7. **P2-W7 教程与 examples**：形成“新用户三条路径”并挂 CI 抽样。

---

## 2) 12 周详细执行计划

### 第 1 月（周 1-4）：把 P2 基线变成硬闸门

- **周 1**
  - 扩大 `check_parity_export_sample` 覆盖到更多代表配置（含多原子 CAS）。
  - 产出 P2 执行台账（本文）并与 `与InQuanto能力差距与实施计划.md` 对齐。
  - DoD：脚本与现有 CI 兼容；文档明确每周验收口径。
- **周 2**
  - P2-W1 字段审计：梳理 `methods_resource_unified_v1` / `resource_estimation_preview_v1` 的重复与缺口。
  - 增补导出单测（config-only + --results 路径）。
  - DoD：导出 schema 无新增未注册顶键。
- **周 3**
  - P2-W2 方案二选一落地 ADR（ONIOM plugin 路径优先）。
  - 形成 1 个端到端最小配置（非 toy 描述，仍可 small system）。
  - DoD：`run_pipeline_sync` + export + docs 一致。
- **周 4**
  - 统一矩阵/差距文档/gap categories 三处表述。
  - DoD：`pytest` 与 `check_parity_export_sample.py` 过；无“文档说有、代码无”条目。

### 第 2 月（周 5-8）：补算法与化学深度

- **周 5**
  - P2-W3：AVAS/CASSCF 路线文档化 + 钩子边界固定（维持 `partial` 诚实口径）。
  - DoD：driver surface 对齐测试通过。
- **周 6**
  - P2-W4：新增一个 mitigation 进阶块（shadows 或 ZNE 变体二选一）。
  - DoD：DAG 报告与 runtime trace 同源不变量保持。
- **周 7**
  - P2-W5：registry 对照表与 `test_backend_conformance` 扩展。
  - DoD：新增 registry 键都可追溯到文档与导出。
- **周 8**
  - QPE/FT 与 NISQ 的 methods 对照样例补齐（至少 1 套可复跑产物）。
  - DoD：QPE 样例、VQE 样例在导出中可并排比较。

### 第 3 月（周 9-12）：产品化收口

- **周 9**
  - P2-W6：`QMEFDataset` + trainer smoke 接线，补 `l1_md_ml` 判据。
  - DoD：最小数据流可从导出回链到上游配置。
- **周 10**
  - P2-W7：整理 `examples/` 与 docs-site 三条入门路径。
  - DoD：每条路径至少 1 份 YAML + 1 份说明 + 1 个 smoke。
- **周 11**
  - 做一次全仓“契约稳定性周”：只修复 schema 漂移、命名漂移、文档失配。
  - DoD：无未注册 snapshot/export 顶键。
- **周 12**
  - 里程碑签字：更新 parity、差距计划、路线图，并输出季度总结。
  - DoD：残余 `partial` 全部进入 SLA 表，且每项有下一季度路径。

---

## 3) 每周固定闸门（必须全部满足）

1. `python -m pytest`（至少相关模块全绿）。
2. `python scripts/check_parity_export_sample.py` 通过。
3. `docs/inquanto_public_parity_matrix.md` 与 `inquanto_gap_categories` 无矛盾。
4. `docs/` 与 `docs-site/` 核心入口同步更新。
5. 新增能力必须有示例配置与最小回归测试。

---

## 4) 本轮已执行（立即落地）

- [x] 将多原子 CAS 样例纳入 parity 导出抽样：
  - `configs/example_h2o_sto3g_cas44.yaml`
  - `configs/example_n2_sto3g_cas44.yaml`
- [x] 新建三个月执行台账文档（本文），作为后续周推进与验收基准。
- [x] 完成 Day1 差距盘点并冻结首批目标映射（`docs/execution/day01_gap_inventory_2026Q2.md`）。
- [x] 完成 Day2 稳定键审计并确认 22 配置无缺失稳定键（`docs/execution/day02_export_keys_audit_2026Q2.md`）。
- [x] 完成 Week1 回归（`check_parity_export_sample` + 相关 pytest）并沉淀报告（`docs/execution/week1_regression_report_2026Q2.md`）。
- [x] 完成 Month1 P2-W1/W2 基线签字页（`docs/execution/month1_baseline_signoff_2026Q2.md`）。
- [x] 完成 Day3：`resource_estimation_preview_v1` 的 results 一致性断言（`docs/execution/day03_resource_preview_consistency_2026Q2.md`）。
- [x] 完成 Day4：资源切片 caveat 与矩阵同步（`docs/execution/day04_resource_preview_docs_sync_2026Q2.md`）。
- [x] 完成 Day5：抽样覆盖扩展（含 Fe CAS）与重复项防护（`docs/execution/day05_sample_coverage_and_stability_2026Q2.md`）。
- [x] 完成 Day6：导出与回归命名稳定性检查（`docs/execution/day06_regression_and_naming_2026Q2.md`）。
- [x] 完成 Day7：周收口并同步差距文档/路线图入口（`docs/execution/day07_week1_closeout_2026Q2.md`）。
- [x] 完成 Day8：P2-W2 plugin 主路径切片（多片段载荷摘要 + 新示例与回归）（`docs/execution/day08_p2w2_plugin_slice_2026Q2.md`）。
- [x] 完成 Day9：plugin 输入 schema/校验增强与失败路径回归（`docs/execution/day09_plugin_schema_validation_2026Q2.md`）。
- [x] 完成 Day10：plugin 最小执行链（run_summary 可检证字段）补强（`docs/execution/day10_plugin_pipeline_chain_2026Q2.md`）。

---

## 5) 三个月目标完成判据（季度终局）

- 至少 2 条 `partial` 项达到“可发表 L1+”收口（文档+机读+测试闭环）。
- P2-W1/W2/W4/W5/W6/W7 至少各有 1 个可复跑样例。
- `examples` 与文档站形成稳定的新用户入口，不依赖内部背景文档。
- 保持“诚实降级”原则：云、硬件、闭源二进制相关项继续 `n/a` 或 `partial+caveat`。
