---
title: OpenAPI
description: FastAPI auto-generated OpenAPI schema when the optional API extra is installed.
---

# OpenAPI

With `pip install "qchem-stack[api]"`:

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

- Interactive docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Since **1.0.0**, JSON responses under `/v1/*` include `api_contract_version: "1.0"`.

CI keeps a checked-in snapshot at `docs/generated/openapi_snapshot.json` (`python scripts/generate_openapi_snapshot.py`).

Contract tables for stable routes remain in the repository engineering docs under `docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`.
