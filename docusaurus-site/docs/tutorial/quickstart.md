---
title: 15 分钟上手
description: 在 15 分钟内完成 qchem-stack 最小端到端流程，包含安装、配置与 API 启动。
keywords:
  - 教程
  - quickstart
  - qchem-stack
  - pipeline
---

# 15 分钟上手

本页聚焦最小可运行路径，帮助你快速验证 `qchem_qml_md` 的端到端流程。

## 1. 安装

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"` 安装 PySCF、Qiskit、pytket 等扩展。

## 2. 最小端到端（YAML）

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
```

## 3. 可选 HTTP API

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 4. 常用命令

| 场景 | 命令 |
|------|------|
| 消费作业队列 | `qchem-jobs-worker --db ./jobs.sqlite` |
| 启动 API | `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000` |
| 本地烟测 | `python scripts/smoke_pipeline.py` |

## 下一步

- [工作流与 YAML 概览](./workflow)
- [产品功能](../product/features)
- [指南总览](../guide/overview)
- [命令与脚本](../reference/cli-http)
