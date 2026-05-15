# Execution Log Index (2026Q2-Q3)

本目录记录 P2 连续执行证据链（按天与里程碑）。

**工程深度总览（维度 × WBS × 闸门）**：[工程深度路线图_InQuanto_Tangelo_对标与交付.md](../工程深度路线图_InQuanto_Tangelo_对标与交付.md) — 与 InQuanto / Tangelo 公开叙事可对标的完整计划母页，承接差距文档附录与下列 Day 日志。

## Day logs

- `day01_gap_inventory_2026Q2.md`
- `day02_export_keys_audit_2026Q2.md`
- `day03_resource_preview_consistency_2026Q2.md`
- `day04_resource_preview_docs_sync_2026Q2.md`
- `day05_sample_coverage_and_stability_2026Q2.md`
- `day06_regression_and_naming_2026Q2.md`
- `day07_week1_closeout_2026Q2.md`
- `day08_p2w2_plugin_slice_2026Q2.md`
- `day09_plugin_schema_validation_2026Q2.md`
- `day10_plugin_pipeline_chain_2026Q2.md`
- `day12_plugin_export_contract_alignment_2026Q2.md`

## Milestones

- `day25_w2_milestone_closeout_2026Q2.md`
- `day45_w3_w4_stage_report_2026Q2.md`
- `day65_w5_w6_stage_report_2026Q2.md`
- `day80_w7_pre_signoff_2026Q2.md`
- `day90_final_closeout_2026Q2.md`
- `day090_tangelo_calendar_closeout.md` — Tangelo gap 日历（Day1–Day90）封板签字与闸门对照
- `month1_baseline_signoff_2026Q2.md`
- `week1_regression_report_2026Q2.md`

## Tangelo / InQuanto gap calendar (Day1–Day90)

- `day001_day090_tangelo_gap_calendar.md` — 三个月逐日台账（差距收口 + Tangelo 设计参考），含周闸门与 Day90 封板指针。

## Unified classical chemistry interface (Day1–Day90)

- `day001_day090_unified_chemistry_interface_calendar.md` — **统一 `ChemIntegralSolver` 入口、多程序适配、下游与 PySCF 解耦** 的 90 天逐日日历（与 `docs/统一经典化学接口_ChemIntegralSolver与下游无关性.md` 配套）。
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

## InQuanto / Tangelo reconciliation sprint (Day121–Day180, 60 days)

- `day121_day180_inquanto_tangelo_calendar_2026Q3.md` — 矩阵 × Tangelo 广度索引 × `capability_surface` 同源链，逐日 60 行日历 + 周闸门
- `day121_kickoff_inquanto_tangelo_reconciliation_2026Q3.md` — Day121 启动（填 `PLAN_START_DATE`、锚点缺口表）
- `day180_signoff_inquanto_tangelo_2026Q3.md` — Day180 封板勾选（周期末填写）
- `inquanto_tangelo_comparative_rd_plan_strict_2026Q3Q4.md` — 对比研发计划（严格实施版，含外部证据与阶段闸门）
- `inquanto_tangelo_comparative_backlog.yaml` — 机器可校验任务台账（任务级路径/测试/验收标准/证据）

### Strict execution tooling

- `scripts/check_inquanto_tangelo_comparative_backlog.py` — 台账结构与完成证据校验脚本
- `tests/test_check_inquanto_tangelo_comparative_backlog_script.py` — 脚本回归测试（含负例）

### Day91-Day97 templates

- `day91_template_2026Q3.md`
- `day92_template_2026Q3.md`
- `day93_template_2026Q3.md`
- `day94_template_2026Q3.md`
- `day95_template_2026Q3.md`
- `day96_template_2026Q3.md`
- `day97_template_2026Q3.md`
