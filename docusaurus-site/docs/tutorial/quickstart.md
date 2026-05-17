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

本页聚焦**最小可运行路径**：你会完成一次从 YAML 到结果的端到端执行。

## 你将得到什么

- 一次可运行的最小任务（`example_h2.yaml`）
- 一个本地作业数据库（`jobs.sqlite`）
- 一份可继续分析的运行结果对象（`out`）

## 1. 安装

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"` 安装 PySCF、Qiskit、pytket 等扩展。

## 2. 跑最小端到端（YAML）

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
```

## 3. 快速验证输出

```python
print(out.get("status"))
print(out.get("run_summary", {}).keys())
pqi = out["pre_quantum_input"]
print(pqi["hamiltonian_fingerprint"], pqi.get("reference_energy_au"))
```

至少确认两点：

- 任务已结束（通常是 `DONE` 语义）
- `pre_quantum_input` 含 `hamiltonian_fingerprint` 与能量/活性空间摘要字段

库内单独构建哈密顿量请用 `qchem_stack.chem.pre_quantum_build.build_pre_quantum_input`（勿再依赖已弃用的 `molecular_hamiltonian_from_classical_reference`）。YAML 组合矩阵见仓库 `docs/pre_quantum_yaml_matrix.md`。

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

## 5. 常见问题

- **安装后找不到命令**：确认当前 shell 在正确 Python 虚拟环境中。
- **任务失败**：先跑 `python scripts/smoke_pipeline.py`，排除环境问题。
- **想切换后端**：先看 [切换后端对比](./switch-backend-compare)。

## 下一步

- [工作流与 YAML 概览](./workflow)
- [产品功能](../product/features)
- [指南总览](../guide/)
- [命令与脚本](../reference/cli-and-scripts)
