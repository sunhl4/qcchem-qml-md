---
title: 产品功能
description: qchem-stack 产品能力总览，覆盖三柱能力模型、接口面与推荐学习路径。
keywords:
  - quantum chemistry
  - workflows
  - YAML
  - 产品文档
---

# 产品功能

本站默认读者是使用者（研发、计算化学、平台集成）。建议按“先建立整体印象，再查接口与配置，最后深入实现细节”的顺序阅读。

## 三层阅读方式

| 层次 | 你关心什么 | 建议从哪里读 |
|------|------------|----------------|
| 1. 主要功能 | 软件解决什么问题、一条任务如何走完 | [15 分钟上手](../tutorial/quickstart) + [工作流与 YAML](../tutorial/workflow) |
| 2. 用法与接口 | 怎么配 YAML、怎么调 Python/HTTP/命令行 | [指南总览](../guide/overview) + [命令行与脚本](../reference/cli-http) |
| 3. 实现细节 | 字段契约、编译与采样路径、作业与复现语义 | [HTTP API](../reference/http-api-sqlite-jobs) + [云与作业](../cloud/overview) |

## 主要功能（用户视角）

- **Chemical Specification**：在 YAML 中定义分子、基组、活性空间和嵌入信息。
- **Program Construction**：将算法、协议与编排层拆分，形成可维护的数据流。
- **Execution and Analysis**：多后端执行、结果汇总、作业追踪与 repro 导出。

## 核心接口

| 接口 | 典型用途 |
|------|----------|
| YAML 配置 | 描述分子、算法、后端、缓解与作业行为 |
| Python API | 在脚本与 notebook 中同步执行管线 |
| HTTP API | 与外部调度器、服务网关集成 |
| CLI | 本地 worker、烟测脚本与运维操作 |

## 学习顺序建议

1. [快速上手](../tutorial/quickstart)
2. [工作流与 YAML](../tutorial/workflow)
3. [指南总览](../guide/overview)
4. [命令与 HTTP 接口](../reference/cli-http)
