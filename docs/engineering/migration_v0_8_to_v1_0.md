# Migration guide: v0.8.x → v1.0.0

English reference for integrators upgrading **qchem-stack** to **1.0.0**.

## Install

```bash
pip install -U "qchem-stack>=1.0.0,<2"
# Typical chemistry path:
pip install -U "qchem-stack[chem]>=1.0.0,<2"
```

## Breaking API removals (1.0.0)

| Removed | Use instead |
|---------|-------------|
| `qchem_stack.chem.embedding.schmidt_variational_sidecar` | `qchem_stack.integrations.schmidt_per_fragment_vqe` |
| `molecular_hamiltonian_from_pyscf` | `build_pre_quantum_input` / `run_pipeline_sync` |
| `qchem_stack.chem.pre_quantum_build.hamiltonian` | `build_pre_quantum_input(cfg, reference).qubit_hamiltonian` |
| `projection_hamiltonian.mulliken_mo_populations_on_atoms(mf, ...)` | `chem.embedding.ao_fragment.mulliken_mo_populations_on_atoms` with `AOBasisView` |

v0.8.0 removals (unchanged): see [`api_stability_policy.md`](api_stability_policy.md) — `molecular_hamiltonian_from_classical_reference`, `apply_backend_profile()`, `integrations.dmet_self_consistent` shim.

## Planned for 1.1.0

See [`migration_v1_0_to_v1_1.md`](migration_v1_0_to_v1_1.md) for the full upgrade guide.

| Removed | Use instead |
|---------|-------------|
| `qchem_stack.integrations.compat.*` | `chem.embedding.dmet_self_consistent`, `integrations.schmidt_per_fragment_vqe`, `chem.kernels.spin_ucc` |
| `QCHEM_PROTOCOL_BLOB_V2=0` (pickle write path) | Default HMAC-signed JSON v2 (unset or `1`) |
| `QCHEM_ALLOW_LEGACY_PICKLE=1` (production default) | Migrate blobs then unset; unsigned pickle load disabled by default |

## Stable integrator surface (1.0.0)

Prefer **`qchem_stack.sdk`**:

- `run_pipeline_sync`, `run_pipeline_from_config`
- `load_experiment_config`, `ExperimentConfig`
- `export_parity_table`
- `workflow_preview_payload`, `list_scenarios_text`
- `repro_json_dumps`, `repro_dict_for_strict_json`

## HTTP API

- All `/v1/*` responses include **`api_contract_version": "1.0"`**.
- Breaking route changes require a new path (e.g. `/v2`); 1.0.0 does not remove existing routes.
- Production: set `QCHEM_STACK_API_KEY`; see [`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](../技术文档_HTTP_API与SQLite作业队列及可观测性契约.md).

## YAML / `ExperimentConfig`

- **`ExperimentConfig.schema_version`** is independent of package semver.
- No mandatory YAML edits for standard H₂ tutorials if you already run on v0.8 configs.
- Run `python scripts/check_config_combo_matrix.py` after editing nested `embedding` / `quantum` blocks.

## Protocol job blobs

- Default write path: **signed JSON blob v2** (`QCHEM_PROTOCOL_BLOB_V2` unset or `1`).
- Legacy signed pickle v1 remains readable; removal window documented for **1.1** in [`protocol_pickle_migration.md`](protocol_pickle_migration.md).

## Legacy note: `PySCFRHFResult`

`qchem_stack.chem.drivers.PySCFRHFResult` remains for typing compatibility; prefer backend-agnostic `ClassicalMeanFieldReference` in new code. Relocation to `chem.systems` is planned for 1.1 (non-blocking for 1.0).

## Verification

```bash
./scripts/bootstrap_dev.sh
./scripts/release_precheck.sh
pytest tests/repro/test_deprecation_schedule.py tests/repro/test_sdk_surface_snapshot.py -q
```
