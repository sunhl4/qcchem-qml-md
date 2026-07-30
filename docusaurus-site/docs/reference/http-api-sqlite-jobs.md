---
title: HTTP API、SQLite 作业队列与可观测性
description: qchem-stack 服务化接口契约，包含 runs API、作业状态、可观测字段和集成建议。
keywords:
  - FastAPI
  - SQLite
  - jobs
  - observability
---

# HTTP API、SQLite 作业队列与可观测性

> **Authoritative repo contract**: [`docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md). English summary: [`docs/QUICKSTART_HTTP_API_en.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/QUICKSTART_HTTP_API_en.md).

本文是 `qchem_stack.api` 与 `qchem_stack.jobs` 的工程契约摘要，用于服务化集成与运维对接。

## 适用场景

- 你要把 pipeline 接入外部服务或网关
- 你要做异步作业提交、轮询和结果拉取
- 你要建立可追踪、可复盘的运行证据链

## 边界

- 当前是本地/私有部署友好的 FastAPI + SQLite 路径
- 不等价于商业云平台 IAM、OAuth、配额与计费体系
- 强调可复现与可审计，而非闭源产品功能复刻

## 鉴权、CORS 与限流（生产）

| 环境变量 | 作用 |
|----------|------|
| `QCHEM_STACK_API_KEY` | 请求需带匹配 API Key（见中间件） |
| `QCHEM_STACK_REQUIRE_API_KEY` | 设为真时：**启动时**若缺 `QCHEM_STACK_API_KEY` 则失败 |
| `QCHEM_STACK_CORS_ORIGINS` | 允许的 CORS 来源列表（逗号分隔）；**不要**与 credentials 一起用 `*` |
| `QCHEM_STACK_CORS_CREDENTIALS` | 是否允许 credentials（显式 origins） |

限流：`slowapi` 装饰器挂在 runs / meta / ml_md 路由（见 `api/middleware.py` 中 `RUNS_*_LIMIT`、`META_POST_LIMIT` 等）。超限返回 429。

```bash
export QCHEM_STACK_REQUIRE_API_KEY=1
export QCHEM_STACK_API_KEY='replace-me'  # pragma: allowlist secret
export QCHEM_STACK_CORS_ORIGINS='https://docs.example.com'
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

默认仅建议绑定 `127.0.0.1`；对外请放在反向代理后。未设 API Key 时进程会打 warning（开发便利，非生产默认）。

## 可观测字段

| 字段 | 说明 |
|------|------|
| `trace_id` | 贯穿请求与执行链路的追踪 ID |
| `client_request_id` | 网关透传的请求标识 |
| `pipeline_profile` | 分阶段耗时与总耗时 |
| `run_summary` | 结果摘要与关键指标 |

## 端点总览

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/health` | 存活检查 |
| GET | `/health/ready` | 就绪检查（含存储可用性） |
| GET | `/v1/meta/product-surface` | 产品面路由指针摘要 |
| GET | `/v1/meta/capability-surface` | 能力面聚合：`schema`=`capability_surface_v2`；载荷含 `capability_map`、`gaps`、`gap_anchor_index_v1`、`mitigation_execution_model`、`open_stack_differentiators`、`operator_pool_registry_export_v1`、`algorithm_registry_export_v1`、`variational_registry_export_v1`、`uccsd_mapping_support_matrix_v1` |
| GET | `/v1/meta/parity-gaps` | 仅差距列表 |
| POST | `/v1/meta/workflow-preview` | YAML 预览五阶段与 computable 图 |
| POST | `/v1/meta/computables-preview` | YAML 预览 computable 列表 |
| GET | `/v1/meta/queue-stats` | 队列状态计数 |
| GET | `/v1/runs` | 作业列表与分页 |
| POST | `/v1/runs` | 提交同步或异步运行（`sync`） |
| GET | `/v1/runs/{id}/status` | 轻量状态查询 |
| GET | `/v1/runs/{id}/events` | 时间线事件 |
| GET | `/v1/runs/{id}/summary` | 产品侧摘要视图 |
| GET | `/v1/runs/{id}/repro` | DONE 后拉取 repro |
| GET | `/v1/meta/ml-md-bridge` | QMEF / MLIP stub 能力面（JSON） |
| POST | `/v1/meta/qmef-validate` | 校验 `QMEFDataset` JSON |
| POST | `/v1/meta/ml-md-trainer-stub-fit` | 内存 stub 训练演示（不落盘） |
| GET | `/v1/runs/{id}` | 原始结果行（完整） |

## `POST /v1/runs` 请求体（准确字段）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `experiment_yaml` | string | 是 | 完整 YAML 文本，不是文件路径 |
| `sync` | bool | 否 | `true` 同步执行；默认 `false` 入队 |
| `job_db_path` | string | 否 | SQLite 路径；默认环境变量或临时目录 |
| `workspace_label` | string | 否 | 写入作业 meta，用于筛选 |
| `project_slug` | string | 否 | 写入作业 meta，用于筛选 |

