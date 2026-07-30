---
title: api 与 sdk
description: SDK re-exports 与 FastAPI /v1/runs、/v1/meta 路由。
---

# api 与 sdk

对外集成优先走 `qchem_stack.sdk`；可选 HTTP 面在 `qchem_stack.api`。参考：[Python SDK](/reference/python-sdk) · [OpenAPI](/reference/openapi) · [HTTP+SQLite](/reference/http-api-sqlite-jobs)。

---

## 1. 文献与角色

| 包 | 作用 |
|----|------|
| `sdk` | 稳定 facade：配置加载、跑管线、parity / repro / 场景列表 |
| `api` | FastAPI：健康检查、meta 能力面、作业入队与查询 |
| 契约 | `api/contract.py` → `with_api_contract`；schema ids 见 [contracts](./contracts) |

SDK 降低对内部包路径的耦合；HTTP 把同一能力映射为 REST。

---

## 2. 理论

$$
\mathrm{SDK}: (\mathrm{YAML\ path}) \rightarrow \mathrm{out}
$$

$$
\mathrm{HTTP}: \mathrm{Request} \rightarrow \{\mathrm{sync\ out}\ |\ \mathrm{job\ id}\}
$$

Meta 面只做预览与能力枚举，不替代完整 `run_pipeline_*`。作业面与 [jobs](./jobs) store 共享状态机。

---

## 3. 实现

### SDK re-exports（`sdk/__init__.py`）

| 符号 | 用途 |
|------|------|
| `ExperimentConfig` | 配置类型 |
| `load_experiment_config` | 加载 YAML（`schema_version` `"2"`） |
| `run_pipeline_sync` | 进程内管线 |
| `run_pipeline_from_config` | **推荐入口**：路径 → `out` |
| `workflow_preview_payload` | 工作流预览 |
| `export_parity_table` | parity 表 |
| `repro_json_dumps` / `repro_dict_for_strict_json` | 严格 JSON |
| `SCENARIOS` / `list_scenarios_text` | 场景目录 |

App 工厂：`api/app.py` → `create_app()`。

### `/v1/runs`（`api/routers/runs.py`）

| 方法 | 路由 | 行为 |
|------|------|------|
| GET | `/v1/runs` | 列表（`JOB_LIST_V1`）；过滤 `status`、`job_kind`、`experiment_id` 等 |
| POST | `/v1/runs` | `sync=true` → 已弃用的内联 `run_pipeline_sync`；否则入队 `full_pipeline`（`202`，`RUN_ENQUEUE_RESPONSE_V1`） |
| GET | `/v1/runs/{job_id}` | 完整 `store.result` |
| GET | `/v1/runs/{job_id}/status` | `JOB_STATUS_V1` |
| GET | `/v1/runs/{job_id}/events` | 时间线 `JOB_EVENTS_V1` |
| GET | `/v1/runs/{job_id}/summary` | UX 精简摘要 |
| GET | `/v1/runs/{job_id}/repro` | `RUN_REPRO_ONLY_V1` — **仅 DONE** |

### `/v1/meta` 与健康

| 路由 | 说明 |
|------|------|
| GET `/v1/meta/product-surface` | `PRODUCT_SURFACE_V1` |
| GET `/v1/meta/capability-surface` | `CAPABILITY_SURFACE_V2` + ETag |
| GET `/v1/meta/parity-gaps` | `CAPABILITY_GAP_EXPORT_V1` |
| POST `/v1/meta/workflow-preview` | YAML → `workflow_preview_payload` |
| POST `/v1/meta/computables-preview` | `COMPUTABLES_PREVIEW_V1` |
| GET `/v1/meta/queue-stats` | `QUEUE_STATS_V1` |
| GET `/v1/meta/ml-md-bridge` | ML/MD 面 |
| POST `/v1/meta/qmef-validate` | `QMEF_VALIDATE_V1` |
| POST `/v1/meta/ml-md-trainer-stub-fit` | stub trainer |
| GET `/health`、`/health/ready` | 存活 + SQLite ping |

路由模块：`meta.py`、`ml_md.py`、`health.py`。

---

## 4. YAML / 启动

实验配置与 CLI 相同（`schema_version: "2"`）。HTTP 启动：

```bash
# 需 pip install "qchem-stack[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

异步作业还需 worker：

```bash
python3 -m qchem_stack.jobs.worker --db jobs.sqlite
```

---

## 5. Python

```python
from qchem_stack.sdk import (
    ExperimentConfig,
    load_experiment_config,
    run_pipeline_from_config,
    run_pipeline_sync,
    export_parity_table,
    workflow_preview_payload,
    repro_json_dumps,
    SCENARIOS,
    list_scenarios_text,
)

print(list_scenarios_text()[:200])
out = run_pipeline_from_config("configs/example_h2.yaml")
print("repro" in out)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config, load_experiment_config; c=load_experiment_config('configs/example_h2.yaml'); o=run_pipeline_from_config('configs/example_h2.yaml'); print(c.schema_version, 'repro' in o)"
```

期望：打印 `2 True`。

```bash
python3 -c "from qchem_stack.sdk import list_scenarios_text, export_parity_table; print(list_scenarios_text().splitlines()[0]); print(type(export_parity_table('configs/example_h2.yaml')).__name__)"
```

期望：场景首行 + 导出类型名。

（可选，需 api extras）`curl -s http://127.0.0.1:8000/health`。

---

## 7. 调优建议

- 新集成**只**依赖 `sdk` 与文档稳定路径。  
- 生产用异步 `/v1/runs` + worker，避免 `sync=true`。  
- Meta 预览用于 CI 门闩；完整能量仍跑管线。  
- OpenAPI 与 schema id 变更走 [contracts](./contracts) 版本策略。

---

## 8. 相关

- [jobs](./jobs) · [orchestration](./orchestration) · [repro](./repro) · [contracts](./contracts)  
- [异步教程](/tutorial/async-run-via-http) · [ops-light](./ops-light)
