# Changelog

All notable changes to this project are documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning** intent for the Python package (`pyproject.toml`).

## [Unreleased]

### Added

- **Docs**: `docs/P2_ninety_day_execution_checklist.md`（D1–D90 逐日核对台账）；`docs/P2_ninety_day_deliverables_summary.md`；`docs/Tangelo_notebook_to_yaml_mapping.md`；`docs/joint_compiler_protocol_narrative.md`；`docs/pipeline_profile_sampling_notes.md`；`docs/jobs_api_error_mapping_audit.md`；`docs/parity_export_schema_versioning.md`.
- **Scripts**: `scripts/sample_pipeline_configs.py`（抽样 10× YAML export / 可选全管线）；`scripts/verify_ninety_day_gates.sh`（pytest + parity export 抽样）；`scripts/smoke_pipeline.py --qpe-parity-integrations`.
- **Config**: `configs/example_h2_pec_literature_stub.yaml`（PEC 文献占位）。
- **Tests**: `tests/test_computable_roundtrip_minimal.py`; `tests/test_ml_surrogate_l1_md_ml.py`; `tests/test_examples_tangelo_facade.py`; workflow-preview HTTP error-path tests; computable graph stress coverage.

### Changed

- **Repro**: `run_summary.classical_active_space_caveat_v1`（经典活性空间诚实边界）；`parity_snapshot.mitigation_pec_literature_stub_v1`（可选 YAML）。
- **Docs sites**: Docusaurus tutorial index + decomposition minimal page; roadmap / positioning updates.

### Notes

- **Export schema** top-level `parity_export_schema_version` remains **`"2"`** until a breaking exporter change is merged (`docs/parity_export_schema_versioning.md`).
