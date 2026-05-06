---
title: Async run via HTTP
description: POST /v1/runs, then poll status / summary until DONE or failure
---

Prerequisites: install the optional **`[api]`** extra and run the worker as in [HTTP API · SQLite jobs](/en/reference/http-api-sqlite-jobs) (localhost binding by default).

## 1. Submit

`POST /v1/runs` with a JSON body that satisfies the contract (typically `config_yaml` for full-pipeline jobs). **202** + `run_enqueue_response_v1` means queued async; a synchronous completion returns `full_pipeline_job_result_v1` directly.

Capture **`X-Trace-ID`** (and optional **`X-Request-ID`**) from response headers for log correlation.

## 2. Poll

1. **`GET /v1/runs/{id}/status`** → `job_status_v1` until terminal or failure.  
2. Product-facing digest: **`GET /v1/runs/{id}/summary`** → `run_product_summary_v1` (`DONE` = full slim; queued = `partial`).  
3. Timeline: **`GET /v1/runs/{id}/events`** → `job_events_v1`.

## 3. Fetch repro

Call **`GET /v1/runs/{id}/repro`** only after **`DONE`** (otherwise **409**). Merged result shape: **`GET /v1/runs/{id}`** — see [HTTP API reference](/en/reference/http-api-sqlite-jobs).

## 4. Next

- [CLI & scripts](/en/reference/cli-and-scripts) — worker flags and smoke scripts  
- [P4 Jobs & reproducibility](/en/guide/jobs-and-reproducibility/) — `repro` semantics  

Authoritative endpoint tables remain in the Reference page.
