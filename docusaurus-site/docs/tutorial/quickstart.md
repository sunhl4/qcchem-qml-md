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

本页聚焦**最小可运行路径**：你会完成一次从 scenario 到结果的端到端执行。

## 你将得到什么

- 一次可运行的最小任务（`configs/scenarios/minimal_vqe.yaml`）
- 一个本地作业数据库（`jobs.sqlite`）
- 一份可继续分析的运行结果对象（`out`）

## 1. 安装

安装配置见仓库 [README — Install profiles](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/install_profiles.md)（`core` / `chemistry` / `qiskit-sim` / `uqc-cloud` / `maintainer`）。

```bash
cd qcchem-qml-md
./scripts/bootstrap_dev.sh
export QCHEM_STACK_PYTHON="$(pwd)/.venv/bin/python"
```

或手动：`pip install -e ".[dev,chem]"`。无 PySCF 烟测：`python scripts/smoke_pipeline.py --precomputed-only`。

## 2. 跑最小端到端（推荐：scenario）

```bash
qchem-run --scenario minimal_vqe
```

或 Python API（薄 v3 stub 经迁移加载）：

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config(
    "configs/scenarios/minimal_vqe.yaml",
    job_db=Path("jobs.sqlite"),
)
```

全量 v2 参考 YAML：`configs/example_h2.yaml`。

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

## 4. 可选 HTTP API

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 5. 常用命令

| 场景 | 命令 |
|------|------|
| CLI 跑默认 H₂ | `qchem-run --scenario minimal_vqe` |
| 列出场景 | `qchem-run --list-scenarios` |
| 覆盖参数 | `qchem-run --scenario minimal_vqe --set quantum.vqe.max_iter=50` |
| 消费作业队列 | `qchem-jobs-worker --db ./jobs.sqlite` |
| 启动 API | `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000` |
| 本地烟测 | `python scripts/smoke_pipeline.py` |

## 验证命令

```bash
python scripts/smoke_pipeline.py
```

## 期望输出

- 进程退出码 `0`
- 结果含 `pre_quantum_input.hamiltonian_fingerprint`
- `qchem-run --scenario minimal_vqe` 可替代烟测

## 6. 常见问题

- **安装后找不到命令**：确认当前 shell 在正确 Python 虚拟环境中。
- **任务失败**：先跑 `python scripts/smoke_pipeline.py`，排除环境问题。
- **想切换后端**：先看 [切换后端对比](./switch-backend-compare)。

## 下一步

- [English onboarding (by role)](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/ONBOARDING_BY_ROLE_en.md)
- [工作流与 YAML 概览](./workflow)
- [产品功能](../product/features)
- [指南总览](../guide/)
- [命令与脚本](../reference/cli-and-scripts)
