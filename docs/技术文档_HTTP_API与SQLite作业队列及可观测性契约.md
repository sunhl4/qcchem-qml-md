# 技术文档：HTTP API、SQLite 作业队列与管线可观测性（开放契约）

**文档性质**：描述可选 **`qchem-stack[api]`** 面与 **`jobs`** 存储的**可机读契约**；与 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md)（英文化分层）互补，本文偏**产品化 HTTP + 观测字段**与**竞品语义对照**。
1
**竞品对照（公开文档口径）**：[launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md)、[inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)。**不**声称实现 Quantinuum Nexus 真队列、真 HQC 或 OAuth。

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

**严格 JSON**：`repro` 大块应经 `repro_json_dumps` 再进对象存储/Kafka（见 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §4）。

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
| `api_workspace_label` | POST body `workspace_label`（竞品「工作区」类比，trim，≤400 字符） |
| `api_project_slug` | POST body `project_slug`（竞品「项目 slug」类比，trim，**≤200** 字符；与 `workspace_label` 一并用于 `GET /v1/runs` 过滤；真源 `app.py` `post_run`） |

### 3.3 列表与过滤

- `list_jobs(status=?, job_kind=?, experiment_id=?, api_workspace_label=?, api_project_slug=?, limit=, offset=)`：按 **`created DESC, rowid DESC`**（`created` 相同时保证**后入队**优先，避免同秒双作业顺序抖动）。
- `experiment_id` / `api_workspace_label` / `api_project_slug`：优先 `json_extract(meta, '$.<key>')`；失败时回退扫描（上限见 `jobs/store.py` 中 `_JSON_SCAN_CAP`）。

### 3.4 运维 API

- `count_by_status()` → `GROUP BY status`。
- `get_job_public_summary(job_id)`：无 payload/result BLOB，适合高频轮询。

---

## 4. Worker：`dispatch_job`

- `qchem-jobs-worker` / `qchem-pipeline-worker`：`drain_one_queued` → `jobs/worker_dispatch.dispatch_job`。
- `full_pipeline` → `run_full_pipeline_job` → `pipeline_result_for_job_store` → `complete`。
- 结果白名单含 **`nexus_analog_ledger`**、缓解/张量网/QPE 侧车等键（与同步管线对齐）；与 [pipeline 侧挂接](工程记忆_Quantinuum对标与数据流技术文档.md)一致。

---

## 5. HTTP API 一览（`schema` 契约）

**真源**：`src/qchem_stack/api/app.py`（FastAPI）。下表为 **响应体顶层 `schema` 字段** 与主要负载；与 OpenAPI 不一致时以代码为准。

| 方法 | 路径 | `schema`（响应体内或约定） |
|------|------|----------------------------|
| GET | `/health` | 无 `schema`；体为 `{"status":"ok"}` |
| GET | `/health/ready` | 无 `schema`；体为 `{"status":"ready","job_db_default":...}`；SQLite ping 失败 → **503** |
| GET | `/v1/meta/capability-surface` | `capability_surface_v1`（`qchem_stack_version`、`object_map`、`gaps`、`mitigation_execution_model`、`open_stack_differentiators`、`operator_pool_registry_export_v1`） |
| GET | `/v1/meta/parity-gaps` | `inquanto_gap_export_v1`：`qchem_stack_version`、`gaps` |
| GET | `/v1/meta/product-analog` | `product_analog_v1`（控制台用路由指针 + `emulation_notes`） |
| POST | `/v1/meta/workflow-preview` | `workflow_preview_v1`（五阶段 + `computable_graph_v2` + 可选 YAML 边覆盖 + `computable_abstract`；可选 `computables_rich`） |
| POST | `/v1/meta/computables-preview` | `computables_preview_v1`（`experiment_id`、`computables[]`、`computable_abstract` v2） |
| GET | `/v1/meta/ml-md-bridge` | `ml_md_bridge_surface_v1`（QMEF / 导出器 / stub trainer 指针） |
| POST | `/v1/meta/qmef-validate` | `qmef_validate_v1`（请求体 `{ "qmef": { … } }`） |
| POST | `/v1/meta/ml-md-trainer-stub-fit` | `ml_md_trainer_stub_fit_v1`（内存 stub ``fit``；**不落盘** checkpoint） |
| GET | `/v1/meta/queue-stats` | `queue_stats_v1`：`job_db`、`counts` |
| GET | `/v1/runs` | `job_list_v1`（`job_db`、`limit`、`offset`、`jobs`） |
| POST | `/v1/runs` | 同步 **200**：`full_pipeline_job_result_v1`；异步 **202**：`run_enqueue_response_v1` |
| GET | `/v1/runs/{id}/status` | `job_status_v1`（`get_job_public_summary` 展开字段） |
| GET | `/v1/runs/{id}/summary` | `run_product_summary_v1`（非 `DONE` 时 `partial`；`DONE` 为完整 slim；可含 `api_labels`） |
| GET | `/v1/runs/{id}/events` | `job_events_v1`（`note`=`sqlite_timeline_json_v1` 或 `sqlite_coarse_timeline_v1`） |
| GET | `/v1/runs/{id}/repro` | `run_repro_only_v1`（仅 `DONE`；否则 **409**） |
| GET | `/v1/runs/{id}` | 无统一 `schema`；为 `SqliteJobStore.result(job_id)` 原始合并字典 |

### 5.1 路由 ↔ 实现函数（维护用）

