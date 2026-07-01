# API stability policy

**Package version:** `qchem_stack.__version__` (from `pyproject.toml` when installed).

## Stable integrator imports (since 1.0.0)

| Symbol | Module |
|--------|--------|
| `run_pipeline_sync`, `run_pipeline_from_config` | `qchem_stack.orchestration.pipeline` |
| `export_parity_criteria_table` | `qchem_stack.protocols.parity_criteria_export` |
| `ExperimentConfig`, `load_experiment_config` | `qchem_stack.config` |
| `repro_json_dumps`, `repro_dict_for_strict_json` | `qchem_stack.repro.export` |
| `ConfigurationError`, `PipelineError`, `ReproExportError`, … | `qchem_stack.exceptions` |

## Stable SDK facade (`qchem_stack.sdk`)

| Symbol | Notes |
|--------|--------|
| `run_pipeline_sync`, `run_pipeline_from_config` | YAML / config orchestration |
| `load_experiment_config`, `ExperimentConfig` | Config loading |
| `export_parity_table` | Parity / Methods export |
| `workflow_preview_payload` | Five-stage + computable graph preview |
| `list_scenarios_text`, `SCENARIOS` | Scenario picker |
| `repro_json_dumps`, `repro_dict_for_strict_json` | Strict repro JSON |

Regression: `tests/repro/test_sdk_surface_snapshot.py`.

## Stable HTTP API (since 1.0.0)

- Routes under **`/v1/*`** include **`api_contract_version": "1.0"`** on JSON responses.
- Breaking changes require a new path (e.g. `/v2`); existing `/v1` routes remain additive-only within 1.x.
- Contract tables: [`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](../技术文档_HTTP_API与SQLite作业队列及可观测性契约.md).

## Removed in v0.8.0

| Symbol | Replacement |
|--------|-------------|
| `molecular_hamiltonian_from_classical_reference` | `build_pre_quantum_input` / YAML pipeline |
| `apply_backend_profile()` | `apply_backend_profile_immutable()` |
| `qchem_stack.integrations.dmet_self_consistent` | `qchem_stack.chem.embedding.dmet_self_consistent` |

## Removed in v1.0.0

| Symbol | Replacement |
|--------|-------------|
| `qchem_stack.chem.embedding.schmidt_variational_sidecar` | `qchem_stack.integrations.schmidt_per_fragment_vqe` |
| `molecular_hamiltonian_from_pyscf` | `build_pre_quantum_input` / YAML pipeline |
| `qchem_stack.chem.pre_quantum_build.hamiltonian` | `build_pre_quantum_input(...).qubit_hamiltonian` |
| `projection_hamiltonian.mulliken_mo_populations_on_atoms` | `chem.embedding.ao_fragment.mulliken_mo_populations_on_atoms` + `AOBasisView` |

Migration: [`migration_v0_8_to_v1_0.md`](migration_v0_8_to_v1_0.md).

## Experimental

- Keys inside `repro.parity_snapshot` not listed in export stable-key registries (`PARITY_EXPORT_V3_STABLE_KEYS`).

## Config contract

`ExperimentConfig.schema_version` is independent of package semver. Breaking YAML changes require migration codemods and `tests/config/test_migrations.py`.

## Release checklist

1. Bump `[project].version` in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Complete [`v1_0_acceptance.md`](v1_0_acceptance.md) for major releases.
4. Run full CI parity gates (`CONTRIBUTING.md`).
5. Publish: see [`pypi_release.md`](pypi_release.md) (GitHub Release → OIDC workflow).
