# HTTP API Quick Reference (English)

Authoritative contract (Chinese): [`docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md).

## Start server

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## Endpoints

| Method | Path | Response `schema` | Notes |
|--------|------|-------------------|-------|
| GET | `/health` | — | Liveness |
| GET | `/health/ready` | — | SQLite ping |
| GET | `/v1/meta/product-surface` | `product_surface_v1` | Route pointers |
| GET | `/v1/meta/capability-surface` | `capability_surface_v2` | Capability map + gaps |
| GET | `/v1/meta/parity-gaps` | `capability_gap_export_v1` | Gaps only |
| POST | `/v1/meta/workflow-preview` | `workflow_preview_v1` | YAML-only preview |
| GET | `/v1/meta/queue-stats` | `queue_stats_v1` | Queue depth |
| POST | `/v1/runs` | `run_enqueue_response_v1` (202) | **Default: async enqueue** |
| POST | `/v1/runs/sync` | `full_pipeline_job_result_v1` (200) | Deprecated sync debug |
| GET | `/v1/runs/{id}/status` | `job_status_v1` | Poll status |
| GET | `/v1/runs/{id}/repro` | `run_repro_only_v1` | 409 until DONE |

## Submit async run

```bash
curl -sS -X POST http://127.0.0.1:8000/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"experiment_yaml": "schema_version: \"2\"\n..."}'
```

Set `"sync": true` on `POST /v1/runs` only for localhost debugging (returns `Deprecation: true` header).

## Environment

See [`docs/说明_API安全与环境变量.md`](说明_API安全与环境变量.md).
