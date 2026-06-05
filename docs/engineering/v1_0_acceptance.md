# qchem-stack 1.0.0 acceptance checklist

**Target version:** `1.0.0` (`pyproject.toml` / `qchem_stack.__version__`)

Maintainers tick each **required** item before tagging `v1.0.0`. Commands assume repo root and `./scripts/bootstrap_dev.sh` unless noted.

## Required — API and SDK

- [x] [`api_stability_policy.md`](api_stability_policy.md) lists stable `qchem_stack.sdk` symbols matching `sdk.__all__`
- [x] `pytest tests/test_sdk_surface_snapshot.py tests/test_deprecation_schedule.py -q`
- [x] v0.8.0 removed symbols remain unimportable (see `test_deprecation_schedule.py`)
- [x] v1.0.0 removed modules/symbols documented in migration guide and CHANGELOG

## Required — HTTP (`[api]` extra)

- [x] All `/v1/*` JSON responses include `api_contract_version: "1.0"`
- [x] `pytest tests/test_api_runs.py -q` (set `QCHEM_STACK_DISABLE_RATE_LIMIT=1` via conftest)
- [ ] `pytest tests/test_api_auth_middleware.py` when validating production auth posture

## Required — contracts and export

- [x] `python -c "from qchem_stack.protocols.product_contract import validate_product_gap_categories; assert not validate_product_gap_categories()"`
- [x] `python scripts/check_parity_export_sample.py`
- [x] Config-only export: `parity_export_schema_version == "3"` and `PARITY_EXPORT_V3_STABLE_KEYS` enforced

## Required — tests and coverage

- [x] `pytest tests -q -m "not slow and not perf"`
- [ ] `python scripts/check_coverage_thresholds.py` after `pytest tests --cov=src/qchem_stack`
- [x] Per-package floors: `jobs` ≥75%; `md_bridge` ≥62% in default CI (70% with `[qmlff]` — see [`code_health_baseline.md`](code_health_baseline.md))

## Required — docs and product surface

- [ ] [`QUICKSTART_CONTRIBUTORS.md`](../QUICKSTART_CONTRIBUTORS.md) + Docusaurus build (`release_precheck.sh` without `--quick`)
- [x] [`migration_v0_8_to_v1_0.md`](migration_v0_8_to_v1_0.md) published
- [x] [`docs/product/non_goals.md`](../product/non_goals.md) unchanged scope (no L0 cloud parity claims)
- [x] `docs/generated/openapi_snapshot.json` in sync (`scripts/generate_openapi_snapshot.py --check`)

## Required — release

- [ ] `./scripts/release_precheck.sh` passes
- [ ] Optional full gate: `QCHEM_RELEASE_FULL=1 ./scripts/release_precheck.sh` (includes L3 when PySCF present)
- [x] `pyproject.toml` classifier `Development Status :: 5 - Production/Stable`
- [ ] GitHub Release `v1.0.0` + PyPI OIDC publish ([`pypi_release.md`](pypi_release.md))

## Optional — nightly / maintainer

- [ ] `QCHEM_RUN_L3=1 pytest -m l3 -q` (representative algorithm YAMLs)
- [ ] `pytest -m slow` / `pytest -m perf` on schedule
- [ ] macOS/Windows `test-cross-platform` green on main

## Explicit non-goals (1.0)

See [`non_goals.md`](../product/non_goals.md): Nexus/HQC, commercial Qermit, cuTensorNet L0, SCBK UCCSD Trotter, ORCA/Gaussian drivers.

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Maintainer | | | `release_precheck.sh` command recorded |