| 路径 | `app.py` 中处理函数 |
|------|---------------------|
| `GET /health` | `health` |
| `GET /health/ready` | `ready` |
| `GET /v1/meta/product-analog` | `product_analog` |
| `GET /v1/meta/capability-surface` | `capability_surface` |
| `GET /v1/meta/parity-gaps` | `parity_gaps` |
| `POST /v1/meta/workflow-preview` | `workflow_preview` |
| `POST /v1/meta/computables-preview` | `computables_preview` |
| `GET /v1/meta/ml-md-bridge` | `ml_md_bridge_meta` |
| `POST /v1/meta/qmef-validate` | `qmef_validate` |
| `POST /v1/meta/ml-md-trainer-stub-fit` | `ml_md_trainer_stub_fit` |
| `GET /v1/meta/queue-stats` | `queue_stats` |
| `GET /v1/runs` | `list_runs` |
| `POST /v1/runs` | `post_run` |
| `GET /v1/runs/{job_id}/status` | `get_run_status` |
| `GET /v1/runs/{job_id}/events` | `get_run_events` |
| `GET /v1/runs/{job_id}/summary` | `get_run_summary_ux` |
| `GET /v1/runs/{job_id}/repro` | `get_run_repro` |
| `GET /v1/runs/{job_id}` | `get_run` |

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

1. 增删 HTTP 路由或响应 `schema`：更新本文 **§5**、[ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §9、[README.md](../../README.md) HTTP 段、[launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md) 表格（若行为类比变）。
2. 增减 `meta` 键或 `full_pipeline_job_result_v1` 白名单：更新 **`pipeline_runner.py`**、[ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §10。
3. 观测字段变更：更新 **§2**、`tests/test_observability_pipeline.py`（PySCF）、`tests/test_api_runs.py`（FastAPI）。
4. 机读差距分类：视需要更新 `inquanto_contract.inquanto_gap_categories()` 与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)。

---

## 9. 工程决策与范围（原独立「HTTP 工程记忆」合并）

本节为 **维护者决策备忘**（与 §1「边界」互补）；对外契约仍以 **§2–§7** 为准。

### 9.1 为什么做这一层

- **竞品叙事**：InQuanto/Nexus 公开资料强调「提交作业 → 轮询状态 → 取结果」与 **Methods/Computable** 可追溯性。本栈在**不引入真云**的前提下，用 **FastAPI + SQLite + 既有 `repro`** 提供**可审计的本地类比**。
- **与「只做库」的关系**：`run_pipeline_sync` 仍是稳定核心；HTTP 与 `full_pipeline` 作业是 **optional extra**（`pip install qchem-stack[api]`），避免把 Web 框架强加给嵌入用户。

### 9.2 已定决策（摘要）

| 决策 | 内容 |
|------|------|
| 同步 POST 返回体 | `pipeline_result_for_job_store`，与异步 **DONE** 同形，保证 **JSON 可序列化** |
| 异步入队前校验 | 与同步共用 `ExperimentConfig`，避免垃圾任务占队列 |
| `traceparent` | `RunContext.from_headers` 优先解析，其次 `X-Trace-ID`，否则新 UUID |
| `GET …/repro` | 仅 `DONE`，否则 **409**，方便 Methods 流水线只拉 `repro` |
| `GET …/events` | **不**承诺完整事件流；仅 `created`/`updated` 合成两点 |
| `experiment_id` + workspace 过滤 | SQL `json_extract` + 老 SQLite **扫描回退**（有上限） |
| 竞品差距机读 | `GET /v1/meta/parity-gaps` 与 `inquanto_gap_categories()` 同内容源 |

### 9.3 明确不做（避免范围漂移）

- **不做** Nexus/qnexus 真 SDK、真 HQC 货币、多租户项目隔离。
- **不做** 全量 `out` 落库（白名单在 `pipeline_runner.pipeline_result_for_job_store`）。
- **不做** Celery/Redis 默认实现（未来可抽象 `JobStore` Protocol 第二实现，不在此包范围）。
- **不强依赖** OpenTelemetry SDK；字段名预留与云网关对齐即可。

### 9.4 与其它文档的分工

| 文档 | 职责 |
|------|------|
| [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) | 英文化分层、稳定公共面、错误类型 |
| **本文** | 中文 **schema/端点/存储** 契约 + 上表决策 |
| [launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md) | Nexus **语义**短表 |
| [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) | 公开能力矩阵 |
| [工程记忆_Quantinuum对标与数据流技术文档.md](工程记忆_Quantinuum对标与数据流技术文档.md) | 化学/Protocol/数据流总记忆 |

### 9.5 变更 Checklist（逐项打勾）

- [ ] 修改 `api/app.py`：同步 **本文 §5**、**ENGINEERING §9**、**README HTTP 段**；必要时 **launch 对照表**。
- [ ] 修改 `jobs/store.py` 行为：同步 **本文 §3**、**ENGINEERING §10**；单测 `test_job_store_list.py`、`test_api_runs.py`。
- [ ] 修改 `run_context` / `pipeline_profile`：同步 **本文 §2**、**ENGINEERING §8**、`test_observability_pipeline.py`。
- [ ] 修改 `pipeline_runner._RESULT_KEYS`：同步 **本文 §4 / §8**、README 若有「侧车」表述。
- [ ] 产品矩阵行级变更：更新 **inquanto_public_parity_matrix.md**；机读条更新 **inquanto_gap_categories()**。

### 9.6 测试与 CI

- FastAPI：`tests/test_api_runs.py`（`importorskip("fastapi")`）。
- 存储：`tests/test_job_store_list.py`、`tests/test_store_experiment_meta.py`。
- 全流程（PySCF）：`tests/test_pipeline_job_store.py`、`tests/test_observability_pipeline.py`。
- CI：见 `.github/workflows/ci.yml`（`pip install -e ".[dev]"` 已含 `api` 依赖链）。

---

*版本：与仓库实现同步；重大行为变更时请 bump 本文 §5 表、§8–§9 及交叉文档。（原 `记忆_HTTP_API与作业队列_工程记忆.md` 已合并至 §9。）*
