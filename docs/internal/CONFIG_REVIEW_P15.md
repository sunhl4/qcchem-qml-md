# Config module review — P15 full refactor

Date: 2026-05-20  
Scope: `src/qchem_stack/config/` + codemods touching orchestration/chem/mitigation call sites.

## Summary

P15 completes the config review backlog: helper/validation module split, property shim removal, canonical active-space counts, strict flat→nested migrations (8 modules), SCF nested driver sub-blocks (`scf.pyscf.*` / `scf.psi4.*`), docs/Field polish, and CI-equivalent verification.

## Maturity matrix (representative)

| Area | Before P15 | After P15 |
|------|------------|-----------|
| `mitigation` | 12 `@property` shims | Nested only + `mitigation_helpers.py` |
| `chemistry_extended` | 12 `@property` shims | Nested only + `chemistry_extended_helpers.py` |
| `active_space` | 7 deprecated `@property` shims | Nested + helpers; canonical `cas.n_orbitals` / `n_electrons` |
| `md_ml_export` | 2 `@property` shims | Nested only + `md_ml_export_helpers.py` |
| `scf` | Flat driver controls on root | `pyscf` / `psi4` / `precomputed` sub-blocks + `scf_helpers.py` |
| `embedding` backend caps | Fake `_Cfg` object for path resolve | Direct `embedding_helpers` + `PreQuantumPath` |
| AVAS validation | Duplicated in backend-cap + dedicated validator | Single gate: `validate_avas_strategy_requires_labels_and_capability` |
| Migration strictness | Partial (embedding, chemistry_extended, quantum) | All 8 section migrators + `tests/test_config_migration_strict.py` |
| Field descriptions | Class docstrings on `compiler`, `parity_integrations`, `nexus` | `Field(description=...)` on public knobs |
| Style doc §3.2/3.3 | “待实现” | ✅ marked implemented in `docs/config_校验分层约定.md` |

## Removed property / alias shims

| Module | Removed |
|--------|---------|
| `mitigation.py` | `zne_enabled`, `zne_mode`, `zne_scales`, `pmsv_*` (5), `spam_calibration_enabled`, `pec_literature_stub_enabled`, `classical_shadows_*` (2) |
| `chemistry_extended.py` | `solvent_model`, `pbc_*`, `avas_*` (8), `integral_crosscheck`, `classical_benchmark_enabled` |
| `active_space.py` | `fermion_qubit_mapping`, `ncas`, `nelecas`, `n_active_*`, `frozen_orbitals`, JW legacy props |
| `md_ml_export.py` | `extra_coordinates_bohr`, `trajectory_theory_level` |
| `_active_space_validation._assign_active_space_counts` | No longer writes `ncas` / `n_active_*` alias fields after normalize |

**Removed in P15 follow-up:** `SCFSpec.precomputed_bundle_path` property (use `scf.precomputed.bundle_path`; flat YAML key still migrates via `_scf_migration`).

## Migration strict coverage

| Module | `raise_if_unmigrated_keys` | Tested in `test_config_migration_strict.py` |
|--------|---------------------------|---------------------------------------------|
| `_embedding_migration.py` | ✅ (prior P0) | ✅ |
| `_chemistry_extended_migration.py` | ✅ (prior P0) | ✅ |
| `_quantum_migration.py` | ✅ (custom) | ✅ |
| `_mitigation_migration.py` | ✅ P15 | ✅ |
| `_active_space_migration.py` | ✅ P15 | ✅ |
| `_scf_migration.py` | ✅ P15 | ✅ |
| `_md_ml_migration.py` | ✅ P15 | ✅ |
| `_experiment_migration.py` | delegates per-section | packaged YAML smoke |

## New / updated artifacts

- Helpers: `mitigation_helpers.py`, `chemistry_extended_helpers.py`, `md_ml_export_helpers.py`, `scf_helpers.py`
- Validation: `_mitigation_validation.py` (extension point)
- Codemods: `codemod_mitigation_paths.py`, `codemod_md_ml_paths.py`, `codemod_scf_paths.py`; updated `codemod_active_space_paths.py`, `codemod_chemistry_paths.py`
- Tests: `tests/test_config_migration_strict.py`
- Docs: `docs/config_校验分层约定.md` §3.2/3.3/SCF row; `STYLE_OPTIMIZATION_ROADMAP.md` P15-config

## CI-equivalent results (2026-05-20)

| Gate | Result |
|------|--------|
| `pyright src/qchem_stack/config` | 0 errors |
| `pytest tests/test_config_*.py tests/test_*embedding* tests/test_*active_space* tests/test_validate_pre_quantum*` | **165 passed**, 1 skipped |
| `pytest tests/test_orchestration_pipeline.py tests/test_repro_*.py` | **56 passed** (incl. CASSCF audit + Schmidt smoke) |
| `ruff check src/qchem_stack/config tests scripts` | Pre-existing TC001/B017 in legacy files; config edits formatted |
| `code_health_baseline.json` | Updated |

## Follow-up (non-blocking for P15 config)

All items below were closed in the 2026-05-20 continuation pass:

1. **PySCF `raw_handle` / `PySCFMeanFieldLike`** — fixed via `unwrap_mean_field_raw()` + updated `as_pyscf_mf()` and UHF guard in `molecular_problem.py`.
2. **`SCFSpec.precomputed_bundle_path`** — property removed; tests/scripts use `scf.precomputed.bundle_path` (flat YAML still migrates).
3. **Helper exports** — stable accessors exported from `qchem_stack.config.__init__`.

## Checklist vs `docs/config_校验分层约定.md`

- [x] `*_helpers.py` + `_*_validation.py` pattern for mitigation, chemistry_extended, md_ml, scf
- [x] No `@property` shims on mitigation / chemistry_extended / active_space / md_ml_export / scf
- [x] Active space canonical writes (`n_orbitals` / `n_electrons` only)
- [x] SCF nested driver blocks with flat YAML migration
- [x] All section migrations strict on unknown flat keys
- [x] AVAS validation deduplicated
- [x] `validate_embedding_backend_caps` without fake config object
- [x] Style doc + roadmap updated
