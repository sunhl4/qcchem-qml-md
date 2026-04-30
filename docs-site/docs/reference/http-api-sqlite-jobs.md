# 技术文档：HTTP API、SQLite 作业队列与管线可观测性（开放契约）

**文档性质**：描述可选 **`qchem-stack[api]`** 面与 **`jobs`** 存储的**可机读契约**；与 [ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture)（英文化分层）互补，本文偏**产品化 HTTP + 观测字段**与**竞品语义对照**。

**竞品对照（公开文档口径）**：[launch_retrieve_nexus_analog.md](/concept/launch-retrieve-nexus-analog)、[inquanto_public_parity_matrix.md](/parity/public-matrix)。**不**声称实现 Quantinuum Nexus 真队列、真 HQC 或 OAuth。

**源码入口**：`src/qchem_stack/api/app.py`、`src/qchem_stack/jobs/`、`src/qchem_stack/orchestration/run_context.py`、`src/qchem_stack/orchestration/pipeline.py`（`_attach_run_summary`、`run_pipeline_sync`）。

---

## 1. 边界与非目标

| 项目 | 本栈做法 | 刻意不做 |
|------|----------|----------|
| 身份与配额 | 无；绑定 `127.0.0.1` + 文档要求边缘鉴权 | Nexus 项目 IAM、合同限额 |
| 作业存储 | 本地 SQLite，FIFO `QUEUED` | Redis/Celery/多云主从 |
| 全量结果 | `full_pipeline` 入库为 **白名单** `full_pipeline_job_result_v1` | 无界 `pickle`/`QubitHamiltonian` 落库 |
| 事件流 | 新作业 **`jobs.timeline_json`**：`submitted` / `running` / **`pipeline_stage`**（`stage` 与 `run_pipeline_sync` 一致）/ `completed` / `failed` / `retry_scheduled`；`GET …/events` 透传字段 | 与云侧完整审计等价 |
| OpenTelemetry | 仅 **`trace_id` 字符串** 与可选 `traceparent` 解析 | OTel SDK 强依赖 |

---

## 2. 可观测性：`run_context` 与 `pipeline_profile`

写入位置：`out["repro"]`（同步管线、全管线异步 **DONE** 结果均含；若 Pauli pickle 作业结果无 `repro` 则本节不适用）。

### 2.1 `repro["run_context"]`（`run_context_v1`）

| 键 | 类型 | 说明 |
|----|------|------|
| `schema` | `"run_context_v1"` | 固定 |
| `trace_id` | `str` | UUID 或 W3C `traceparent` 中 32 hex |
| `client_request_id` | `str`（可选） | `X-Request-ID` 等 |

来源：`RunContext.from_headers(...)`（HTTP）；或 `run_pipeline_sync(..., run_context=...)`。`run_summary` 镜像短字段 `trace_id` / `client_request_id` 便于单行检索。

### 2.2 `repro["pipeline_profile"]`（`pipeline_profile_v1`）

| 键 | 说明 |
|----|------|
| `schema` | `"pipeline_profile_v1"` |
| `stages` | `list[{stage, duration_ms}]`，相邻 `mark` 间隔 |
| `total_wall_ms` | 总墙钟近似（与 `stages` 求和一致） |

**约定阶段名（非穷举）**：`scf_done`、`hamiltonian_built`、`variational_done`、`embedding_dmet` / `embedding_none`、`excited_stages`、`pre_pauli_protocol`、`pauli_protocol_done` / `pauli_protocol_skipped`、`finalize_repro` 等。

`run_summary` 可选：`pipeline_total_wall_ms`、`pipeline_slowest_stage`、`pipeline_slowest_stage_ms`。

**严格 JSON**：`repro` 大块应经 `repro_json_dumps` 再进对象存储/Kafka（见 [ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture) §4）。

---

## 3. SQLite：`SqliteJobStore`

### 3.1 `job_kind`

- `pauli_protocol`（默认）：payload 为 pickle 协议体；与 `protocol_hash` 列对齐。
- `full_pipeline`：payload 为 UTF-8 JSON，`config_yaml` + 可选 `run_context`。

### 3.2 `meta`（JSON）

HTTP 异步入队常见键：

| 键 | 来源 |
|----|------|
| `trace_id` | `RunContext` |
| `experiment_id` | 校验后的 `ExperimentConfig.experiment_id` |
| `nexus_analog_project_label` | YAML `nexus_analog.project_label`（若启用） |
| `api_workspace_label` | POST body `workspace_label`（竞品「项目」类比，trim，≤400 字符） |

### 3.3 列表与过滤

