# 15 分钟上手

本页提炼自仓库根 `README.md` 编排段落；**权威安装与参数仍以 README 为准**（开发过程中请对照源码）。

## 1. 安装

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"` 拉齐 PySCF、Qiskit、pytket 等 extras。

## 2. 最小端到端（YAML）

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
# out：scf_energy、variational 能量、Pauli 协议、resource_summary、repro、job_result 等
```

## 3. 可选 HTTP API

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

契约与端点表见 [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs)。

## 4. 常用命令（摘要）

| 场景 | 命令 |
|------|------|
| 消费 SQLite 队列里的作业 | `qchem-jobs-worker --db ./jobs.sqlite`（或 `qchem-pipeline-worker`，等价） |
| 起本地 API | `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000` |
| 仓库内烟测 | `python scripts/smoke_pipeline.py`（可加 `--sampled`、`--qiskit-shots` 等） |

完整说明与更多脚本见 **[命令行与脚本](/reference/cli-and-scripts)**。

## 下一步

- [产品功能](/product/features) — 能力分层与用户接口一览  
- [工作流与 YAML 概览](/tutorial/workflow-overview) — 配置与四柱对应  
- [指南总览](/guide/) — 按柱阅读功能与用法  
- [命令行与脚本](/reference/cli-and-scripts) · [HTTP API](/reference/http-api-sqlite-jobs)  
- 深入：[原理与阅读建议](/guide/principles-and-reading)；内部对标见 [定位与路线](/product/)  
