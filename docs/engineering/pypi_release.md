# PyPI release guide

## Package coordinates

| Field | Value |
|-------|--------|
| PyPI name | `qchem-stack` |
| Import | `qchem_stack` |
| Version | `[project].version` in `pyproject.toml` |

## Pre-release checklist

1. Bump `version` in `pyproject.toml` and `src/qchem_stack/__init__.py`.
2. Update `CHANGELOG.md`.
3. Run full CI locally or on PR: `pytest tests -m "not slow and not perf"`, `ruff check`, `python scripts/check_parity_export_sample.py`.
4. Ubuntu 3.12 extras: `scripts/smoke_pipeline.py` (full flags), `pytest tests/test_api_runs.py` (with `[api]`).
5. Optional before tag: `pytest -m psi4`; nightly-style `QCHEM_RUN_L3=1 pytest -m l3`; `pytest -m slow tests/test_dmet_fragment_exact.py`.
6. Production API: set `QCHEM_STACK_API_KEY`; run `tests/test_api_auth_middleware.py`.
7. Confirm `README_PYPI.md` is ASCII-only (PyPI long description).

## Automated publish (recommended)

1. Create a GitHub **Release** with tag `vX.Y.Z` matching `pyproject.toml`.
2. Workflow [`.github/workflows/publish-pypi.yml`](../.github/workflows/publish-pypi.yml) builds sdist/wheel and publishes via **OIDC** (`id-token: write`).
3. Configure repository **Environment** `pypi` with trusted publishing on [pypi.org](https://pypi.org/manage/project/qchem-stack/settings/publishing/).

### Dry-run to TestPyPI

Actions → **Publish to PyPI** → Run workflow → `dry_run: true`.

## Manual publish

```bash
python -m pip install -U build twine
python -m build
twine check dist/*
twine upload dist/*
```

## Optional extras

```bash
pip install "qchem-stack[chem,quantum,api,uqc]"
```

QML-FF remains a sibling editable install (not bundled on PyPI). See root `README.md`.

## API stability

See [`api_stability_policy.md`](api_stability_policy.md) for semver intent on integrator imports.

## v0.6.0 breaking migrations

| Removed | Migration |
|---------|-----------|
| `PySCFDriver` | `create_solver` + `classical_mean_field_reference_from_config` — see [`../迁移指南_PySCFDriver到ChemIntegralSolver.md`](../迁移指南_PySCFDriver到ChemIntegralSolver.md) |
| `qchem_stack.ml` | `qchem_stack.md_bridge.active_learning` |
| `integrations/*` re-export shims | Import from `chem.embedding`, `chem.kernels`, etc. |
| `POST /v1/runs/sync` | `POST /v1/runs` + poll `GET /v1/runs/{id}` |
| `qchem-pipeline-worker` CLI | `qchem-jobs-worker` |
