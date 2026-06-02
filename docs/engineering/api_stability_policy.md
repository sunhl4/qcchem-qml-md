# API stability policy

**Package version:** `qchem_stack.__version__` (from `pyproject.toml` when installed).

## Stable integrator imports (semver intent)

| Symbol | Module |
|--------|--------|
| `run_pipeline_sync`, `run_pipeline_from_config` | `qchem_stack.orchestration.pipeline` |
| `ExperimentConfig`, `load_experiment_config` | `qchem_stack.config` |
| `repro_json_dumps`, `repro_dict_for_strict_json` | `qchem_stack.repro.export` |
| `ConfigurationError`, `PipelineError`, `ReproExportError`, … | `qchem_stack.exceptions` |

## Experimental

- Keys inside `repro.parity_snapshot` not listed in export stable-key registries.
- HTTP `/v1/*` routes (local analog; may evolve until v1.0).
- `qchem_stack.integrations` re-export shims (removal v0.6.0 per CHANGELOG).

## Config contract

`ExperimentConfig.schema_version` is independent of package semver. Breaking YAML changes require migration codemods and `tests/test_config_migration_strict.py`.

## Release checklist

1. Bump `[project].version` in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Run full CI parity gates (`CONTRIBUTING.md`).
4. Publish: see [`pypi_release.md`](pypi_release.md) (GitHub Release → OIDC workflow).
