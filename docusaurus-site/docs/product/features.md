---
title: 产品功能
description: 面向用户和维护者的产品功能说明，包含能力地图、接口面、适用场景与边界。
keywords:
  - quantum chemistry
  - workflows
  - YAML
  - 产品文档
---

# 产品功能

本站默认读者是三类人：量子化学研发、平台集成工程师、项目维护者。  
这页先回答“能做什么”，再告诉你“应该从哪里做”。

## 三层阅读方式

| 层次 | 你关心什么 | 建议从哪里读 |
|------|------------|----------------|
| 1. 跑起来 | 一条任务如何从配置到结果 | [15 分钟上手](../tutorial/quickstart) + [工作流与 YAML](../tutorial/workflow) |
| 2. 用起来 | 怎么改配置、切后端、接 API | [指南总览](../guide/) + [命令行与脚本](../reference/cli-and-scripts) |
| 3. 管起来 | 怎么稳定运行、可观测、可验收 | [HTTP API](../reference/http-api-sqlite-jobs) + [云与作业](../cloud/overview) |

## 主要功能（用户视角）

- **P1 化学与嵌入**：定义分子、基组、活性空间，组织经典问题输入。
- **P2 程序构建**：按算法/协议/编排分层，形成稳定可演进的执行计划。
- **P3 执行与分析**：多后端执行、采样路径、缓解与结果摘要。
- **P4 作业与可复现**：作业状态机、HTTP 提交与追踪、`repro` 导出。

## 产品接口面

| 接口面 | 你在这里做什么 | 常见使用者 |
|---|---|---|
| YAML 配置 | 描述化学问题、算法和后端 | 算法研发、实验工程 |
| Python API | 在脚本与 notebook 内运行管线 | 研发、分析 |
| HTTP API | 与外部服务对接异步作业 | 平台/后端工程 |
| CLI + scripts | worker、烟测、导出与维护脚本 | 平台运维、维护者 |

## 典型场景

1. **研究者路径**：改 `configs/*.yaml` -> 跑 pipeline -> 看 `run_summary`
2. **集成路径**：`POST /v1/runs` -> worker 消费 -> `GET /summary` / `GET /repro`
3. **维护路径**：跑 `scripts/smoke_pipeline.py` + parity/export 检查 -> 更新文档契约

## 边界（必须明确）

- 聚焦开放工程路径，不宣称闭源产品逐行等价
- 支持本地/私有部署，不默认承诺商业云 IAM、计费、硬件 SLA
- 对标页用于研发验收和计划管理，不是终端用户入门必读

## 建议学习顺序

1. [15 分钟上手](../tutorial/quickstart)
2. [工作流与 YAML](../tutorial/workflow)
3. [指南总览](../guide/)
4. [命令行与脚本](../reference/cli-and-scripts)
5. [HTTP API](../reference/http-api-sqlite-jobs)