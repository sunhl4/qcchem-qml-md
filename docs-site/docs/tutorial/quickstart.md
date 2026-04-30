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

## 下一步

- [指南总览](/guide/) — 四柱索引  
- [公开 parity 矩阵](/parity/public-matrix) — 与 InQuanto 公开能力的对照  
- [工程架构](/concept/engineering-architecture) — 分层与稳定 JSON 导出  
