---
title: 命令行与脚本
description: 安装后可用的控制台命令与仓库 scripts/ 常用入口。
---

# 命令行与脚本

本文聚焦日常高频命令。参数细节以仓库 `README.md`、`pyproject.toml` 与脚本 docstring 为准。

## 安装

在仓库根目录执行：

```bash
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"`、`pip install -e ".[api]"`。

## 包入口命令

| 命令 | 作用 |
|------|------|
| `qchem-jobs-worker` | 轮询 SQLite 作业库，消费 `QUEUED` 作业 |
| `qchem-pipeline-worker` | 与 `qchem-jobs-worker` 等价入口 |

典型用法：

```bash
qchem-jobs-worker --db ./jobs.sqlite --sleep 0.5
```

## 本地 HTTP 服务

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

契约说明见 [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)。

## 仓库脚本（`scripts/`）

| 脚本 | 说明 |
|------|------|
| `python scripts/smoke_pipeline.py` | 本地/CI 烟测入口 |
| `python scripts/export_parity_criteria_table.py <config.yaml>` | 导出 parity 判据表 |
| `python scripts/check_parity_export_sample.py` | 校验导出样例 |
| `python scripts/check_solver_adapter_contract.py [config.yaml]` | 检查 solver 适配合同 |
| `python scripts/create_solver_adapter_scaffold.py <backend_id>` | 生成新后端适配骨架 |
| `python scripts/demo_mock_external_backend.py` | 运行 mock 外部后端演示 |
| `python scripts/run_qpe_track_demo.py` | QPE 演示轨 |
| `python scripts/resource_estimation_demo.py` | 资源估计演示 |

## 另见

- [快速上手](/tutorial/quickstart)
- [P4 作业与可复现](/guide/jobs-and-reproducibility)
- [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)
