# Test directory ownership

Pytest discovers all modules under `tests/` recursively (`testpaths = ["tests"]`).

| Directory | Layer / scope |
|-----------|----------------|
| `tests/api/` | HTTP FastAPI (`qchem_stack.api`) |
| `tests/backends/` | Backend executors and conformance |
| `tests/chem/` | Classical chemistry, solvers, embedding, DMET |
| `tests/config/` | `ExperimentConfig` validation and migrations |
| `tests/contracts/` | Shared contract modules |
| `tests/jobs/` | SQLite worker, protocol blobs, migration scripts |
| `tests/md_bridge/` | MD/ML bridge and QMEF |
| `tests/mitigation/` | Mitigation stacks (ZNE, PMSV, SPAM, Qermit analog) |
| `tests/orchestration/` | Pipeline stages, events, registry |
| `tests/protocols/` | Pauli protocol, parity export, product contract |
| `tests/quantum/` | Variational algorithms, operator pools, excited states |
| `tests/repro/` | Strict JSON export, parity evidence, SDK surface |
| `tests/integrations/` | Cross-layer smoke, tier-2 glue |

When adding tests, place them in the layer directory that owns the code under test.

## Intentional split: `test_run_build_cache.py`

| File | Scope |
|------|--------|
| `tests/chem/test_run_build_cache.py` | Unit tests for `pack_cache_key` |
| `tests/orchestration/test_run_build_cache.py` | Integration: cache hits and pipeline stats |

These are **not** duplicates.

## `tests/repro/` retention list

Keep SDK / strict repro / parity export tests here, for example:

- `test_cli.py`, `test_repro_schema*.py`, `test_repro_export.py`, `test_repro_run_summary.py`
- `test_sdk_*.py`, `test_deprecation_schedule.py`, `test_secure_serialization.py`
- `test_export_parity_*.py`, `test_check_parity_export_sample_script.py`
- `test_methods_resource_unified_export.py`, `test_partial_l1_evidence.py`
- `test_pipeline_result_schema.py`, `test_observability_pipeline.py`
- `test_workflow_preview_repro_alignment.py`, `test_resource_summary_excited_bounds.py`
- `test_check_import_layers_script.py` (engineering script regression)

Cross-layer smoke belongs in `tests/integrations/`; layer-specific tests belong in the matching directory above.
