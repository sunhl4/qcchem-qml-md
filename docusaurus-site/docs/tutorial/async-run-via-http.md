# HTTP 异步运行教程

本教程演示如何通过 API 异步提交任务并轮询状态。

## 1. 启动服务

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 2. 提交任务

向 `POST /v1/runs` 发送 `experiment_yaml`，并设置异步模式。

## 3. 轮询状态

- `GET /v1/runs/{id}/status`：轻量状态
- `GET /v1/runs/{id}/summary`：产品摘要
- `GET /v1/runs/{id}/repro`：完成后获取完整 repro

## 4. 实践建议

- 在网关层统一传 `X-Trace-ID`
- 把 `job_id` 和业务单号做映射存档
