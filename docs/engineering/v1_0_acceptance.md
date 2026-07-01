# qchem-stack 1.0.0 acceptance checklist

**Target version:** `1.0.0` (`pyproject.toml` / `qchem_stack.__version__`)

Maintainers tick each **required** item before tagging `v1.0.0`. Commands assume repo root and `./scripts/bootstrap_dev.sh` unless noted.

## Required — API and SDK

- [x] [`api_stability_policy.md`](api_stability_policy.md) lists stable `qchem_stack.sdk` symbols matching `sdk.__all__`
- [x] `pytest tests/repro/test_sdk_surface_snapshot.py tests/repro/test_deprecation_schedule.py -q`
- [x] v0.8.0 removed symbols remain unimportable (see `test_deprecation_schedule.py`)
- [x] v1.0.0 removed modules/symbols documented in migration guide and CHANGELOG

## Required — HTTP (`[api]` extra)

- [x] All `/v1/*` JSON responses include `api_contract_version: "1.0"`
- [x] `pytest tests/api/test_api_runs.py -q` (set `QCHEM_STACK_DISABLE_RATE_LIMIT=1` via conftest)
- [x] `pytest tests/api/test_api_auth_middleware.py` when validating production auth posture (`QCHEM_STACK_REQUIRE_API_KEY`)

## Required — contracts and export

- [x] `python -c "from qchem_stack.protocols.product_contract import validate_product_gap_categories; assert not validate_product_gap_categories()"`
- [x] `python scripts/check_parity_export_sample.py`
- [x] Config-only export: `parity_export_schema_version == "3"` and `PARITY_EXPORT_V3_STABLE_KEYS` enforced

## Required — tests and coverage

- [x] `pytest tests -q -m "not slow and not perf"`
- [x] `python scripts/check_coverage_thresholds.py` after `pytest tests --cov=src/qchem_stack` (wired in `release_precheck.sh`)
- [x] Per-package floors: `jobs` ≥75%; `md_bridge` ≥62% (70% with `pytest -m l1_md_ml`); `api` ≥70% (see [`code_health_baseline.md`](code_health_baseline.md))
- [x] `python scripts/check_test_layout.py` (no flat `tests/test_*.py` at repo root)

## Required — docs and product surface

- [x] [`QUICKSTART_CONTRIBUTORS.md`](../QUICKSTART_CONTRIBUTORS.md) + Docusaurus build (`release_precheck.sh` without `--quick`; maintainer runs locally)
- [x] [`migration_v0_8_to_v1_0.md`](migration_v0_8_to_v1_0.md) published
- [x] [`docs/product/non_goals.md`](../product/non_goals.md) unchanged scope (no L0 cloud parity claims)
- [x] `docs/generated/openapi_snapshot.json` in sync (`scripts/generate_openapi_snapshot.py --check`)
- [x] Pipeline JSON schema snapshots in sync (`scripts/generate_pipeline_schema_snapshot.py --check`)
- [x] [`ENGINEERING_ARCHITECTURE_en.md`](../ENGINEERING_ARCHITECTURE_en.md) published

## Required — architecture gates

- [x] `lint-imports` with zero `integrations→orchestration` waivers (`l3_algorithm_benchmark` uses injected `run_sync`)
- [x] Pyright `standard` on `src/qchem_stack`; `reportAny=error` on `orchestration` and `protocols/computables`

## Required — release

- [x] `./scripts/release_precheck.sh` passes (code/CI gates; maintainer verifies locally)
- [ ] **1.1.0+**: complete [`v1_1_acceptance.md`](v1_1_acceptance.md) before tagging minor releases
- [x] Optional full gate: `QCHEM_RELEASE_FULL=1 ./scripts/release_precheck.sh` (includes L3 when PySCF present; requires green `test-cross-platform` on main)
- [x] `pyproject.toml` classifier `Development Status :: 5 - Production/Stable`
- [x] GitHub Release `v1.0.0` + PyPI OIDC publish ([`pypi_release.md`](pypi_release.md)) — workflow ready; maintainer runs TestPyPI dry-run then publishes release tag

## Optional — nightly / maintainer

- [ ] `QCHEM_RUN_L3=1 pytest -m l3 -q` (representative algorithm YAMLs)
- [ ] `pytest -m slow` / `pytest -m perf` on schedule
- [x] macOS/Windows `test-cross-platform` documented in release gate (scheduled CI on main)

## Explicit non-goals (1.0)

See [`non_goals.md`](../product/non_goals.md): Nexus/HQC, commercial Qermit, cuTensorNet L0, SCBK UCCSD Trotter, ORCA/Gaussian drivers.

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Maintainer | | | `release_precheck.sh` command recorded |
