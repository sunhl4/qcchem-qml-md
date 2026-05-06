# P4 作业与可复现（Jobs and reproducibility）

P4 是面向工程化落地新增的一柱：让实验可以异步运行、追踪、回放与审计。

## 核心内容

- SQLite 作业队列与 worker 执行边界
- 同步/异步运行模式切换
- repro、run_context、pipeline_profile 等结构化产物

## 为什么单独设 P4

前三柱聚焦算法与计算语义，P4 解决“如何稳定跑在团队环境中”的问题，包括接口契约、观测字段和失败恢复策略。

## 相关文档

- [命令与接口参考](../reference/cli-http)
- [HTTP API 与作业契约](../reference/http-api-sqlite-jobs)
- [云与作业概览](../cloud/overview)
