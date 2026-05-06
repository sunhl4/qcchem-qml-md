# 命令行与脚本

本文汇总日常高频命令，详细契约可结合 [HTTP API 与作业队列](./http-api-sqlite-jobs) 阅读。

## 安装

```bash
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"`、`pip install -e ".[api]"`。

## 包入口命令

| 命令 | 作用 |
|------|------|
| `qchem-jobs-worker` | 轮询 SQLite 队列，消费 `QUEUED` 作业 |
| `qchem-pipeline-worker` | 与 `qchem-jobs-worker` 等价入口 |

典型用法：

```bash
qchem-jobs-worker --db ./jobs.sqlite --sleep 0.5
```

## 本地 HTTP 服务

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 仓库脚本（scripts）

| 脚本 | 说明 |
|------|------|
| `python scripts/smoke_pipeline.py` | 本地/CI 烟测 |
| `python scripts/export_parity_criteria_table.py <config.yaml>` | 导出对标判据表 |
| `python scripts/check_parity_export_sample.py` | 校验导出样例 |

## 另见

- [快速上手](../tutorial/quickstart)
- [P4 作业与可复现](../guide/jobs-and-reproducibility)
