# 作业与日志

:::warning 建议模式
本文描述推荐运维模式；当前开源实现以本地 FastAPI + SQLite worker 为主，租户配额/商业 IAM 未内置强制执行。
:::

本页定义运维最关键的三件事：状态机、失败语义、告警口径。

## 作业生命周期

`QUEUED -> RUNNING -> DONE/FAILED`

建议对 `FAILED` 固定记录：

- 错误类型
- 重试次数
- 最终失败原因

## 关键可观测字段

- `trace_id`
- `client_request_id`
- `pipeline_profile`
- `run_summary`

## 建议告警项

- 队列积压长度持续增长
- RUNNING 超时占比过高
- FAILED 比例超过阈值
- 某类错误短时间内集中爆发

## 日志治理

- 约定日志保留周期与归档策略
- 生产环境默认脱敏请求体中的敏感字段
- 为队列异常增加告警（积压、超时、失败率）

## 相关

- [HTTP API 与作业契约](../reference/http-api-sqlite-jobs)
- [租户与配额](./tenant-and-quotas)
