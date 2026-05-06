---
title: 通过 HTTP 异步提交一次运行
description: POST /v1/runs 入队后轮询 status / summary，直到 DONE 或失败
---

前提：已按 [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs) 安装可选 **`[api]`** 依赖并启动 worker；默认绑定本机。

## 1. 提交

对 `POST /v1/runs` 发送 JSON 体（至少包含管线所需的 `config_yaml` 或等价字段，与 API 契约一致）。若作业进入异步队列，响应为 **202** 且 body 为 `run_enqueue_response_v1`（含 `run_id` 等）；同步完成时则直接返回 `full_pipeline_job_result_v1`。

记录响应头 **`X-Trace-ID`**（及可选 `X-Request-ID`）便于与日志对齐。

## 2. 轮询

1. **`GET /v1/runs/{id}/status`** → `job_status_v1`，直到状态离开排队/运行或失败。  
2. 需要产品级摘要时：**`GET /v1/runs/{id}/summary`** → `run_product_summary_v1`（`DONE` 后为完整 slim 结果；排队中为 `partial`）。  
3. 需要阶段时间线：**`GET /v1/runs/{id}/events`** → `job_events_v1`。

## 3. 取 repro

仅在 **`DONE`** 后调用 **`GET /v1/runs/{id}/repro`**；否则 **409**。完整合并视图见 **`GET /v1/runs/{id}`**（契约见 Reference）。

## 4. 延伸阅读

- [命令行与脚本](/reference/cli-and-scripts) — 本地烟测与 worker 启动参数  
- [P4 作业与可复现](/guide/jobs-and-reproducibility/) — `repro` 键语义与落盘策略  

端点与 schema 名称以 [HTTP API 文档](/reference/http-api-sqlite-jobs) 为准。
