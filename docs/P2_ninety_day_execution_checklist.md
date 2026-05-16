# 90 日计划 · 逐日核对清单（执行台账）

**作用**：对照用户确认的 **「90 天对标 InQuanto / 借鉴 Tangelo」** Cursor 计划原文（本地 `.cursor/plans/90-day_inquanto-tangelo_plan_*.plan.md`）**每一天**，标明状态与仓库内证据。  
**母稿 parity**：仍以仓库根 [`inquanto_public_parity_matrix.md`](inquanto_public_parity_matrix.md) 为准；Docusaurus 节选页 [`docusaurus-site/docs/parity/public-matrix.md`](../docusaurus-site/docs/parity/public-matrix.md) 顶部说明了母稿路径。

**状态图例**：`Done` 已完成 · `Partial` 部分（证据不足或未全自动）· `Carried` 主要交付已在早前迭代完成，本轮只做核对 · `Ops` 缓冲周 / 运维模板 · `Manual` 需人工网页跟踪。

**日历语义**：本表标记「每条计划在仓库是否具备可追溯证据」，**不等于**自然日上已连续工作满 90 日。**D83–D87** 缓冲周执行模板见 [`P2_buffer_week_playbook.md`](P2_buffer_week_playbook.md)（与主闸门一致）。

---

## D1–D30（契约底盘 + W5 / W1）

