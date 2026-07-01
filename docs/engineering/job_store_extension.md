# Job store extension guide

This note describes how to scale beyond the default SQLite implementation while keeping the public job API stable.

## `JobStore` protocol

Defined in [`store_schema.py`](../../src/qchem_stack/jobs/store_schema.py):

| Method | Purpose |
|--------|---------|
| `enqueue(job_id, payload, protocol_hash=None)` | Persist a queued job; returns `JobHandle` |
| `result(job_id)` | Load completed job result mapping |

Reference implementation: `SqliteJobStore` in [`store_service.py`](../../src/qchem_stack/jobs/store_service.py).

Production HA reference: `PostgresJobStore` in [`store_postgres.py`](../../src/qchem_stack/jobs/store_postgres.py) (`pip install qchem-stack[jobs-postgres]`, schema in [`scripts/init_postgres_jobs.sql`](../../scripts/init_postgres_jobs.sql)).

Worker CLI:

```bash
qchem-jobs-worker --db /data/jobs.sqlite          # SQLite (default)
qchem-jobs-worker --db-url postgresql://...       # Postgres
```

## When to replace SQLite

| Signal | Action |
|--------|--------|
| Single worker on one host | Default SQLite + `QCHEM_STACK_DB_DIR` volume |
| Multiple workers | External store with atomic claim / lease semantics |
| Large protocol blobs | Object storage for payload bytes; DB holds pointer + HMAC metadata |
| HA / failover | Replicated SQL or managed queue (Postgres, Redis stream, SQS analog) |

## Extension sketch (PostgresJobStore)

```python
class PostgresJobStore:
    def enqueue(self, job_id: str, payload: bytes, protocol_hash: str | None = None) -> JobHandle:
        # INSERT INTO jobs (...) VALUES (...,'QUEUED',...)
        return JobHandle(job_id=job_id, protocol_hash=protocol_hash)

    def result(self, job_id: str) -> dict[str, object]:
        # SELECT result_blob FROM jobs WHERE job_id = %s AND status = 'DONE'
        ...
```

Workers should continue to call `process_job_with_retry` dispatch logic; only the persistence layer changes.

## Migration checklist

1. **Protocol blobs** — HMAC-signed v1/v2 only ([protocol_pickle_migration.md](protocol_pickle_migration.md)).
2. **`QCHEM_PROTOCOL_HMAC_KEY`** — rotate with dual-read window if needed.
3. **`timeline_json`** — preserve enqueue / run / complete / retry events for HTTP `/v1/runs/{id}/events`.
4. **Multi-worker** — use `UPDATE ... WHERE status='QUEUED' RETURNING` (or equivalent) to avoid double execution.
5. **Blob storage** — store `s3://` or `file://` URI in `payload` column when rows exceed SQLite BLOB limits.

## Related

- [production_deployment.md](production_deployment.md)
- [HTTP API contract (Chinese)](../技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)
- [`tests/jobs/test_job_store_protocol_conformance.py`](../../tests/jobs/test_job_store_protocol_conformance.py)

**CI:** the `integration` workflow runs Postgres conformance tests (`test_job_store_postgres.py` + `test_job_store_protocol_conformance.py`) against a `postgres:15` service when `QCHEM_JOB_DATABASE_URL` is set.
