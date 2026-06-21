# Migration guide: v1.0.x → v1.1.0

English reference for integrators upgrading **qchem-stack** to **1.1.0**.

## Install

```bash
pip install -U "qchem-stack>=1.1.0,<2"
pip install -U "qchem-stack[chem]>=1.1.0,<2"
```

## Breaking changes (1.1.0)

| Removed / tightened | Use instead |
|---------------------|-------------|
| `qchem_stack.integrations.compat.*` | `chem.embedding.dmet_self_consistent`, `integrations.schmidt_per_fragment_vqe`, `chem.kernels.spin_ucc` |
| Unsigned legacy pickle protocol blobs (default) | Run `python scripts/migrate_job_protocol_blobs.py`; temporary `QCHEM_ALLOW_LEGACY_PICKLE=1` only during migration |
| `QCHEM_PROTOCOL_BLOB_V2=0` write path (deprecated) | Default HMAC-signed JSON v2 (unset or `1`) |

## Job store / worker operators

1. Set `QCHEM_PROTOCOL_HMAC_KEY` to a production-strength secret before workers load signed blobs.
2. If upgrading from SQLite rows with unsigned pickle payloads:
   ```bash
   export QCHEM_PROTOCOL_HMAC_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   export QCHEM_ALLOW_LEGACY_PICKLE=1
   python scripts/migrate_job_protocol_blobs.py
   unset QCHEM_ALLOW_LEGACY_PICKLE
   ```
3. For HA deployments, prefer `PostgresJobStore` via `QCHEM_JOB_DATABASE_URL` (see [`job_store_extension.md`](job_store_extension.md)).

## Config / onboarding

- Prefer scenario-first runs: `qchem-run --scenario minimal_vqe` (thin v3 stubs under `configs/scenarios/`).
- DMET Schmidt production embedding requires `scf.method='RHF'`; validation errors include a `Suggestion:` hint pointing to the `embedding_dmet` scenario.

## HTTP API

No `/v1` route removals in 1.1.0. Production posture unchanged: set `QCHEM_STACK_API_KEY` and `QCHEM_STACK_REQUIRE_API_KEY=1` (see [`production_deployment.md`](production_deployment.md)).

## Verification after upgrade

```bash
./scripts/release_precheck.sh --quick   # fast gate (no docusaurus / full cov)
pytest tests/repro/test_secure_serialization.py -q
pytest tests/api/test_api_auth_middleware.py -q
```

## Related

- [`CHANGELOG.md`](../../CHANGELOG.md) — `[Unreleased]` / `1.1.0` section
- [`migration_v0_8_to_v1_0.md`](migration_v0_8_to_v1_0.md) — earlier breaking removals
- [`v1_1_acceptance.md`](v1_1_acceptance.md) — maintainer release checklist
