# qchem-stack 1.1.0 acceptance checklist

**Target version:** `1.1.0` (`pyproject.toml` / `qchem_stack.__version__`)

Tick each **required** item before tagging `v1.1.0`. Commands assume repo root and an editable install (`pip install -e ".[dev,chem,api]"`).

**Local interpreter (required):** use the project venv, not a stale conda env:

```bash
export QCHEM_STACK_PYTHON="/path/to/qcchem-qml-md/.venv/bin/python"
pip install -e ".[dev,chem,api]"   # once, with that interpreter
QCHEM_STACK_PYTHON="$QCHEM_STACK_PYTHON" bash scripts/release_precheck.sh --quick
```

> **Local sign-off (2026-06-21):** layout/import-layers/code-health gates pass; schema snapshots in sync; `.secrets.baseline` committed; reusable CI workflows + publish hardening staged locally. **Push to origin required** before CI/integration/PyPI items below can be ticked on remote.

## Required — breaking migrations

- [x] [`migration_v1_0_to_v1_1.md`](migration_v1_0_to_v1_1.md) published
- [x] `CHANGELOG.md` `[Unreleased]` merged into `## [1.1.0] - 2026-06-15`
- [x] `integrations.compat` removed; no imports remain (`rg integrations\\.compat`)
- [x] `pytest tests/repro/test_secure_serialization.py -q` (legacy pickle opt-in + `JobPayloadError` default)

## Required — scenario-first onboarding

- [x] All eight `configs/scenarios/*.yaml` stubs compile (`pytest tests/config/test_scenario_v3_compile.py -q`)
- [x] `qchem-run --scenario minimal_vqe --json-summary` (contract-smoke parity)
- [x] README + Docusaurus quickstart default `--scenario minimal_vqe`

## Required — architecture gates

- [x] `lint-imports` zero `integrations→orchestration` waivers
- [x] `python scripts/check_code_health_regression.py` — verified locally 2026-06-21
- [x] `python scripts/check_doc_test_paths.py` (Tier-1 fail, Tier-2 warn) — verified locally 2026-06-21
- [x] `python scripts/check_test_layout.py` — zero flat `tests/test_*.py` at repo root
- [x] Pyright `typecheck-config` (config, repro, chem/solvers) — full orchestration stack deferred to **1.2** (`QCHEM_PYRIGHT_FULL=1` opt-in; `release_precheck.sh` defaults `QCHEM_PYRIGHT_FULL=0`)

## Required — jobs / Postgres

- [x] `pytest tests/jobs/test_job_store_protocol_conformance.py -q` (memory + sqlite; postgres when `QCHEM_JOB_DATABASE_URL` set)
- [x] Integration workflow green with `postgres:15` service (see `.github/workflows/integration.yml`) — CI Run [#28530730813](https://github.com/sunhl4/qcchem-qml-md/actions/runs/28530730813) 2026-07-01

## Required — release gate

- [x] `./scripts/release_precheck.sh --quick` passes with `.venv (1254 tests, contract snapshots; skips Docusaurus/nbmake in --quick) — verified 2026-07-02
- [x] Optional: `QCHEM_RELEASE_FULL=1` L3 + `l3_algorithm_benchmark_report.py` (PySCF; uses `--no-cov` on `-m l3`)
- [x] Local wheel: `python -m build && twine check dist/*` + isolated `pip install dist/*.whl` smoke
- [ ] GitHub Release `v1.1.0` + PyPI OIDC publish ([`pypi_release.md`](pypi_release.md)) — **manual; not performed**

## Required — packaging & CI metadata

- [x] Wheel bundles `configs/` under `share/qchem-stack/configs` (`MANIFEST.in` + `pyproject.toml` data-files)
- [x] GitHub Actions CI green on `main` — Run [#28530730813](https://github.com/sunhl4/qcchem-qml-md/actions/runs/28530730813) 2026-07-01 (13/13 jobs)
- [x] GitHub Pages: `docusaurus.config.ts` + `.github/workflows/deploy-docs.yml` (docusaurus job green in CI; deploy workflow dispatch on release)
- [x] `SECURITY.md`, `CITATION.cff`, `CODE_OF_CONDUCT.md`, README CI badge
- [x] `.secrets.baseline` for detect-secrets pre-commit hook

## Required — production posture

- [x] [`production_deployment.md`](production_deployment.md) pickle migration steps reviewed
- [x] `.env.example` for docker-compose production secrets (no real values)
- [x] `QCHEM_ALLOW_LEGACY_PICKLE` documented as migration-only (not production default)
- [x] OTel quickstart: `examples/observability/docker-compose.otlp.yaml` + [`ENGINEERING_ARCHITECTURE_en.md`](../ENGINEERING_ARCHITECTURE_en.md)

## Explicit non-goals (1.1.0)

Unchanged from 1.0 — see [`non_goals.md`](../product/non_goals.md).

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Maintainer | auto | 2026-07-02 | CI #28530730813 green; `release_precheck.sh --quick` OK (1254 passed) |
