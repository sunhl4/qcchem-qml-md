# Scripts index (`scripts/`)

Utility and CI scripts for qchem-stack. Run from the repository root unless noted.

Install dev deps first: `pip install -e ".[dev]"`. Optional extras: `[chem]`, `[quantum]`, `[api]`.

## CI and quality gates

| Script | Purpose | Minimal command |
|--------|---------|-----------------|
| `check_import_layers.py` | Enforce chem/quantum → no orchestration imports | `python scripts/check_import_layers.py` |
| `check_parity_export_sample.py` | Config-only parity export on all experiment YAMLs | `python scripts/check_parity_export_sample.py` |
| `check_coverage_thresholds.py` | Per-package coverage floors (needs `htmlcov/` from pytest) | `pytest tests -q --cov=src/qchem_stack && python scripts/check_coverage_thresholds.py` |
| `check_doc_links.py` | Validate Docusaurus / docs links | `python scripts/check_doc_links.py` |
| `check_examples_importable.py` | Syntax/import check for `examples/` | `python scripts/check_examples_importable.py` |
| `check_comparative_execution_backlog.py` | Comparative execution backlog validator | `python scripts/check_comparative_execution_backlog.py` |
| `check_constraints_freshness.py` | pip-tools constraints drift | `pip install pip-tools && python scripts/check_constraints_freshness.py` |
| `check_solver_adapter_contract.py` | Solver adapter contract smoke | `python scripts/check_solver_adapter_contract.py` |
| `check_cross_solver_parity.py` | Cross-solver parity checks | `python scripts/check_cross_solver_parity.py` |
| `code_health_baseline.py` | LOC / large-file metrics | `python scripts/code_health_baseline.py` |
| `verify_ninety_day_gates.sh` | Maintainer gate bundle | `./scripts/verify_ninety_day_gates.sh` |

## Smoke and pipeline

| Script | Purpose | Minimal command | Extras |
|--------|---------|-----------------|--------|
| `smoke_pipeline.py` | End-to-end orchestration smoke | `python scripts/smoke_pipeline.py --precomputed-only` | `[chem]` for PySCF paths |
| `run_qpe_track_demo.py` | QPE dual-track demo (no PySCF) | `python scripts/run_qpe_track_demo.py` | core |
| `demo_mock_external_backend.py` | Mock external solver demo | `python scripts/demo_mock_external_backend.py` | `[chem]` |
| `minimal_pipeline_viz.py` | Minimal pipeline visualization | `python scripts/minimal_pipeline_viz.py` | core |

## Documentation sync and generation

| Script | Purpose | Minimal command |
|--------|---------|-----------------|
| `sync_pre_quantum_docs.py` | Sync pre-quantum YAML matrix docs | `python scripts/sync_pre_quantum_docs.py` |
| `generate_config_reference_snippets.py` | Regenerate `docs/generated/` snippets | `python scripts/generate_config_reference_snippets.py` |
| `generate_configs_catalog.py` | Regenerate configs catalog snippet | `python scripts/generate_configs_catalog.py` |
| `execution_doc_index.py` | Index execution docs | `python scripts/execution_doc_index.py` |

## Parity and export

| Script | Purpose | Minimal command |
|--------|---------|-----------------|
| `export_parity_criteria_table.py` | Methods-style parity export JSON | `python scripts/export_parity_criteria_table.py configs/example_h2.yaml` |
| `count_parity_matrix_main_tables.py` | Count parity matrix table rows | `python scripts/count_parity_matrix_main_tables.py` |
| `sample_pipeline_configs.py` | Sample pipeline configs helper | `python scripts/sample_pipeline_configs.py` |

## UQC and MD/ML

| Script | Purpose | Minimal command | Extras |
|--------|---------|-----------------|--------|
| `run_uqc_md_ml.py` | UQC mock + MD/ML integration runner | `python scripts/run_uqc_md_ml.py` | `[uqc]`, `[chem]` |
| `run_uqc_cloud_sim_online_learning.py` | Cloud-sim online learning loop | `python scripts/run_uqc_cloud_sim_online_learning.py` | `[uqc]` |
| `analyze_uqc_md_ml_results.py` | Analyze UQC MD/ML outputs | `python scripts/analyze_uqc_md_ml_results.py` | core |
| `compare_uqc_vqe_mock_vs_cloud.py` | Compare mock vs cloud VQE | `python scripts/compare_uqc_vqe_mock_vs_cloud.py` | `[uqc]` |
| `restore_uqc_5round_md_summary.py` | Restore 5-round MD summary fixture | `python scripts/restore_uqc_5round_md_summary.py` | core |
| `check_uqc_connectivity.py` | UQC connectivity check | `python scripts/check_uqc_connectivity.py` | `[uqc]` |

## Benchmarks and reports

| Script | Purpose | Minimal command |
|--------|---------|-----------------|
| `l3_algorithm_benchmark_report.py` | L3 algorithm benchmark JSON | `python scripts/l3_algorithm_benchmark_report.py` |
| `benchmark_dashboard/generate.py` | HTML benchmark dashboard | `python scripts/benchmark_dashboard/generate.py --input ... --output /tmp/dashboard.html` |
| `benchmark_qwen_triple.py` | Qwen triple benchmark (offline) | `python scripts/benchmark_qwen_triple.py` |
| `resource_estimation_demo.py` | Resource estimation demo | `python scripts/resource_estimation_demo.py` |
| `compare_shots_per_circuit.py` | Compare shot budgets | `python scripts/compare_shots_per_circuit.py` |
| `render_qwen_report_charts.py` | Render qwen report charts | `python scripts/render_qwen_report_charts.py` |

## Scaffolding and migration

| Script | Purpose | Minimal command |
|--------|---------|-----------------|
| `create_solver_adapter_scaffold.py` | Generate solver adapter scaffold | `python scripts/create_solver_adapter_scaffold.py` |
| `build_precomputed_bundle.py` | Build precomputed integral bundle | `python scripts/build_precomputed_bundle.py` |
| `migrate_job_protocol_blobs.py` | Migrate job protocol blobs | `python scripts/migrate_job_protocol_blobs.py` |
| `backend_profile_helpers.py` | Backend profile helpers | `python scripts/backend_profile_helpers.py` |
| `integration_checklist.py` | Integration checklist runner | `python scripts/integration_checklist.py` |

## Dev environment

| Script | Purpose |
|--------|---------|
| `venv-run` | Run commands with maintainer Python (`QCHEM_STACK_PYTHON`) |
| `bootstrap_dev.sh` | Bootstrap dev environment |
| `update_constraints.py` | Update pip constraints |
| `normalize_repo_text_utf8.py` | Normalize repo text encoding |
| `setup_psi4_micromamba.sh` | Psi4 micromamba env (CI/local) |
| `release_precheck.sh` | Pre-release quality gate bundle |
| `check_notebooks_smoke.py` | Notebook smoke helper |

See also [CONTRIBUTING.md](../CONTRIBUTING.md) and [docs/backends.md](../docs/backends.md).