- `list_jobs(status=?, job_kind=?, experiment_id=?, api_workspace_label=?, api_project_slug=?, limit=, offset=)`：按 `created DESC`。
- `experiment_id` / `api_workspace_label`：优先 `json_extract(meta, '$.<key>')`；失败时回退扫描（上限见 `jobs/store.py` 中 `_JSON_SCAN_CAP`）。

### 3.4 运维 API

- `count_by_status()` → `GROUP BY status`。
- `get_job_public_summary(job_id)`：无 payload/result BLOB，适合高频轮询。

---

## 4. Worker：`dispatch_job`

- `qchem-jobs-worker` / `qchem-pipeline-worker`：`drain_one_queued` → `jobs/worker_dispatch.dispatch_job`。
- `full_pipeline` → `run_full_pipeline_job` → `pipeline_result_for_job_store` → `complete`。
- 结果白名单含 **`nexus_analog_ledger`**、缓解/张量网/QPE 侧车等键（与同步管线对齐）；与 [pipeline 侧挂接](/concept/engineering-memory-quantinuum)一致。

---

## 5. HTTP API 一览（`schema` 契约）

| 方法 | 路径 | `schema`（响应体内或约定） |
|------|------|----------------------------|
| GET | `/health` | — |
| GET | `/health/ready` | — |
| GET | `/v1/meta/capability-surface` | `capability_surface_v1`（`object_map` + `gaps` + `mitigation_execution_model` + `open_stack_differentiators`） |
| GET | `/v1/meta/parity-gaps` | `inquanto_gap_export_v1` |
| GET | `/v1/meta/product-analog` | `product_analog_v1` |
| POST | `/v1/meta/workflow-preview` | `workflow_preview_v1`（五阶段 + `computable_graph_v2` + 可选 YAML 边覆盖 + `computable_abstract`） |
| POST | `/v1/meta/computables-preview` | `computables_preview_v1`（内嵌 `computable_abstract` v2） |
| GET | `/v1/meta/queue-stats` | `queue_stats_v1` |
| GET | `/v1/runs` | `job_list_v1`（含 `limit`/`offset` 回显） |
| POST | `/v1/runs` | 同步：`full_pipeline_job_result_v1`；异步 **202**：`run_enqueue_response_v1` |
| GET | `/v1/runs/{id}/status` | `job_status_v1` |
| GET | `/v1/runs/{id}/summary` | `run_product_summary_v1`（`DONE` 为完整 slim；排队中为 `partial`；可含 `api_labels`） |
| GET | `/v1/runs/{id}/events` | `job_events_v1`（`note`=`sqlite_timeline_json_v1` 或 `sqlite_coarse_timeline_v1`） |
| GET | `/v1/runs/{id}/repro` | `run_repro_only_v1`（仅 `DONE`；否则 **409**） |
| GET | `/v1/runs/{id}` | `SqliteJobStore.result` 合并形（`DONE` 时混用结果 JSON） |

**响应头（成功 POST `/v1/runs`）**：`X-Trace-ID`；若请求带 client id 则 `X-Request-ID`。

**Computable 图声明式覆盖（可选）**：`quantum.computable_extra_edges`（追加边）、`quantum.computable_remove_edges`（按 name 删自动边）— 仅影响 `workflow-preview` / `computable_graph_v2` 与控制台，**不**改变管线执行顺序。

**校验**：异步入队前与同步相同路径校验 YAML → `ExperimentConfig`（**400** / **422**）。**422** 亦用于 `QChemStackError` 同步管线失败。

---

## 6. 网关映射建议（可选实现）

| HTTP | 条件 |
|------|------|
| 400 | YAML 非 mapping / 解析失败 |
| 404 | 未知 `job_id` |
| 409 | `/repro` 且 `status != DONE` |
| 422 | Pydantic、`QChemStackError` |
| 503 | `/health/ready` 存储不可用 |

---

## 7. 启动与环境

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

- 环境变量 **`QCHEM_JOB_DB`**：默认队列 SQLite 路径兜底。

---

## 8. 维护清单（变更时同步）

1. 增删 HTTP 路由或响应 `schema`：更新本文 **§5**、[ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture) §9、[README.md](/tutorial/quickstart) HTTP 段、[launch_retrieve_nexus_analog.md](/concept/launch-retrieve-nexus-analog) 表格（若行为类比变）。
2. 增减 `meta` 键或 `full_pipeline_job_result_v1` 白名单：更新 **`pipeline_runner.py`**、[ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture) §10。
3. 观测字段变更：更新 **§2**、`tests/test_observability_pipeline.py`（PySCF）、`tests/test_api_runs.py`（FastAPI）。
4. 机读差距分类：视需要更新 `inquanto_contract.inquanto_gap_categories()` 与 [inquanto_public_parity_matrix.md](/parity/public-matrix)。

---

*版本：与仓库实现同步；重大行为变更时请 bump 本文 §5 表、§8 清单及交叉文档。*
