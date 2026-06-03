# Phase N closeout — P0–P4 verification + residual closure

**Date:** 2026-06-03  
**Backlog:** Phase `N` in [`comparative_execution_backlog.yaml`](comparative_execution_backlog.yaml)

## Summary

Phase N closed high-ROI gaps from the P0–P4 verification plan:

| ID | Deliverable |
|----|-------------|
| N-001 | [`sprint0_p0_p4_regression_audit.md`](sprint0_p0_p4_regression_audit.md) |
| N-002 | Config scenario picker + `qchem-run --list-scenarios` |
| N-003 | Expanded `qchem_stack.sdk` facade |
| N-004 | Backend×mapping conformance matrix (12 parametrized cases) |
| N-005 | Resource estimation depth proxies |
| N-006 | OpenFermion 1.7 + UQC compatibility shims |
| N-007 | Binder `environment.yml` + expanded `README_PYPI.md` |
| N-008 | Mitigation queue `drain_all` E2E test + driver gap caveat |
| N-009 | CHANGELOG `[0.6.0]` alignment |

## Path A user test template (P3-R01)

Record for three independent reviewers:

| Reviewer | Install path | Time to `qchem-run configs/example_h2.yaml` | Pass ≤30min? |
|----------|--------------|-----------------------------------------------|--------------|
| R1 | `pip install "qchem-stack[chem]"` | ___ min | |
| R2 | editable `[dev]` | ___ min | |
| R3 | Binder badge | ___ min | |

Steps: `qchem-run --list-scenarios` → `qchem-run configs/example_h2.yaml` → inspect stdout energies.

## Version alignment (P4-R01)

- Package version: `pyproject.toml` **0.6.0**
- CHANGELOG: `[0.6.0] - 2026-06-03` section added
- PyPI publish: run `.github/workflows/publish-pypi.yml` on tag (maintainer action)

## Exit criteria

- [x] Backlog Phase N tasks `done` with evidence
- [x] Sprint0 audit written
- [x] Config picker + SDK + Binder shipped
- [ ] Full CI green (monitor post-merge)
- [ ] PyPI 0.6.0 tag (maintainer)
