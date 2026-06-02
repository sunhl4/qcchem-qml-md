# P3 engineering closeout — unified WBS Phase M

**Date:** 2026-05-29  
**Scope:** P0-E through P3-E engineering excellence track.

## Version alignment

- `pyproject.toml` / `qchem_stack.__version__` / OpenAPI → **0.3.0** (matches CHANGELOG)

## Deliverables

| Track | Items |
|-------|--------|
| P0-E | Install profiles, Qiskit 2.x `quantum` extra, QUICKSTART §0, `pip-audit` on `[dev]`, constraints |
| P0-A | gap validator CI, `day210_p0_closeout.md` |
| P1-E | `md_bridge/energy_reference.py`, dual delta fields, tests, md_ml_export docs |
| P1-E docs | `docs/reference/config_*`, test pyramid in QUICKSTART |
| P1-A | Qulacs executor (pre-existing), DMET TypedDict report types |
| P2-E | Psi4 E2E smoke CI, P2_W5 Psi4 row, JSON log, meta ETag, partial→L1 playbook |
| P2-A | QPE main config (`example_h2_qpe_main.yaml`, tests pre-existing) |
| P3-E | docs IA, api stability policy, RunBuildCache spill, nightly L3 dashboard step |
| P3-A | 6 notebooks, `/parity/gaps`, `public-matrix` redirect, sidebars |

## Path A smoke (maintainer)

```bash
pip install -e ".[dev]"
python scripts/smoke_pipeline.py --precomputed-only  # no PySCF
python scripts/smoke_pipeline.py                     # with PySCF
```

## Backlog

Phase **M** in `comparative_execution_backlog.yaml` — mark tasks `done` with evidence pointers.
