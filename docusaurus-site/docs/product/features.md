---
title: 产品功能
description: qchem-stack 能做什么：能力地图、接口面、适用场景与边界。
keywords:
  - quantum chemistry
  - workflows
  - YAML
  - 产品文档
---

# 产品功能

面向量子化学研发、平台集成与项目维护三类读者：先看能力，再选入口。

编排层为 **Production / Stable**；局部能力诚实标注见 [能力 SLA](./capability-sla)。

## 怎么读

| 目标 | 入口 |
|------|------|
| 跑通一条管线 | [15 分钟上手](../tutorial/quickstart) |
| 改配置、切后端、接 API | [选型手册](../guide/) · [CLI](../reference/cli-and-scripts) |
| 作业、可观测与验收 | [HTTP API](../reference/http-api-sqlite-jobs) · [云与作业](../cloud/overview) |

## 能力地图

- **P1 化学与嵌入**：分子、基组、活性空间与经典输入。
- **P2 算法与协议**：变分算法、算符池、Pauli 协议与激发态。
- **P3 执行与分析**：多后端、采样、缓解与结果摘要。
- **P4 作业与可复现**：作业状态、HTTP 提交与 `repro` 导出。

## 接口面

| 接口 | 用途 | 典型用户 |
|------|------|----------|
| YAML | 描述化学问题、算法与后端 | 算法研发 |
| Python SDK | 脚本与 notebook 内跑管线 | 研发、分析 |
| HTTP API | 异步作业对接 | 平台工程 |
| CLI / scripts | 烟测、导出与运维 | 维护者 |

## 典型路径

1. **研究**：改 `configs/*.yaml` → 跑管线 → 读 `run_summary` / `repro`
2. **集成**：`POST /v1/runs` → worker → `GET /summary` / `GET /repro`
3. **维护**：`smoke_pipeline` + parity 检查 → 更新契约文档

## 边界

- 开放工程路径；不宣称与闭源产品逐行等价
- 支持本地 / 私有部署；不默认提供商业云 IAM、计费或硬件 SLA
- 路线图面向研发验收，不是入门必读
- 可用性标签见 [能力 SLA](./capability-sla)

## 建议顺序

1. [15 分钟上手](../tutorial/quickstart)
2. [选型手册](../guide/)
3. [Python SDK](../reference/python-sdk)
4. [能力 SLA](./capability-sla)
