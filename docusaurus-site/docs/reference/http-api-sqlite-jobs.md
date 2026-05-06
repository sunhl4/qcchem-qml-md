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

本文是 `qchem_stack.api` 与 `qchem_stack.jobs` 的工程契约摘要，用于服务化集成与运维对接。

## 边界

- 当前是本地/私有部署友好的 FastAPI + SQLite 路径
- 不等价于商业云平台 IAM、OAuth、配额与计费体系
- 强调可复现与可审计，而非闭源产品功能复刻

## 可观测字段

| 字段 | 说明 |
|------|------|
| `trace_id` | 贯穿请求与执行链路的追踪 ID |
| `client_request_id` | 网关透传的请求标识 |
| `pipeline_profile` | 分阶段耗时与总耗时 |
| `run_summary` | 结果摘要与关键指标 |

## 常用接口

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/health` | 存活检查 |
| GET | `/health/ready` | 就绪检查（含存储可用性） |
| GET | `/v1/runs` | 作业列表与分页 |
| POST | `/v1/runs` | 提交同步或异步运行 |
| GET | `/v1/runs/{id}/status` | 轻量状态查询 |
| GET | `/v1/runs/{id}/summary` | 产品侧摘要视图 |
| GET | `/v1/runs/{id}/repro` | DONE 后拉取 repro |

## 状态码建议

- `400`：YAML 解析错误或请求体不合法
- `404`：作业不存在
- `409`：作业未完成但请求了仅完成态可读的数据
- `422`：配置校验失败或管线业务错误

## 运行

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```
