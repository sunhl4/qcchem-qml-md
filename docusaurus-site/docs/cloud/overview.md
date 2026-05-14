---
title: 云与运维概览
description: 面向本地/私有部署的作业云化实践，聚焦后端治理、作业状态和可观测能力。
keywords:
  - cloud
  - jobs
  - tenant
  - backend registry
---

# 云与运维概览

本区不是“商业云说明书”，而是 `qchem-stack` 在本地/私有部署场景下的云化运维手册。

## 目标场景

- 内部研发团队共享同一套执行入口
- 需要异步作业和状态查询
- 需要最小可行的多租户隔离与配额控制
- 需要运行证据（日志、摘要、复现字段）

## 当前覆盖范围

- SQLite 队列 + worker 作业消费
- FastAPI 提交、查询、追踪接口
- run_context/repro/pipeline_profile 观测与审计字段

## 非目标

- 厂商 OAuth/IAM 体系
- 商业真机配额与计费系统
- 闭源控制台行为复刻

## 运维三件套

1. [后端注册表](./backend-registry)：定义可用执行面与能力标签  
2. [作业与日志](./jobs-and-logs)：定义状态机、失败语义与告警口径  
3. [租户与配额](./tenant-and-quotas)：定义公平性和资源上限策略

## 推荐建设顺序（渐进式）

1. 稳定作业状态机与错误语义
2. 增强队列可观测与告警
3. 演进多租户、配额与治理能力

## 相关文档

- [HTTP API 与作业队列](../reference/http-api-sqlite-jobs)
- [P4 作业与可复现](../guide/jobs-and-reproducibility)
