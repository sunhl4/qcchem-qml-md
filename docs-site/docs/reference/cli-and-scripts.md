---
title: 命令行与脚本
description: 安装后可用的控制台命令与仓库 scripts/ 常用入口
---

本文汇总**日常用法**里会碰到的命令；参数以仓库 `README.md` 与源码 `argparse` 为准。

## 安装（pip）

在仓库根 `qchem_qml_md/` 下：

```bash
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"`（PySCF、Qiskit、pytket 等）、`pip install -e ".[api]"`（FastAPI 服务）。

## 包入口（`pyproject.toml` · `[project.scripts]`）

安装后可在 PATH 中使用：

| 命令 | 作用 |
|------|------|
| `qchem-jobs-worker` | 轮询 SQLite 作业库，消费 `QUEUED` 作业（与 `qchem-pipeline-worker` 同一实现） |
| `qchem-pipeline-worker` | 同上 |

典型用法（数据库路径按你的部署修改）：

```bash
qchem-jobs-worker --db ./jobs.sqlite --sleep 0.5
```

支持参数：`--db`（必填）、`--sleep`（队列空时休眠秒数，默认 `0.5`）、`--max-retries`（默认 `2`）。实现见源码 `src/qchem_stack/jobs/worker.py`。

## 本地 HTTP 服务（uvicorn）

需 `[api]` extra：

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

路由与契约见 [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs)。

## 仓库 `scripts/`（在克隆目录内用 `python` 调用）

均在 `qchem_qml_md/` 根目录、已激活含 `qchem_stack` 的环境中执行。

| 脚本 | 说明 |
|------|------|
| `python scripts/smoke_pipeline.py` | CI/本地烟测：默认 `configs/example_h2.yaml`；可加 `--excited`、`--sampled`、`--qiskit-shots`、`--iqeb`、`--projection-trace` 等（见文件顶部 docstring） |
| `python scripts/export_parity_criteria_table.py <config.yaml>` | 导出 parity / Methods 用字段表；可选 `--results out.json` |
| `python scripts/check_parity_export_sample.py` | 校验导出样例（CI 相关） |
| `python scripts/run_qpe_track_demo.py` | QPE 演示轨（按需） |
| `python scripts/resource_estimation_demo.py` | 资源估计演示（按需） |

## Python 一行跑管线（非 CLI）

教程主路径见 [15 分钟上手](/tutorial/quickstart)：

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
```

## 另见

- [指南总览](/guide/) — 功能分柱说明  
- [HTTP API](/reference/http-api-sqlite-jobs) — REST 与作业状态  
