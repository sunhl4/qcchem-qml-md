# 作业与日志

本页说明作业生命周期、可观测字段和日志治理建议。

## 作业生命周期

`QUEUED -> RUNNING -> DONE/FAILED`

建议对失败态记录：

- 错误类型
- 重试次数
- 最终失败原因

## 可观测字段

- `trace_id`
- `client_request_id`
- `pipeline_profile`
- `run_summary`

## 日志治理

- 约定日志保留周期与归档策略
- 生产环境默认脱敏请求体中的敏感字段
- 为队列异常增加告警（积压、超时、失败率）

## 相关

- [HTTP API 与作业契约](../reference/http-api-sqlite-jobs)
- [租户与配额](./tenant-and-quotas)
