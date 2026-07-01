# PyPI release guide

## Package coordinates

| Field | Value |
|-------|--------|
| PyPI name | `qchem-stack` |
| Import | `qchem_stack` |
| Version | `[project].version` in `pyproject.toml` |

## Pre-release checklist

1. Bump `version` in `pyproject.toml` and `src/qchem_stack/__init__.py`.
2. Update `CHANGELOG.md` (move `[Unreleased]` into the target version section).
3. Complete [`v1_1_acceptance.md`](v1_1_acceptance.md) (or [`v1_0_acceptance.md`](v1_0_acceptance.md) for patch releases on 1.0.x).
4. Run the unified gate (use the **project `.venv`**, not a stale conda env):
   ```bash
   cd /path/to/qcchem-qml-md
   export QCHEM_STACK_PYTHON="$PWD/.venv/bin/python"
   pip install -e ".[dev,chem,api]"   # once
   QCHEM_STACK_PYTHON="$QCHEM_STACK_PYTHON" bash scripts/release_precheck.sh
   ```
   Fast maintainer pass (skips Docusaurus build):
   ```bash
   QCHEM_STACK_PYTHON="$QCHEM_STACK_PYTHON" bash scripts/release_precheck.sh --quick
   ```
5. Optional before tag: `QCHEM_RELEASE_FULL=1 QCHEM_STACK_PYTHON="$QCHEM_STACK_PYTHON" bash scripts/release_precheck.sh` (L3 when PySCF installed).
6. Production API: set `QCHEM_STACK_API_KEY`; `pytest tests/api/test_api_auth_middleware.py`.
7. Confirm `README_PYPI.md` is ASCII-only (PyPI long description).

Integrators upgrading from 1.0.x: [`migration_v1_0_to_v1_1.md`](migration_v1_0_to_v1_1.md).

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