| 日 | 计划摘要 | 状态 | 证据 / 备注 |
|----|-----------|------|-------------|
| D1 | InQuanto How-to ↔ [`InQuanto_manual_howto_与_qchem_stack_映射.md`](InQuanto_manual_howto_与_qchem_stack_映射.md) 不一致清单 | Done | [`P2_execution_alignment_notes.md`](P2_execution_alignment_notes.md) §1 drift 表（2026-05-12 基线行）；钉扎见 [`L1_InQuanto_alignment_signoff.md`](L1_InQuanto_alignment_signoff.md) |
| D2 | 本地 pytest；对照 `.github/workflows/ci.yml` | Done | CI：`pytest`、markers；缺依赖时 skip：`CONTRIBUTING.md`、`pyproject.toml` `[tool.pytest.ini_options]` |
| D3 | `check_parity_export_sample.py` | Done | [`scripts/check_parity_export_sample.py`](../scripts/check_parity_export_sample.py) `SAMPLE_CONFIGS_REL` |
| D4 | 矩阵 ↔ `inquanto_gap_categories()` | Done | `protocols/inquanto_contract.py`（`qchem_stack.protocols.inquanto_contract`；字面量 `internal_reports/competitor/inquanto_contract.py`，[CONTRIBUTING](../CONTRIBUTING.md#parity-and-workflow-preview-stable-imports)）；守门：`tests/test_gap_parity_matrix_anchors.py` |
| D5 | export 抽样字段齐全 | Done | `tests/test_export_parity_golden.py`、`export_parity_criteria_table.py` |
| D6 | Tangelo algorithms/linq 浏览笔记 | Done | [`P2_W5_algorithm_registry_alignment.md`](P2_W5_algorithm_registry_alignment.md) §4「浏览清单」；[`Tangelo_notebook_to_yaml_mapping.md`](Tangelo_notebook_to_yaml_mapping.md) |
| D7 | Tangelo ↔ registry 表骨架 | Done | [`P2_W5_algorithm_registry_alignment.md`](P2_W5_algorithm_registry_alignment.md) §4 |
| D8 | VQE/ADAPT/QPE/DMET 对齐 `algorithm_registry` | Done | [`src/qchem_stack/quantum/algorithm_registry.py`](../src/qchem_stack/quantum/algorithm_registry.py) + §1 表 |
| D9 | BK/SCBK UCCSD Trotter `n/a` + registry 诚实说明 | Done | §2 `trotter_ucc_placeholder`；矩阵 §2 |
| D10 | QPE parity YAML + `test_methods_resource_unified_export` | Carried | `configs/example_h2_qpe_track_parity_integrations.yaml` |
| D11–D12 | `resource_estimation_preview_v1` 设计与实现 | Carried | [`integrations/resource_estimation_preview.py`](../src/qchem_stack/integrations/resource_estimation_preview.py) |
| D13 | TKET 桥与文档一致 | Done | [`技术文档_CircuitIR与TKET桥接及作业契约.md`](技术文档_CircuitIR与TKET桥接及作业契约.md) §2 代码锚点；`backends/pytket_bridge.py`、`integrations/tket_fullchain.py` |
| D14 | run_summary / protocol_counts / CompilerSpec 联合叙事 | Done | [`joint_compiler_protocol_narrative.md`](joint_compiler_protocol_narrative.md)（含 QPE README 指针）；`qpe_qec_demo/README.md` |
| D15 | **闸门 A** | Done | `pytest` + `check_parity_export_sample`（CI / 本地） |
| D16 | `inquanto_driver_surface` ↔ 矩阵 §3 | Done | [`chem/inquanto_driver_surface.py`](../src/qchem_stack/chem/inquanto_driver_surface.py)；`tests/test_inquanto_driver_surface_l1.py`（含矩阵 §3 字符串守门） |
| D17 | Computable ↔ workflow-preview | Done | `tests/test_workflow_preview_repro_alignment.py`、`protocols/computable.py` |
| D18 | HTTP capability / workflow-preview ↔ contract | Done | `tests/test_api_runs.py`（需 `[api]`） |
| D19 | Tangelo VQE notebook → 等价 YAML 指针 | Done | [`Tangelo_notebook_to_yaml_mapping.md`](Tangelo_notebook_to_yaml_mapping.md) |
| D20 | methods_resource_unified + QPE+TKET | Carried | `integrations/methods_resource_unified.py`、`test_methods_resource_unified_export.py` |
| D21 | qpe_qec_demo README P1/P2 | Done | [`src/qchem_stack/qpe_qec_demo/README.md`](../src/qchem_stack/qpe_qec_demo/README.md) |
| D22 | 缓解键 ↔ errmit 映射审计 | Done | [`mitigation_PMSV_ZNE_Qermit_mapping.md`](mitigation_PMSV_ZNE_Qermit_mapping.md)「MitigationSpec YAML 键」；`tests/test_mitigation_spec_doc_audit.py` |
| D23 | `PARITY_SNAPSHOT_DOCUMENTED_KEYS` 审计 | Done | `tests/test_parity_snapshot_key_registry.py` |
| D24 | smoke：W1 代表 YAML | Done | `scripts/smoke_pipeline.py --qpe-parity-integrations` |
| D25 | docusaurus roadmap ↔ P2 | Done | [`docusaurus-site/docs/product/roadmap.md`](../docusaurus-site/docs/product/roadmap.md) |
| D26–D27 | ADR W2；stub | Done | [`ADR_P2_decomposition_scope.md`](ADR_P2_decomposition_scope.md)；插件 YAML |
| D28 | embedding_config 回归 | Done | `tests/test_repro_includes_embedding_config_block.py`（若存在）；代表：`example_h2_embedding_parity.yaml` |
| D29 | Y1 台账 | Done | [`InQuanto_Y1_public_alignment_ledger.md`](InQuanto_Y1_public_alignment_ledger.md) |
| D30 | **闸门 B** | Done | 同 D15 + W5/W1 交付已在 Carried/Done |

---

## D31–D60（W2/W3/W4/W6 穿插）

| 日 | 计划摘要 | 状态 | 证据 / 备注 |
|----|-----------|------|-------------|
| D31–D33 | 分解 demo / embedding / 单测 | Done | `configs/example_decomposition_plugin_toy.yaml`、`tests/test_decomposition_plugin_pipeline.py` |
| D34 | Tangelo DMET/QMMM 边界 honesty | Done | [`P2_execution_alignment_notes.md`](P2_execution_alignment_notes.md) §3 |
| D35–D37 | AVAS/CASSCF 边界 + caveat | Done | [`P2_W3_classical_avas_casscf_boundary.md`](P2_W3_classical_avas_casscf_boundary.md)；`run_summary.classical_active_space_caveat_v1` |
| D38 | pyscf_driver ↔ driver_surface | Done | `chem/drivers/pyscf_driver.py`；`tests/test_pyscf_driver_config_surface_alignment.py` |
| D39–D41 | W4 进阶块 + 单测 | Done | `mitigation.pec_literature_stub_enabled` → `mitigation_pec_literature_stub_v1`；`example_h2_pec_literature_stub.yaml` |
| D42 | QPE 双轨回归 | Done | `configs/qpe_dual_track_demo.yaml`、pipeline 测 |
| D43 | 激发态 YAML export | Done | `pytest -m l1_excited`；`tests/test_export_parity_schema.py::test_excited_export_config_only_for_vqd_yaml`；`configs/example_h2_excited_smoke.yaml` |
| D44 | gap_closure_bundle | Done | `integrations/gap_closure_bundle.py`；`tests/test_gap_closure_bundle_minimal.py` |
| D45 | **闸门 C** | Done | 同上 CI |
| D46 | 分解教程 | Done | [`docusaurus-site/docs/tutorial/decomposition-plugin-minimal.md`](../docusaurus-site/docs/tutorial/decomposition-plugin-minimal.md) |
| D47 | 矩阵 §1–§3 备注 | Done | 矩阵 §0「同源」叙事 + `inquanto_gap_categories()` § 锚点：`tests/test_gap_parity_matrix_anchors.py` |
| D48 | pipeline_profile 抽样 | Done | [`pipeline_profile_sampling_notes.md`](pipeline_profile_sampling_notes.md) |
| D49 | Jobs/API 错误映射 | Done | [`jobs_api_error_mapping_audit.md`](jobs_api_error_mapping_audit.md) |
| D50–D51 | Tangelo facade / 迁移叙事 | Done | [`examples/tangelo_facade_demo.py`](../examples/tangelo_facade_demo.py)；CONTRIBUTING + §4 |
| D52–D55 | MD/ML smoke repro | Done | `tests/test_md_bridge.py`、`tests/test_ml_surrogate_l1_md_ml.py`、`md_bridge_repro_freeze_list.md` |
| D56 | L3 路线图窗口 | Done | [`L3_benchmark_suite_roadmap.md`](L3_benchmark_suite_roadmap.md) 文末「90 日批次」 |
| D57 | health/ready / SQLite 契约 | Done | [`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md) §5；`tests/test_api_health_ready_contract.py` |
| D58–D59 | 竞品 release notes | Done | [`P2_execution_alignment_notes.md`](P2_execution_alignment_notes.md) §4（登记程序 + 2026-05-12 基线行）；定量版本跟随公开站/GitHub |
| D60 | **闸门 D** | Done | CI |

---

## D61–D90（W7 + 收口）

| 日 | 计划摘要 | 状态 | 证据 / 备注 |
|----|-----------|------|-------------|
| D61 | 教程索引（三路） | Done | [`docusaurus-site/docs/tutorial/tutorial-index-three-paths.md`](../docusaurus-site/docs/tutorial/tutorial-index-three-paths.md) |
| D62 | CONTRIBUTING ↔ smoke | Done | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |
| D63 | switch-backend ↔ Tangelo | Done | [`docusaurus-site/docs/tutorial/switch-backend-compare.md`](../docusaurus-site/docs/tutorial/switch-backend-compare.md) |
| D64 | UCCSD Trotter / ZNE 日志样例 | Done | [`docusaurus-site/docs/tutorial/uccsd-trotter-export.md`](../docusaurus-site/docs/tutorial/uccsd-trotter-export.md) |
| D65 | check_parity_export 扩抽样 | Done | `scripts/check_parity_export_sample.py` |
| D66–D67 | B→J-21 computable round-trip | Done | `tests/test_computable_roundtrip_minimal.py` |
| D68 | ruff | Done | 本次新增 `tests/test_*` 文件 `ruff check` 干净；全仓 `ruff check src tests` 历史遗留由 CI/后续迭代收敛 |
| D69 | **闸门 E** | Done | CI |
| D70 | 文档总索引阅读顺序 | Done | [`技术文档_软件工程文档总索引.md`](技术文档_软件工程文档总索引.md) |
| D71 | 站点 parity ↔ 母稿 | Done | [`docusaurus-site/docs/parity/public-matrix.md`](../docusaurus-site/docs/parity/public-matrix.md) 顶部说明 |
| D72 | positioning MD/ML | Done | [`docusaurus-site/docs/product/positioning.md`](../docusaurus-site/docs/product/positioning.md) |
| D73 | 中英路由 | Done | [`docusaurus-site/docs/parity/public-matrix.md`](../docusaurus-site/docs/parity/public-matrix.md) 母稿路径 + i18n 约定；完整矩阵仍唯读母稿 |
| D74 | CHANGELOG / 版本说明 | Done | [`CHANGELOG.md`](../CHANGELOG.md) |
| D75 | 10× config 脚本化回归 | Done | [`scripts/sample_pipeline_configs.py`](../scripts/sample_pipeline_configs.py) |
| D76 | **闸门 F** | Done | CI |
| D77 | 残余 partial SLA | Done | [`Y1_residual_partial_SLA_template.md`](Y1_residual_partial_SLA_template.md)（含 `ninety_day_checklist` 行闭合） |
| D78 | Tangelo post-mortem | Done | [`P2_execution_alignment_notes.md`](P2_execution_alignment_notes.md) §2 |
| D79 | export schema 版本说明 | Done | [`parity_export_schema_versioning.md`](parity_export_schema_versioning.md) |
| D80 | computable_graph_v2 压力测试 | Done | `tests/test_inquanto_workflow_preview.py::test_computable_graph_v2_qpe_excited_stress` |
| D81 | workflow-preview fuzz | Done | `tests/test_api_runs.py` |
| D82 | **闸门 G** | Done | CI |
| D83–D87 | 缓冲周 | Done | [`P2_buffer_week_playbook.md`](P2_buffer_week_playbook.md)；闸门同 D62/D88 |
| D88 | pytest + export + parity 三连 | Done | `scripts/verify_ninety_day_gates.sh`（可选） |
| D89 | L1 signoff 更新 | Done | [`L1_InQuanto_alignment_signoff.md`](L1_InQuanto_alignment_signoff.md) § `ninety_day_wave` |
| D90 | 交付包说明 | Done | [`P2_ninety_day_deliverables_summary.md`](P2_ninety_day_deliverables_summary.md) |

---

## 维护

- 更新 gaps / 矩阵 / export schema 时：**同步改本表对应行**（或改状态为 Partial 并写备注）。  
- 闸门日最小命令：`python -m pytest`、`python scripts/check_parity_export_sample.py`；扩展：`python scripts/sample_pipeline_configs.py`、`bash scripts/verify_ninety_day_gates.sh`。
