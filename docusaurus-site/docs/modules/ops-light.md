---
title: Day-2 运维（轻量）
description: 冒烟、jobs worker、health、repro 导出——日常运维清单。
---

# Day-2 运维（轻量）

面向「已经跑通一次 H₂」之后的日常检查：冒烟、作业 worker、HTTP 健康、repro 导出。算法深读请回 [reading-paths](./reading-paths) · [算法索引](./quantum/algorithms/)。

---

## 1. 文献与角色

| 主题 | 去哪读 |
|------|--------|
| MD/ML / QMEF | [md-bridge](./md-bridge) · [选型](/guide/md-ml-active-learning) |
| HTTP 作业 | [jobs](./jobs) · [api-sdk](./api-sdk) · [云作业](/cloud/jobs-and-logs) |
| 可复现 | [repro](./repro) · [parity 契约](/guide/parity-repro-contract) |
| 资源估计 | [资源估计选型](/guide/resource-estimation-methods) |

本页是**操作清单**，不是算法手册。

---

## 2. 理论：健康闭环

$$
\mathrm{smoke} \rightarrow \mathrm{enqueue} \rightarrow \mathrm{worker} \rightarrow \mathrm{repro\ export}
$$

任一步失败都应有：非零退出码、或 job `failed`、或 `ReproExportError`——禁止静默 `default=str`。

---

## 3. 实现：四件套

| 步骤 | 机制 |
|------|------|
| Smoke | `run_pipeline_from_config` 或 `qchem-run --scenario` |
| Worker | `python3 -m qchem_stack.jobs.worker --db jobs.sqlite` |
| Health | `GET /health`、`/health/ready`（api extras） |
| Repro | `repro_json_dumps(out["repro"])` 或 `GET /v1/runs/{id}/repro`（DONE） |

Store：`SqliteJobStore`；入队：`POST /v1/runs` → `full_pipeline`。详见 [jobs](./jobs)。

---

## 4. YAML / 运行时

冒烟用最小配置（`schema_version: "2"`）：

```yaml
# configs/profiles/minimal_h2.yaml 或 example_h2.yaml
schema_version: "2"
```

Worker / API 环境变量示例：

| 项 | 说明 |
|----|------|
| `--db jobs.sqlite` | 本地队列 |
| `QCHEM_PROTOCOL_BLOB_V2` | 默认开；勿随意关 |
| uvicorn host/port | 如 `127.0.0.1:8000` |

---

## 5. Python

```python
from qchem_stack.sdk import (
    run_pipeline_from_config,
    load_experiment_config,
    repro_json_dumps,
)

cfg = load_experiment_config("configs/example_h2.yaml")
assert cfg.schema_version == "2"
out = run_pipeline_from_config("configs/example_h2.yaml")
payload = repro_json_dumps(out["repro"])
print(len(payload))
```

---

## 6. 验证（运维冒烟）

**A. 同步管线**

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps; o=run_pipeline_from_config('configs/example_h2.yaml'); s=repro_json_dumps(o['repro']); print('smoke_ok', len(s))"
```

期望：`smoke_ok` + 正整数。

**B. Worker CLI**

```bash
python3 -m qchem_stack.jobs.worker --help
```

期望：帮助含 `--db`。后台消费：

```bash
python3 -m qchem_stack.jobs.worker --db jobs.sqlite
```

**C. Health（需 api extras + 已启动 uvicorn）**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health
```

期望：`200`。

**D. 空队列 drain**

```bash
python3 -c "from qchem_stack.jobs.worker import drain_one_queued; from qchem_stack.jobs.store_factory import in_memory_job_store; print(drain_one_queued(in_memory_job_store()))"
```

期望：`False`。

---

## 7. 调优建议

- CI：只跑 A（同步 smoke）+ contracts/schema 断言；worker 用独立 job。  
- 一机一 SQLite；多进程改 Postgres。  
- 导出失败先查 NaN/非 JSON 类型，再查磁盘。  
- Meta 面（`/v1/meta/*`）可做部署后 readiness 扩展，但不替代完整 smoke。

---

## 8. 相关

- [jobs](./jobs) · [api-sdk](./api-sdk) · [repro](./repro) · [orchestration](./orchestration)  
- [异步教程](/tutorial/async-run-via-http) · [reading-paths](./reading-paths) · [模块总览](./)
