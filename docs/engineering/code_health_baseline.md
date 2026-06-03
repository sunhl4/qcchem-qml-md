# Code health baseline

Snapshot for regression tracking. Regenerate with `python scripts/code_health_baseline.py`.

**Recorded:** 2026-06-03 (post registry-driven `pipeline_sync_runner`)

## Metrics

| Metric | Value |
|--------|-------|
| `src/qchem_stack` Python files | 418 |
| Files over 400 lines | 4 |
| Files over 500 lines | 0 |
| `orchestration/pipeline.py` lines | ~185 |
| `orchestration/pipeline_sync_runner.py` | registry loop via `PIPELINE_STAGE_SPECS` (~88 lines) |

## Files over 400 lines

| Lines | Path |
|-------|------|
| 471 | `quantum/algorithms/excited_vqd.py` |
| 444 | `md_bridge/md_loop_rounds.py` |
| 412 | `orchestration/pipeline_events.py` |
| 411 | `md_bridge/from_pipeline.py` |

## `dict[str, Any]` density (top 4)

| Count | Path |
|-------|------|
| 18 | `protocols/protocol_v2_document.py` |
| 15 | `quantum/algorithms/excited_basis.py` |
| 13 | `config/migrations.py` |
| 11 | `chem/embedding/dmet_self_consistent.py` |

## Coverage targets (CI)

| Package prefix | Threshold |
|----------------|-----------|
| `src/qchem_stack/chem` | 65% (raise toward 70% next phase) |

## Related

- [`pipeline_stage_ownership.md`](pipeline_stage_ownership.md)
- [`dmet_module_map.md`](dmet_module_map.md)
