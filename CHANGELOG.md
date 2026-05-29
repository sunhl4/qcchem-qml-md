# Changelog

All notable changes to this project are documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning** intent for the Python package (`pyproject.toml`).

## [0.3.0] - 2026-05-28

### Added (P4 competitor gap closure)

- **Ansatz**: UpCCGSD, pUCCD, iQCC, QITE; UCCGD/UpCCGSD/pUCCD Pauli protocol paths; staggered operator pool `fermionic_singles_doubles_staggered`.
- **Backends**: Braket and Cirq HEA executors with conformance tests.
- **Mitigation**: SPAM 2-qubit calibration, Richardson ZNE extrapolation, classical-shadows main-path runtime; local `jobs/mitigation_queue.py`.
- **Embedding**: PySCF density-feedback DMET bath hook; ONIOM three-layer MM energy; MI-FNO precomputed fragment sidecar plugin.
- **MD/ML**: `science_kpi_met` / `max_abs_delta_hartree` in validation summary; 5-round AL test path.
- **Ecosystem**: `examples/tutorial_06_http_client.py`; bilingual examples index; optional notebook CI script; v0.3.0 parity doc sync (Phase I–L backlog).

## [Unreleased]

### Deprecated (removal timelines — no runtime break this release)

| Surface | Status | Planned removal |
|---------|--------|-----------------|
| `chem.drivers.PySCFDriver` (`chem/drivers/pyscf_driver.py`) | Deprecated; use `ChemIntegralSolver` + `scf.driver` registry | **v0.5.0** (target 2026 Q3) |
| `qchem_stack.ml` (Ridge surrogate toy) | Non-production; use `md_bridge` for MD/ML loops | **v0.5.0** |
| `qchem_stack.integrations.*` re-export shims (DMET, UCC reference, Schmidt sidecars) | Compatibility aliases; import from `chem` / `quantum` instead | **v0.6.0** |

See `docs/迁移指南_PySCFDriver到ChemIntegralSolver.md` for the PySCF driver migration path.

### Added

- **Docs**: UQC/MD-ML/Psi4 Docusaurus pages; `configs/README.md`, `configs/_template.yaml`; `docs/迁移指南_PySCFDriver到ChemIntegralSolver.md`; `docs/说明_mitigation配置.md`, `docs/说明_md_ml_export配置.md`; `docs/QUICKSTART_HTTP_API_en.md`; `docs/算法面广度_Vendor platform_Tangelo对照索引.md` alias; `docusaurus-site/docs/parity/gap-implementation-plan.md`.
- **Tests**: `tests/test_uqc_backend_units.py`, `tests/test_protocol_counts_and_build_cache.py`; shared `tests/helpers/h2_yaml.py`; `l1_excited` markers on excited plugin tests.
- **Scripts**: `scripts/check_import_layers.py`; CI import-layer + coverage artifact + nightly job scaffold.
- **API**: `POST /v1/runs/sync` (deprecated); `Deprecation` header when `sync: true` on `POST /v1/runs`.

### Changed

- **Refactor**: Split `quantum_helpers`, `product_contract`, `qmlff_adapter`, `md_validation_loop`, `embedding_strategies` into submodules with re-export shims.
- **CI**: Default pytest excludes `slow` and `perf`; Psi4 job blocking; smoke pipeline `QCHEM_SMOKE_REQUIRE_PYSCF=1` in CI.
- **API**: Default CORS origins `127.0.0.1:3000/8000` (override via `QCHEM_STACK_CORS_ORIGINS`).
- **Docs**: HTTP API docs synced to `product-surface` / `capability_surface_v2`; YAML path `quantum.variational.uccsd_trotter_steps`; machine path placeholders → `$QCHEM_REPO` / `$QMLFF_ROOT`.
- **ml/**: Module docstring clarifies toy scope vs `md_bridge` production loop.

### Notes

- **Export schema** top-level `parity_export_schema_version` remains **`"2"`** until a breaking exporter change is merged (`docs/parity_export_schema_versioning.md`).

### Added (prior unreleased entries)

- **Docs**: `docs/P2_ninety_day_execution_checklist.md`（D1–D90 逐日核对台账）；`docs/P2_ninety_day_deliverables_summary.md`；`docs/Tangelo_notebook_to_yaml_mapping.md`；`docs/joint_compiler_protocol_narrative.md`；`docs/pipeline_profile_sampling_notes.md`；`docs/jobs_api_error_mapping_audit.md`；`docs/parity_export_schema_versioning.md`.
- **Scripts**: `scripts/sample_pipeline_configs.py`（抽样 10× YAML export / 可选全管线）；`scripts/verify_ninety_day_gates.sh`（pytest + parity export 抽样）；`scripts/smoke_pipeline.py --qpe-parity-integrations`.
- **Config**: `configs/example_h2_pec_literature_stub.yaml`（PEC 文献占位）。
- **Tests**: `tests/test_computable_roundtrip_minimal.py`; `tests/test_ml_surrogate_l1_md_ml.py`; `tests/test_examples_tangelo_facade.py`; workflow-preview HTTP error-path tests; computable graph stress coverage.

### Changed

- **Repro**: `run_summary.classical_active_space_caveat_v1`（经典活性空间诚实边界）；`parity_snapshot.mitigation_pec_literature_stub_v1`（可选 YAML）。
- **Docs sites**: Docusaurus tutorial index + decomposition minimal page; roadmap / positioning updates.

### Notes

- **Export schema** top-level `parity_export_schema_version` remains **`"2"`** until a breaking exporter change is merged (`docs/parity_export_schema_versioning.md`).
