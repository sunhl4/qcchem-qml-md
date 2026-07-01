# Code health baseline

Snapshot for regression tracking. Regenerate with `python scripts/code_health_baseline.py --write docs/engineering/code_health_baseline.snapshot.json`.

**Recorded:** 2026-06-14 (P0–P3 engineering optimization wave)

## Metrics

| Metric | Value |
|--------|-------|
| `src/qchem_stack` Python files | 457 |
| Files over 400 lines | 0 |
| Files over 500 lines | 0 |
| Largest module | `quantum/algorithms/excited_basis.py` (~379 lines) |

## `dict[str, Any]` density (top 4)

| Count | Path |
|-------|------|
| 26 | `protocols/protocol_v2_document.py` |
| 13 | `integrations/methods_resource_unified.py` |
| 11 | `chem/embedding/dmet_self_consistent.py` |
| 11 | `mitigation/qermit_runtime.py` |

## Coverage targets (CI)

| Package prefix | Threshold |
|----------------|-----------|
| `src/qchem_stack/chem` | 75% |
| `src/qchem_stack/jobs` | 62% |
| `src/qchem_stack/md_bridge` | 69% |
| `src/qchem_stack/mitigation` | 70% |
| `src/qchem_stack/api` | 70% |

## Related

- [`pipeline_stage_ownership.md`](pipeline_stage_ownership.md)
- [`dmet_module_map.md`](dmet_module_map.md)
