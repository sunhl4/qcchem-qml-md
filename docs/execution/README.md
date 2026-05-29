# Execution Log Index (2026Q2-Q3)

本目录记录 P2 连续执行证据链（按天与里程碑）。

**产品 export / gap 机读契约与 `workflow-preview` 维护入口**：见仓库根目录 [CONTRIBUTING.md — Product contracts and workflow-preview](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)。

**工程深度总览（维度 × WBS × 闸门）**：以 `docs/execution/comparative_execution_rd_plan_strict_2026Q3Q4.md` 与仓库根目录 `CONTRIBUTING.md` 为入口（历史独立 roadmap 文档已合并/下线）。

## Day logs (archived)

Historical day-by-day execution evidence lives under **`archive/`** (moved from this directory to reduce root sprawl). Examples:

- `archive/day01_gap_inventory_2026Q2.md`
- `archive/day02_export_keys_audit_2026Q2.md` … through `archive/day12_plugin_export_contract_alignment_2026Q2.md`

## Milestones (archived)

- `archive/day25_w2_milestone_closeout_2026Q2.md` … `archive/day90_final_closeout_2026Q2.md`
- `archive/day090_tangelo_calendar_closeout.md` — Tangelo gap 日历（Day1–Day90）封板
- `archive/month1_baseline_signoff_2026Q2.md`, `archive/week1_regression_report_2026Q2.md`

## Tangelo / Vendor platform gap calendar (Day1–Day90)

- `archive/day001_day090_tangelo_gap_calendar.md`

## Unified classical chemistry interface (Day1–Day90)

- `archive/day001_day090_unified_chemistry_interface_calendar.md`
- `unified_chem_driver_audit_notes.md` — `scf.driver` / PySCF 在编排层出现点的审计台账。
- `unified_chem_capabilities_matrix.md` — embedding/hamiltonian 分支与 `SolverCapabilities` 对照矩阵。
- `dual_classical_ingress_acceptance_checklist_2026Q2.md` — 双线路经典输入（在线结构文件 + 离线 bundle）统一 `PreQuantumInput` 验收勾选表。
- `week_unified_chem_w01.md` … `week_unified_chem_w13.md` — 每周交付与闸门执行记录骨架。
- `psi4_get_integrals_design.md` — Psi4 `get_integrals` 返回形状草案。
- `subprocess_chem_risk_checklist.md` — subprocess adapter 许可证/协议风险清单。
- `day090_unified_chemistry_interface_closeout.md` — 封板清单（已勾选，2026-05-08）。

## Next phase (Day91+)

- `day91_next_phase_plan_2026Q3.md`
- `day91_day120_daily_breakdown_2026Q3.md`
- `day120_gate_checklist_2026Q3.md`

## Comparative execution sprint (Day121–Day180, 历史命名)

- 逐日日历与 kickoff/signoff 的 **历史第三方品牌文件名版本已删除**；请只使用：
- `comparative_execution_rd_plan_strict_2026Q3Q4.md` — 对比研发计划（严格实施版）
- `comparative_execution_backlog.yaml` — 机器可校验任务台账

### Strict execution tooling

- `scripts/check_comparative_execution_backlog.py` — 台账结构与完成证据校验脚本（在 CI/本地对 `comparative_execution_backlog.yaml` 运行）

## Full P0–P3 master plan (Day181–Day450)

- [`inquanto_tangelo_p0_p3_master_plan_2026Q3Q4.md`](inquanto_tangelo_p0_p3_master_plan_2026Q3Q4.md) — InQuanto/Tangelo 对标全量 WBS
- [`day210_p0_closeout.md`](day210_p0_closeout.md) — Phase D (P0) 封板
- [`day450_p3_closeout.md`](day450_p3_closeout.md) — Phase H (P3) 封板
- `comparative_execution_backlog.yaml` Phase **D–H** — 全部 `done`（2026-05-28）

### Day91-Day97 templates

- `day91_template_2026Q3.md`
- `day92_template_2026Q3.md`
- `day93_template_2026Q3.md`
- `day94_template_2026Q3.md`
- `day95_template_2026Q3.md`
- `day96_template_2026Q3.md`
- `day97_template_2026Q3.md`
