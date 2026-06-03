# Sprint 0 — P0–P4 regression audit

**Date:** 2026-06-03  
**Scope:** Verify Phases A–M (P0–P4) deliverables; record gate results before Phase N closure.

## Gate results

| ID | Gate | Result | Notes |
|----|------|--------|-------|
| S0-01 | `pytest -m "not slow and not perf"` | **pass (spot + fixes)** | Fixed OpenFermion 1.7 spatial fermion, UQC shims, ZNE polyfit cov, UQC factory registration |
| S0-02 | `check_parity_export_sample.py` | **pass** | exit 0 |
| S0-03 | `check_comparative_execution_backlog.py` | **pass** | Phases A–N |
| S0-04 | `check_import_layers.py` | **pass** | |
| S0-05 | Docusaurus build | **not run locally** | defer to CI `docusaurus` job |
| S0-06 | `examples/run_all_smoke.py` | **not run** | optional maintainer smoke |
| S0-07 | `QCHEM_RUN_L3=1 pytest -m l3` | **not run** | optional nightly |
| S0-08 | Backlog evidence audit | **pass** | Phase N tasks registered with evidence |

## Fixes applied (Phase N)

1. **`spatial_restricted_fermion.py`**: OpenFermion 1.7 rejects bulk dict construction; build term-by-term with `int` indices.
2. **UQC shims**: `src/qchem_stack/backends/uqc_*.py` re-export `qchem_stack_uqc`; `tests/conftest.py` adds plugin `src` path.
3. **`packages/qchem-stack-uqc/pyproject.toml`**: fix `build-backend` typo.

## Residual risks

- Full pytest matrix should be re-run on CI after merge.
- Optional backends (cirq/braket/qulacs) in mapping matrix skip when import missing.
- PyPI publish (P4-R02) requires maintainer tag + OIDC workflow — not executed in this sprint.

## Next steps

- Monitor CI `test` job across Python 3.10–3.12.
- Run `./scripts/release_precheck.sh` before tagging `0.6.0`.
