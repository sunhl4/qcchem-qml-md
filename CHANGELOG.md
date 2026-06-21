# Changelog

All notable changes to this project are documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning** intent for the Python package (`pyproject.toml`).

## [Unreleased]

## [1.1.0] - 2026-06-15

### Added

- Bundled configs: `config_paths.default_configs_dir()`; wheel installs YAMLs under `share/qchem-stack/configs`.
- GitHub Pages docs deployment (`deploy-docs.yml`); `SECURITY.md`, `CITATION.cff`, `CODE_OF_CONDUCT.md`.
- **Release hardening**: `scripts/check_doc_test_paths.py` (Tier-1 fail); expanded `release_precheck.sh` (pyright config slice, pip-audit, contract-docs sync); per-package coverage floors aligned to measured baseline (`jobs` 62%, `md_bridge` 69%).
- **Types & export**: `protocols/parity_export_types.py`; Pyright `reportAny=error` on all core packages; `dict[str, Any]` density regression gate for `protocols/`.
- **Jobs & observability**: Postgres protocol conformance CI; OTel docker-compose example (`examples/observability/docker-compose.otlp.yaml`); config validation `Suggestion:` hints for DMET/RHF.
- **P0–P3 waves (carry-over)**: reusable CI workflows; `WorkerJobStore` / `PostgresJobStore`; config v3 scenario MVP; pipeline JSON schema snapshots; role-based onboarding; production deployment checklist.

### Removed

- `qchem_stack.integrations.compat.*` re-export shims — use `chem.embedding.dmet_self_consistent`, `integrations.schmidt_per_fragment_vqe`, `chem.kernels.spin_ucc`.

### Changed

- Legacy unsigned pickle protocol blobs **disabled by default** (`JobPayloadError`); migration via `scripts/migrate_job_protocol_blobs.py` with temporary `QCHEM_ALLOW_LEGACY_PICKLE=1`.
- `release_precheck.sh` aligned with CI lint/contract-docs/security gates; default skips full-stack pyright (opt-in `QCHEM_PYRIGHT_FULL=1` for 1.2 debt); L3/nbmake use `--no-cov`; `run_all_smoke.py` skips jax tutorial without `[qmlff]`.
- Per-package coverage floors for `integrations` (60%), `contracts` and `sdk` (75%).
- Tests live under layer subdirectories only (`tests/<layer>/`); contributor docs remapped via `check_doc_test_paths.py --fix`.

### Security

- `security.yml` audits both `dev` and `chem,api` install surfaces with `pip-audit`.

## [1.0.0] - 2026-06-05

### Added

- **P0–P3 engineering wave**: Python 3.10 `StrEnum` shim; `QCHEM_STACK_REQUIRE_API_KEY` fail-fast; `protocols.excited_resource_export` (removes protocols→orchestration import); ADAPT/IQEB/DMET L1 example YAMLs; `docs/engineering/test_ownership.md`; perf baseline seed; SDK doc sync in CI.
- **Stable integrator facade** [`qchem_stack.sdk`](src/qchem_stack/sdk/__init__.py): pipeline, parity export, workflow preview, repro helpers.
- Console scripts **`qchem-run`** and **`qchem-export-parity`**; wheel-safe **`export_parity_criteria_table`** in-package.
- HTTP **`api_contract_version": "1.0"`** on all `/v1/*` routes; OpenAPI snapshot gate (`docs/generated/openapi_snapshot.json`).
- Docs: [`docs/engineering/v1_0_acceptance.md`](docs/engineering/v1_0_acceptance.md), [`migration_v0_8_to_v1_0.md`](docs/engineering/migration_v0_8_to_v1_0.md).
- CI: import-linter contracts (protocols/chem/quantum layer boundaries); `QCHEM_RELEASE_FULL=1` optional L3 in `release_precheck.sh`.
- Jobs/md_bridge test expansion; coverage floors **jobs 75%**, **md_bridge 70%**.
- Operator-pool L1 configs: `example_h2_adapt_bk_pool.yaml`, `example_h2_adapt_generalized_doubles_pool.yaml`, `example_h2_iqeb_bk_singles_pool.yaml`.
- DMET L1 config: `example_h2_dimer_dmet_self_consistent.yaml`.

### Changed

- Tests reorganized from flat `tests/test_*.py` into layer subdirectories (`api/`, `chem/`, `quantum/`, `repro/`, …).
- `pipeline_events` split into `pipeline_event_types.py`, `pipeline_event_bus.py`, and slim facade.
- Coverage floors: `md_bridge` and `api` packages ≥70%; `release_precheck.sh` runs pytest with `--cov`.
- PyPI classifier **Production/Stable**; package version **1.0.0**.
- **`results/`** local-only (see `results/README.md`).
- Per-package coverage floors and pyright tightening on **backends** / **jobs**.
- Execution closeout docs under **`docs/execution/archive/2026Q2/`**.
- `product_contract_gaps` rows include `evidence` YAML lists for operator pools and DMET.

### Removed (breaking since v0.8 / v1.0)

- **`qchem_stack.chem.embedding.schmidt_variational_sidecar`** — use **`integrations.schmidt_per_fragment_vqe`**.
- **`molecular_hamiltonian_from_pyscf`** — use **`build_pre_quantum_input`** / YAML pipeline.
- **`qchem_stack.chem.pre_quantum_build.hamiltonian`** alias — use **`build_pre_quantum_input(...).qubit_hamiltonian`**.
- **`projection_hamiltonian.mulliken_mo_populations_on_atoms`** (PySCF-mf shim) — use **`chem.embedding.ao_fragment.mulliken_mo_populations_on_atoms`** with **`AOBasisView`**.
- Root **`opus4.8-test.md`** agent session artifact (0.8 cycle).

### Fixed

- `release_precheck.sh` no longer assumes pre-existing `htmlcov/` for threshold checks.

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

## [0.8.0] - 2026-06-04

### Removed (breaking)

- **`molecular_hamiltonian_from_classical_reference`** — use **`build_pre_quantum_input`** / YAML pipeline.
- **`apply_backend_profile()`** — use **`apply_backend_profile_immutable()`**.
- **`qchem_stack.integrations.dmet_self_consistent`** shim — import from **`qchem_stack.chem.embedding.dmet_self_consistent`**.

### Changed

- Protocol job writes default to **JSON blob v2** when `QCHEM_PROTOCOL_BLOB_V2` is unset (opt-out with `0`/`false`).
- Pyright **`reportMissingParameterType=error`** for **`src/qchem_stack/quantum/algorithms`**.

## [0.7.0] - 2026-06-04

### Added

- In-package parity export API: **`qchem_stack.protocols.parity_criteria_export.export_parity_criteria_table`** (wheel-safe; no repo `scripts/` dependency).
- **`scripts/bootstrap_dev.sh`** for one-shot `.venv` + `pip install -e ".[dev]"`.
- CI **`contract-gate`** split into **`contract-docs`**, **`contract-smoke`**, **`contract-integration`** (parallel).
- Chem coverage gate raised to **70%**; extra adapter/bundle edge tests.

### Changed

- **`qchem_stack.sdk.export_parity_table`** and **`qchem-export-parity`** call the in-package exporter (no subprocess).
- **`scripts/venv-run`** / CONTRIBUTING: prefer `.venv` bootstrap path.
- Docs index: explicit Product / Reference / Non-runtime zones.

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
