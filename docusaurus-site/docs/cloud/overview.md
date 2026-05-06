---
title: 模拟器云（契约骨架）
description: qchem-stack 云端作业能力概览，聚焦多租户模拟器、作业契约与可观测治理。
keywords:
  - cloud
  - jobs
  - tenant
  - backend registry
---

# 模拟器云（契约骨架）

自建多租户模拟器云的契约叙事：租户、后端注册、作业与日志。重点是开放可验证的工程路径，而不是复制商业云能力。

## 当前覆盖范围

- SQLite 队列 + worker 作业消费
- FastAPI 提交、查询、追踪接口
- run_context/repro/pipeline_profile 观测与审计字段

## 非目标

- 厂商 OAuth/IAM 体系
- 商业真机配额与计费系统
- 闭源控制台行为复刻

## 推荐建设顺序

1. 稳定作业状态机与错误语义
2. 增强队列可观测与告警
3. 演进多租户、配额与治理能力

## 相关文档

- [HTTP API 与作业队列](../reference/http-api-sqlite-jobs)
- [P4 作业与可复现](../guide/jobs-and-reproducibility)
