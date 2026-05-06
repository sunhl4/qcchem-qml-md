---
title: Ten repro keys to read first
description: Navigate exported JSON for schema, tracing, and stages — not a substitute for Reference
---

`out["repro"]` (and HTTP **`GET …/repro`**) is the **machine-readable** reproducibility bundle. These ten **areas** help you orient before diving into [Reference](/en/reference/http-api-sqlite-jobs) and source (exact key names follow the current schema).

| # | Focus | Typical keys / blocks |
|---|--------|------------------------|
| 1 | Block schema | `schema` strings (e.g. `run_context_v1`) |
| 2 | Tracing | `trace_id`, `client_request_id` under `run_context` |
| 3 | Stage timing | `pipeline_profile`: `stages`, `total_wall_ms` |
| 4 | Experiment id | `experiment_id`, `random_seed`, `schema_version` (when mirrored) |
| 5 | Backend / shots | Summary fields aligned with `backend` / `shots` |
| 6 | Mitigation / compile | Whitelisted summary slices |
| 7 | Embedding | e.g. `embedding.mode` summaries when applicable |
| 8 | Parity export | `parity_export_schema_version`, `inquanto_gap_categories`, … |
| 9 | Protocol hashes | `protocol_hash`, Pauli job metadata (async paths) |
| 10 | Errors / retry | Short `error` / retry fields on failure branches |

**Strict JSON**: use `repro_json_dumps` before handing `repro` to external storage (see HTTP API doc).

More: [HTTP API](/en/reference/http-api-sqlite-jobs) · [DMET · parity_snapshot](/en/reference/dmet-parity-snapshot).
