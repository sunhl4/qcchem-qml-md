# Changelog

All notable changes to this project are documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning** intent for the Python package (`pyproject.toml`).

## [0.6.0] - 2026-06-03

### Added

- **P0–P4 verification wave**: config scenario picker (`qchem_stack.config.scenarios`, `qchem-run --list-scenarios`), expanded SDK facade, Binder environment, backend×mapping conformance matrix tests.
- UQC backend compatibility shims under `qchem_stack.backends.uqc_*` (optional `packages/qchem-stack-uqc` plugin).
- Mitigation queue `drain_all` E2E test; resource estimation preview depth proxies (`ft_total_measurement_shots_proxy`, `ft_t_gate_count_proxy`).
- Docusaurus: CASSCF audit workflow page; expanded PyPI README.

### Fixed

- OpenFermion 1.7+ compatibility in `spatial_restricted_fermion` (term-by-term construction, int indices).

### Changed

- `driver_surface_breadth` gap caveat documents ORCA/Gaussian non-goals explicitly.

## [Unreleased]

### Added

- Console scripts **`qchem-run`** and **`qchem-export-parity`**; stable integrator facade **`qchem_stack.sdk`**.
- Docker **slim** / **full** build targets; **`python -m qchem_stack.api`** entry for Compose.
- CI **`contract-gate`** job and **`test-cross-platform`** (main/schedule); PR matrix Ubuntu-only with **pytest-xdist**.
- Scripts: `generate_parity_gap_snippet.py`, `check_config_combo_matrix.py`; generated `docs/generated/parity_gap_snippet.md`.
- Resource estimation preview fields: `mitigation_zne_scale_count_yaml`, `mitigation_zne_richardson_order_yaml`.

### Changed

- **`results/`** removed from git tracking (local outputs only; see `results/README.md`).
- Per-package coverage floors: **quantum/backends/chem 70%**, **mitigation 65%**.
- Pyright **`reportMissingParameterType`** for **`backends`** and **`jobs`** packages.
- Execution closeout docs archived under **`docs/execution/archive/2026Q2/`**.

### Deprecated

- **`qchem_stack.integrations.dmet_self_consistent`** import path (use **`chem.embedding.dmet_self_consistent`**); removal **v0.8.0** (see `docs/engineering/api_stability_policy.md`).

### Removed

- Root **`opus4.8-test.md`** agent session artifact.

## [0.3.0] - 2026-05-28

### Added (P4 competitor gap closure)

- **Ansatz**: UpCCGSD, pUCCD, iQCC, QITE; UCCGD/UpCCGSD/pUCCD Pauli protocol paths; staggered operator pool `fermionic_singles_doubles_staggered`.
- **Backends**: Braket and Cirq HEA executors with conformance tests.
- **Mitigation**: SPAM 2-qubit calibration, Richardson ZNE extrapolation, classical-shadows main-path runtime; local `jobs/mitigation_queue.py`.
- **Embedding**: PySCF density-feedback DMET bath hook; ONIOM three-layer MM energy; MI-FNO precomputed fragment sidecar plugin.
- **MD/ML**: `science_kpi_met` / `max_abs_delta_hartree` in validation summary; 5-round AL test path.
- **Ecosystem**: `examples/tutorial_06_http_client.py`; bilingual examples index; optional notebook CI script; v0.3.0 parity doc sync (Phase I–L backlog).

## [0.6.0] - 2026-05-29

### Added

- **`config/experiment_profiles.py`** and `configs/profiles/{minimal,research,production}_h2.yaml`.
- **`LocalMitigationJobQueue.drain_all`** for in-process async mitigation batches.
- Pipeline profile rendering in benchmark dashboard (`--pipeline-profile`).
- Doc tier policy, doc link CI, API YAML body size limit (512 KiB), expanded `README_PYPI.md`.
- `examples/tutorial_07_md_classical_h2_only.py` (no QML-FF dependency).

### Changed

- ML ridge/discrete-pool stubs moved to **`md_bridge.active_learning`**.
- **`QubitHamiltonianFragmentSolverVQE`** under **`chem.embedding.fragment_solvers`**.
- RDM correction glue imports from **`chem.kernels.rdm_corrections`** (not integrations shim).

### Removed

- **`PySCFDriver`** (`chem/drivers/pyscf_driver.py`).
- **`qchem_stack.ml`** package.
- Integrations shims: `schmidt_dmet_self_consistent`, `ucc_reference`, `dmet_fragment_solvers`, `integrations/rdm_corrections`.
- **`POST /v1/runs/sync`** route; use `POST /v1/runs` + poll.
- Duplicate **`qchem-pipeline-worker`** console script (use `qchem-jobs-worker`).

## [0.4.1] - 2026-05-29

### Added

- Cross-backend `get_integrals` parity tests; `uccsd_scbk_trotter_circuit` product-contract gap row.

## [0.4.0] - 2026-05-29

### Added

- **`tests/orchestration/test_stage_execution.py`**: mocked SCF / pre-quantum stage unit tests.
- **`scripts/check_coverage_thresholds.py`**: per-package coverage gates (CI Python 3.12).
- Extended jobs concurrency and 5-round MD/ML regression tests.

## [0.3.1] - 2026-05-29

### Added

- **`scripts/bootstrap_dev.sh`**: one-command `.venv` + `[dev]` install + precomputed smoke.
- **`tests/helpers/h2_yaml.py`**: `h2_yaml_with` / `write_h2_config`; broader test DRY adoption.
- **`tests/orchestration/test_orchestration_packaged_configs.py`**: split packaged YAML smokes.

### Changed

- **`scripts/venv-run`**: prefers repo `.venv/bin/python` when `QCHEM_STACK_PYTHON` is unset.

## [Unreleased]

### Notes

- See **[0.6.0]** for breaking removals (PySCFDriver, `ml/`, integrations shims, sync route).

- **UQC**: `circuit_scale_fold` multi-scale cloud submissions (`uqc_zne_fold.py`); ZNE `energy_stub` post-processing.
- **PyPI**: `README_PYPI.md`, `docs/engineering/pypi_release.md`, `.github/workflows/publish-pypi.yml` (OIDC).
- **Types**: `QmefFramePayload`, `QmefDatasetPayload` in `md_bridge.from_pipeline`.
- **Docs**: UQC/MD-ML/Psi4 Docusaurus pages; `configs/README.md`, `configs/_template.yaml`; `docs/迁移指南_PySCFDriver到ChemIntegralSolver.md`; `docs/说明_mitigation配置.md`, `docs/说明_md_ml_export配置.md`; `docs/QUICKSTART_HTTP_API_en.md`; `docs/算法面广度_Vendor platform_Tangelo对照索引.md` alias; `docusaurus-site/docs/parity/gap-implementation-plan.md`.
- **Tests**: `tests/test_uqc_backend_units.py`, `tests/test_protocol_counts_and_build_cache.py`; shared `tests/helpers/h2_yaml.py`; `l1_excited` markers on excited plugin tests.
- **Scripts**: `scripts/check_import_layers.py`; CI import-layer + coverage artifact + nightly job scaffold.
- **API**: `POST /v1/runs/sync` (deprecated); `Deprecation` header when `sync: true` on `POST /v1/runs`.

### Changed

- **CI**: Docusaurus `npm audit --audit-level=high` is blocking; `serialize-javascript` override.
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
