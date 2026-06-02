# P0 closeout — parity / CI hygiene + install profiles (Phase M)

**Date:** 2026-05-29  
**Scope:** P0-A (parity/gap gates) + P0-E (install/onboarding/security) from unified WBS.

## Gates executed

| Gate | Result |
|------|--------|
| `python scripts/check_comparative_execution_backlog.py` | pass |
| `python scripts/check_parity_export_sample.py` | pass (local / CI 3.12) |
| `validate_product_gap_categories()` | wired in CI test job (3.12) |
| `pip-audit` on `pip install -e ".[dev]"` | blocking `security-audit` job |
| Import layers `scripts/check_import_layers.py` | lint job |

## P0-A residual review

| ID | Status | Notes |
|----|--------|-------|
| P0-01 | done | `tests/conftest.py` + `tests/helpers/h2_yaml.py` in tree |
| P0-05 | done | `check_parity_export_sample.py` multi-config sample incl. DMET/projection |
| P0-07 | **closed this pass** | gap validator step added to CI |
| P0-10 | **this document** | closeout |

## P0-E deliverables

- README install profiles table + Qiskit 2.x policy (`quantum` extra aligned with `uqc`)
- `docs/QUICKSTART_CONTRIBUTORS.md` §0 (15-minute path, precomputed smoke)
- `constraints/dev.txt`, `constraints/uqc.txt`, `pip-audit.toml`
- Docusaurus quickstart install cross-link

## Exit criteria

- [x] parity sample + gap validator green path documented
- [x] README extras table; Qiskit version documented
- [x] pip-audit on `[dev]` install surface
- [x] QUICKSTART §0 precomputed smoke path

**Next:** P1-E MD/ML energy reference contract (`M-P1-E01`).
