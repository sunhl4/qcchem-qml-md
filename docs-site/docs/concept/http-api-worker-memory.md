# 工程记忆：HTTP API、全管线异步作业与可观测性字段

**文档性质**：给维护者的**决策与同步清单**（非对外 API 合同正文）。合同细节见 [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs) 与 [ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture) §8–10。

---

## 1. 为什么做这一层

- **竞品叙事**：InQuanto/Nexus 公开资料强调「提交作业 → 轮询状态 → 取结果」与 **Methods/Computable** 可追溯性。我们在**不引入真云**的前提下，用 **FastAPI + SQLite + 既有 `repro`** 提供**可审计的本地类比**，便于网关、回归仪表盘与论文附录机读 JSON 对齐。
- **与「只做库」的关系**：`run_pipeline_sync` 仍是稳定核心；HTTP 与 `full_pipeline` 作业是 **optional extra**（`pip install qchem-stack[api]`），避免把 Web 框架强加给嵌入用户。

---

## 2. 已定决策（摘要）

| 决策 | 内容 |
|------|------|
| 同步 POST 返回体 | `pipeline_result_for_job_store`，与异步 **DONE** 同形，保证 **JSON 可序列化** |
| 异步入队前校验 | 与同步共用 `ExperimentConfig`，避免垃圾任务占队列 |
| `traceparent` | `RunContext.from_headers` 优先解析，其次 `X-Trace-ID`，否则新 UUID |
| `GET …/repro` | 仅 `DONE`，否则 **409**，方便 Methods 流水线只拉 `repro` |
| `GET …/events` | **不**承诺完整事件流；仅 `created`/`updated` 合成两点 |
| `experiment_id` + workspace 过滤 | SQL `json_extract` + 老 SQLite **扫描回退**（有上限） |
| 竞品差距机读 | `GET /v1/meta/parity-gaps` 与 `inquanto_gap_categories()` 同内容源 |

---

## 3. 明确不做（避免范围漂移）

- **不做** Nexus/qnexus 真 SDK、真 HQC 货币、多租户项目隔离。
- **不做** 全量 `out` 落库（白名单在 `pipeline_runner.pipeline_result_for_job_store`）。
- **不做** Celery/Redis 默认实现（未来可抽象 `JobStore` Protocol 第二实现，不在此记忆包范围）。
- **不强依赖** OpenTelemetry SDK；字段名预留与云网关对齐即可。

---

## 4. 与其他文档的分工

| 文档 | 职责 |
|------|------|
| [ENGINEERING_ARCHITECTURE.md](/concept/engineering-architecture) | 英文化分层、稳定公共面、错误类型 |
| [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs) | 中文 **schema/端点/存储** 契约 |
| [launch_retrieve_nexus_analog.md](/concept/launch-retrieve-nexus-analog) | Nexus **语义**短表 |
| [inquanto_public_parity_matrix.md](/parity/public-matrix) | 公开能力矩阵 |
| [工程记忆_Quantinuum对标与数据流技术文档.md](/concept/engineering-memory-quantinuum) | 化学/Protocol/数据流总记忆 |

---

## 5. 变更时必须同步的清单（Checklist）

- [ ] 修改 `api/app.py`：同步 **技术文档 §5**、**ENGINEERING §9**、**README HTTP 段**；必要时 **launch 对照表**。
- [ ] 修改 `jobs/store.py` 行为：同步 **技术文档 §3**、**ENGINEERING §10**；单测 `test_job_store_list.py`、`test_api_runs.py`。
- [ ] 修改 `run_context` / `pipeline_profile`：同步 **技术文档 §2**、**ENGINEERING §8**、`test_observability_pipeline.py`。
- [ ] 修改 `pipeline_runner._RESULT_KEYS`：同步 **技术文档 §4 / §8**、README 若有「侧车」表述。
- [ ] 产品矩阵行级变更：更新 **inquanto_public_parity_matrix.md**；机读条更新 **inquanto_gap_categories()**。

---

## 6. 测试与 CI 记忆

- FastAPI 单测：`tests/test_api_runs.py`（`importorskip("fastapi")`）。
- 存储单测：`tests/test_job_store_list.py`、`tests/test_store_experiment_meta.py`。
- 全流程（PySCF）：`tests/test_pipeline_job_store.py`、`tests/test_observability_pipeline.py`。
- CI：`pip install -e ".[dev]"` 已含 `api`；另可单独 `pytest tests/test_api_runs.py`（见 `.github/workflows/ci.yml`）。

---

*最后更新：Computable 预览、queue-stats、repro-only 路由、`api_workspace_label`、列表双 meta 过滤、响应头 `X-Trace-ID`/`X-Request-ID`、ready 探针、list offset。*
