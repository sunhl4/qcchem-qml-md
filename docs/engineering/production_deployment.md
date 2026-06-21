# Production deployment checklist

Use this when exposing the optional HTTP API or SQLite worker beyond localhost.

## Required environment variables

| Variable | Production value | Purpose |
|----------|------------------|---------|
| `QCHEM_STACK_REQUIRE_API_KEY` | `1` | Fail-fast if API key missing at startup |
| `QCHEM_STACK_API_KEY` | strong random secret | `X-API-Key` authentication |
| `QCHEM_STACK_CONFIG_BASE_DIR` | trusted config root | Allowlist for geometry / precomputed paths ([path_sandbox.py](../src/qchem_stack/config/path_sandbox.py)) |
| `QCHEM_PROTOCOL_HMAC_KEY` | strong random secret | Protocol blob integrity (never use dev default) |
| `QCHEM_STACK_DB_DIR` | persistent volume | SQLite job store directory |
| `QCHEM_JOB_DATABASE_URL` | Postgres DSN | HA worker (`PostgresJobStore`) — see [`job_store_extension.md`](job_store_extension.md) |

## Network posture

- Bind API to `127.0.0.1` only; terminate TLS at a reverse proxy.
- Do not expose the worker or API on a public interface without authentication.
- Configure `QCHEM_STACK_CORS_ORIGINS` explicitly; never use `*` with credentials.

## Docker Compose defaults

[`docker-compose.yml`](../docker-compose.yml) sets `QCHEM_STACK_REQUIRE_API_KEY=1` for `qchem-api`. Copy [`.env.example`](../.env.example) to `.env` and set `QCHEM_STACK_API_KEY` and `QCHEM_PROTOCOL_HMAC_KEY` before `docker compose up`.

## Path sandbox

`validate_config_base_dir()` resolves user-supplied `config_base_dir` against:

1. `QCHEM_STACK_CONFIG_BASE_DIR` (if set), and/or
2. repository `configs/` when present.

Requests outside allowed directories raise `ConfigBaseDirError` (HTTP 400 on enqueue when using `/v1/runs`).

## Verification tests

- `pytest tests/api/test_api_auth_middleware.py`
- `pytest tests/api/test_api_config_base_dir_sandbox.py`

## Pickle legacy migration

Legacy **unsigned** pickle protocol blobs are **disabled by default**. Production workers should only load HMAC-signed JSON v2 (default) or signed pickle v1 blobs.

### Migration path

If you have existing SQLite job rows containing legacy unsigned pickle blobs:

1. Set a temporary migration key and opt-in flag on the worker that will read old rows:
   ```bash
   export QCHEM_PROTOCOL_HMAC_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   export QCHEM_ALLOW_LEGACY_PICKLE=1
   ```
2. Run the one-time migration script before upgrading production workers:
   ```bash
   python scripts/migrate_job_protocol_blobs.py
   ```
   The script reports counts for `legacy_unsigned_pickle`, `signed_json_v2`, and related blob classes.
3. After migration completes, **unset** `QCHEM_ALLOW_LEGACY_PICKLE` and rotate `QCHEM_PROTOCOL_HMAC_KEY` to a production-strength secret.
4. Prefer `QCHEM_PROTOCOL_BLOB_V2=1` (default) for new jobs; setting `QCHEM_PROTOCOL_BLOB_V2=0` emits a deprecation warning on workers.

### Rollback

If migration fails, restore from database backup. Unsigned blobs cannot be loaded without `QCHEM_ALLOW_LEGACY_PICKLE=1` during the migration window.

## Scaling beyond SQLite

Default deployments use `SqliteJobStore` under `QCHEM_STACK_DB_DIR`. For multiple workers or HA:

| Concern | Guidance |
|---------|----------|
| Interface | Implement `JobStore` (`enqueue`, `result`) — see [job_store_extension.md](job_store_extension.md) |
| Worker coordination | Atomic job claim (`QUEUED` → `RUNNING`); never run the same `job_id` on two workers |
| Protocol blobs | Keep HMAC signing; offload large payloads to object storage |
| Timeline / HTTP | Preserve `timeline_json` for `/v1/runs/{id}/events` |
| Migration | Dual-write or drain queue before cutover; rotate `QCHEM_PROTOCOL_HMAC_KEY` deliberately |

Full extension sketch: [job_store_extension.md](job_store_extension.md).

## Related

- [HTTP API contract (Chinese)](../技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)
- [ENGINEERING_ARCHITECTURE.md §9](ENGINEERING_ARCHITECTURE.md)
- [v1.1.0 acceptance checklist](v1_1_acceptance.md)
- [v1.0.x → v1.1.0 migration](migration_v1_0_to_v1_1.md)
