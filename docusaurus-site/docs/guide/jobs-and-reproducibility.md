# P4 作业与可复现（Jobs and reproducibility）

P4 是工程落地层：让实验从“本地能跑”变成“团队可追踪、可回放、可审计”。

## 你在 P4 主要做什么

- SQLite 作业队列与 worker 执行边界
- 同步/异步运行模式切换
- repro、run_context、pipeline_profile 等结构化产物

## 为什么单独设 P4

前三柱聚焦计算语义，P4 聚焦运行治理：接口契约、状态机、观测字段和失败恢复。

## 典型接入流程

1. API 提交任务（同步或异步）
2. worker 消费队列并执行
3. 通过状态接口轮询
4. 任务完成后读取 `summary`/`repro`

## 运维建议

- 把 `FAILED` 的分类和重试策略文档化
- 为积压、超时、失败率设置告警阈值
- 定期回归关键配置，防止“能跑但不可复现”

## 相关文档

- [命令与接口参考](../reference/cli-and-scripts)
- [HTTP API 与作业契约](../reference/http-api-sqlite-jobs)
- [云与作业概览](../cloud/overview)
