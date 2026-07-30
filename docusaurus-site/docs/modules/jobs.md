---
title: jobs 模块
description: SqliteJobStore、worker、full_pipeline 与 Pauli pickle、drain_one_queued。
---

# jobs 模块

`qchem_stack.jobs` 提供异步作业边界：SQLite / 内存 / Postgres store 与 worker 调度。选型：[P4 作业](/guide/jobs-and-reproducibility) · [HTTP 契约](/reference/http-api-sqlite-jobs)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| Store | 持久化队列、状态机、时间线事件 |
| Worker | 认领 `QUEUED`、重试、派发到管线或 Pauli 协议 |
| HTTP | `POST /v1/runs` 入队 `full_pipeline`（见 [api-sdk](./api-sdk)） |
| 云面 | [作业与日志](/cloud/jobs-and-logs) |

作业把长跑与 HTTP 请求解耦，避免同步超时。

---

## 2. 理论

生命周期：

$$
\mathrm{queued} \rightarrow \mathrm{running} \rightarrow \{\mathrm{succeeded},\mathrm{failed}\}
$$

重试退避（`store_retry.exponential_backoff_delay`）：

$$
\Delta t = t_0\, r^{k},\quad k=0,1,\ldots
$$

两种载荷语义：**整管线 YAML** vs **已物化的 Pauli 协议 blob**。

---

## 3. 实现

### SqliteJobStore

| 项 | 路径 |
|----|------|
| 实现 | `jobs/store_service.py` → `SqliteJobStore` |
| 导出 | `jobs/store.py` |
| 其他 | `InMemoryJobStore`、`store_postgres` |

关键方法：`enqueue`、`claim_next_queued`、`complete`、`result`、`list_jobs`、`get_job_public_summary`、`get_job_timeline_events`、`count_by_status`。

### Job kinds（`jobs/kinds.py`）

| 常量 | 值 | 载荷 |
|------|-----|------|
| `JOB_KIND_PAULI_PROTOCOL` | `pauli_protocol` | 签名/pickle 的 `PauliAveragingProtocol`（默认） |
| `JOB_KIND_FULL_PIPELINE` | `full_pipeline` | JSON：`config_yaml`、`config_base_dir?`、`run_context?` |

### Worker

- 模块：`jobs/worker.py` → `main()`  
- CLI：`python3 -m qchem_stack.jobs.worker --db jobs.sqlite`  
- 参数：`--db`、`--db-url`、`--sleep`、`--max-retries`、`--workers`  
- 环境：`QCHEM_PROTOCOL_BLOB_V2`（默认开；`0` → legacy pickle v1 警告）  
- 循环：`worker_loop` → 反复 `drain_one_queued`

### `drain_one_queued`

```text
drain_one_queued(store, runner=None, *, max_retries=2, timeout_seconds=None) -> bool
```

认领一个 `QUEUED`，经 `process_job_with_retry` + `dispatch_job`（或自定义 `runner`）执行；有任务返回 `True`。

### `dispatch_job`（`worker_dispatch.py`）

| `job_kind` | 处理 |
|------------|------|
| `full_pipeline` | `run_full_pipeline_job` → `run_pipeline_sync`，结果 schema `FULL_PIPELINE_JOB_RESULT_V1` |
| 其他（Pauli） | `PauliAveragingProtocol.process_job`（反序列化后 build/compile/run/evaluate） |

入队：`enqueue_full_pipeline_run`（`pipeline_jobs.py`）；Pauli：`protocol.launch(store)` 或 `run_pipeline_from_config(..., job_db=...)`。

---

## 4. YAML / 运行时

Jobs 无独立实验 YAML 块。典型运行时：

| 项 | 说明 |
|----|------|
| `--db jobs.sqlite` | 本地 SQLite 路径 |
| `--db-url` | Postgres |
| API 异步 | `POST /v1/runs` 且 `sync` 非 true → 入队 `full_pipeline` |

实验仍用 `schema_version: "2"` 的标准配置。

---

## 5. Python

```python
from qchem_stack.jobs.store_factory import in_memory_job_store, job_store_from_cli
from qchem_stack.jobs.store_schema import JobStatus
from qchem_stack.jobs.worker import drain_one_queued
from qchem_stack.jobs.kinds import JOB_KIND_FULL_PIPELINE, JOB_KIND_PAULI_PROTOCOL

store = in_memory_job_store()
print(JobStatus, JOB_KIND_FULL_PIPELINE, JOB_KIND_PAULI_PROTOCOL)
# 生产：SqliteJobStore via --db
# while drain_one_queued(store):
#     pass
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.jobs.store_factory import in_memory_job_store; s=in_memory_job_store(); print(type(s).__name__)"
```

期望：打印 store 类名（如含 `JobStore` / `InMemory`）。

```bash
python3 -m qchem_stack.jobs.worker --help
```

期望：退出码 `0`；帮助含 `--db`。

```bash
python3 -c "from qchem_stack.jobs.worker import drain_one_queued; from qchem_stack.jobs.store_factory import in_memory_job_store; print(drain_one_queued(in_memory_job_store()))"
```

期望：空队列打印 `False`。

---

## 7. 调优建议

- 本地：一库一 worker（`--db jobs.sqlite`）；多 worker 注意 SQLite 锁。  
- 生产优先 Postgres（`--db-url`）或云作业面。  
- `full_pipeline` 适合 HTTP 异步；已物化测量用 Pauli pickle 避免重复 SCF。  
- 保持 `QCHEM_PROTOCOL_BLOB_V2` 默认；导出 `repro` 走严格 JSON（[repro](./repro)）。

---

## 8. 相关

- [api-sdk](./api-sdk) · [orchestration](./orchestration) · [protocols](./protocols)  
- [异步 HTTP 教程](/tutorial/async-run-via-http) · [ops-light](./ops-light)