## 最小请求示例（异步）

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/runs" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "experiment_yaml": "experiment_id: demo-api\nmolecule:\n  symbols: [H, H]\n  geometry_bohr:\n    - [0.0, 0.0, 0.0]\n    - [0.0, 0.0, 1.4]\n",
  "sync": false
}
JSON
```

异步返回 `202`，包含 `job_id`、`status=QUEUED`、`trace_id`。

## 查询示例

```bash
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/status"
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/summary"
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/repro"
```

## 关键端点响应示例（可联调）

以下示例按当前实现整理，字段可能在未来版本扩展，但 `schema` 与主键语义应保持稳定。

### `POST /v1/runs`（异步）`202`

```json
{
  "schema": "run_enqueue_response_v1",
  "job_id": "job_20260508_abc123",
  "experiment_id": "demo-api",
  "trace_id": "demo-async-001",
  "client_request_id": null,
  "status": "QUEUED",
  "job_db": "/tmp/qchem_api_jobs.sqlite"
}
```

响应头会包含：`X-Trace-ID`（若请求头有 request id，也会回 `X-Request-ID`）。

### `GET /v1/runs/{job_id}/status` `200`

```json
{
  "schema": "job_status_v1",
  "job_id": "job_20260508_abc123",
  "status": "RUNNING",
  "job_kind": "full_pipeline",
  "created": 1746709101.12,
  "updated": 1746709103.44,
  "retry_count": 0,
  "meta": {
    "experiment_id": "demo-api",
    "api_workspace_label": "team-a"
  }
}
```

### `GET /v1/runs/{job_id}/events` `200`

```json
{
  "schema": "job_events_v1",
  "job_id": "job_20260508_abc123",
  "note": "sqlite_timeline_json_v1",
  "events": [
    {"t": 1746709101.12, "kind": "submitted", "status": "QUEUED"},
    {"t": 1746709102.03, "kind": "running", "status": "RUNNING"}
  ]
}
```

### `GET /v1/runs/{job_id}/summary` `200`

`summary` 在未完成时也会返回（`partial=true`），便于前端先展示状态。

```json
{
  "schema": "run_product_summary_v1",
  "status": "DONE",
  "job_kind": "full_pipeline",
  "experiment_id": "demo-api",
  "partial": false,
  "algorithm": "vqe",
  "energy_after_variational": -1.137,
  "energy_pauli_protocol": -1.136,
  "run_summary": {
    "energy_after_variational": -1.137
  },
  "trace_id": "demo-async-001",
  "sidecars_present": {
    "nexus_analog_ledger": false,
    "mitigation_graph_report": false,
    "mitigation_dag_execution": false,
    "tensornet_protocol_stub": false,
    "qpe_demo_track": false,
    "vqs_track": false
  }
}
```

### `GET /v1/runs/{job_id}/repro` `200`（仅 DONE）

```json
{
  "schema": "run_repro_only_v1",
  "job_id": "job_20260508_abc123",
  "job_kind": "full_pipeline",
  "repro": {
    "experiment_id": "demo-api",
    "run_context": {"trace_id": "demo-async-001"},
    "pipeline_profile": {"total_s": 1.23},
    "run_summary": {"energy_after_variational": -1.137}
  }
}
```

任务未完成时会返回 `409`：

```json
{
  "detail": {
    "message": "repro available when job status is DONE",
    "status": "RUNNING"
  }
}
```

### `GET /v1/runs`（分页）

```json
{
  "schema": "job_list_v1",
  "job_db": "/tmp/qchem_api_jobs.sqlite",
  "limit": 50,
  "offset": 0,
  "jobs": [
    {
      "job_id": "job_20260508_abc123",
      "status": "DONE",
      "job_kind": "full_pipeline",
      "created": 1746709101.12,
      "updated": 1746709109.55,
      "protocol_hash": "5a8d..."
    }
  ]
}
```

## 状态码建议

- `400`：YAML 解析错误或请求体不合法
- `404`：作业不存在
- `409`：作业未完成但请求了仅完成态可读的数据
- `422`：配置校验失败或管线业务错误
- `503`：`/health/ready` 存储不可用

## 快速运行

```bash
pip install -e ".[api]"
```

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 最小自检（curl）

```bash
curl -sS "http://127.0.0.1:8000/health"
curl -sS "http://127.0.0.1:8000/v1/runs"
```

## 排障建议

- **频繁 422**：先在本地跑最小配置并校验 YAML 字段
- **`repro` 取不到（409）**：任务还没 DONE，先查 `/status`
- **404 但明明提交过**：检查 `job_db_path` 是否和提交时一致
- **任务积压**：检查 worker 是否启动、是否连接同一个 SQLite
- **readiness 失败**：检查 `QCHEM_JOB_DB` 路径权限与磁盘可写性

## 关联页面

- [HTTP 异步运行教程](/tutorial/async-run-via-http)
- [P4 作业与可复现](/guide/jobs-and-reproducibility)
- [命令行与脚本](/reference/cli-and-scripts)
