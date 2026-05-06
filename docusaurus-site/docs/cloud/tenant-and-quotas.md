# 租户与配额

该页描述平台化场景下的租户隔离与资源治理约束。

## 推荐契约字段

| 字段 | 含义 |
|------|------|
| `workspace_label` | 逻辑租户标识 |
| `project_slug` | 项目标识 |
| `max_concurrency` | 并发上限 |
| `max_wall_time` | 单任务最长运行时间 |

## 调度建议

- 默认 FIFO，可增加小任务穿插策略
- 对超时/重试任务设置独立队列策略
- 暴露等待时间分位数用于公平性评估

## 相关

- [作业与日志](./jobs-and-logs)
- [HTTP API 与作业契约](../reference/http-api-sqlite-jobs)
