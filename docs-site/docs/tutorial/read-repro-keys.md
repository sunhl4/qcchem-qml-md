---
title: repro 里值得先看的 10 个键
description: 从导出 JSON 快速定位 schema、追踪与管线阶段，不替代 Reference
---

`out["repro"]`（及 HTTP **`GET …/repro`**）是**可机读**的可复现摘要。下面 10 类键帮助你**先建立地图**再下钻 Reference 与源码（具体键名以当前 schema 为准）。

| # | 关注点 | 典型键 / 块 |
|---|--------|-------------|
| 1 | 大块 schema | 顶层或子块中的 `schema` 字符串（如 `run_context_v1`） |
| 2 | 追踪 | `run_context` 内的 `trace_id`、`client_request_id` |
| 3 | 阶段耗时 | `pipeline_profile`：`stages`、`total_wall_ms` |
| 4 | 实验标识 | `experiment_id`、`random_seed`、`schema_version`（若出现在 repro 镜像中） |
| 5 | 后端与采样 | 与 `backend`、`shots` 相关的摘要字段（见 run_summary 镜像） |
| 6 | 缓解 / 编译摘要 | 与 `mitigation`、`compiler` 相关的白名单子集 |
| 7 | 嵌入模式 | `embedding.mode` 一类摘要（若本次运行涉及） |
| 8 | Parity / 对表 | `parity_export_schema_version`、`inquanto_gap_categories` 等（若导出） |
| 9 | 协议与哈希 | `protocol_hash`、Pauli 作业类元数据（异步路径） |
| 10 | 错误与重试 | 失败分支下的 `error` / `retry` 相关短字段（若有） |

**严格 JSON**：对外系统写入前使用 `repro_json_dumps`（见 [HTTP API](/reference/http-api-sqlite-jobs) 与工程架构文档）。

深入字段表：[HTTP API · repro / run_context](/reference/http-api-sqlite-jobs) · [DMET · parity_snapshot](/reference/dmet-parity-snapshot)。
