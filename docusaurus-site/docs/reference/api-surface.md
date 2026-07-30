---
title: API surface（集成面）
description: qchem_stack.sdk 与关键入口的实用签名参考；非 Sphinx autodoc。
keywords:
  - sdk
  - API
  - run_pipeline_sync
  - BackendSpec
---

# API surface（集成面）

本文是**实用集成面**参考，不是完整 Sphinx autodoc。稳定入口优先 `qchem_stack.sdk`；完整 API 文档可能后续补充。

策略见仓库 [api_stability_policy.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/api_stability_policy.md)。薄 facade 摘要：[Python SDK](/reference/python-sdk) · **[SDK API（生成）](/reference/api-generated)** · [api 与 sdk](/modules/api-sdk)。

---

## 1. `qchem_stack.sdk` 公共导出

```python
from qchem_stack.sdk import (
    ExperimentConfig,
    SCENARIOS,
    export_parity_table,
    list_scenarios_text,
    load_experiment_config,
    repro_dict_for_strict_json,
    repro_json_dumps,
    run_pipeline_from_config,
    run_pipeline_sync,
    workflow_preview_payload,
)
```

| 符号 | 签名（概要） | 用途 |
|------|----------------|------|
| `ExperimentConfig` | Pydantic 模型 | 类型化实验配置（`schema_version` `"2"`） |
| `load_experiment_config` | `(path: str \| Path, *, strict_top_level_keys: bool = False) → ExperimentConfig` | 加载并校验 YAML |
| `run_pipeline_sync` | `(cfg: ExperimentConfig, *, cfg_path=None, ...) → PipelineResultV1` | 进程内跑完整管线 |
| `run_pipeline_from_config` | `(cfg_path: str \| Path, *, job_db=None, enqueue_only=False, ...) → PipelineResultV1` | **推荐**：路径 → `out`（含 `repro`） |
| `workflow_preview_payload` | `(cfg: ExperimentConfig, ...) → dict` | 工作流预览（不跑重计算） |
| `export_parity_table` | `(config_path, *, results_path=None) → ParityExportV3Document` | Methods 风格 parity JSON |
| `repro_dict_for_strict_json` | `(repro: dict) → dict` | 仅 JSON 原生类型的严格字典 |
| `repro_json_dumps` | `(repro: dict, *, indent=None, ensure_ascii=False) → str` | 稳定 UTF-8 JSON（无 NaN） |
| `SCENARIOS` / `list_scenarios_text` | 常量 / `() → str` | 入门场景目录 |

### 最小用法

```python
from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps

out = run_pipeline_from_config("configs/example_h2.yaml")
print(repro_json_dumps(out["repro"]))
```

CLI 等价：`qchem-run`、`qchem-export-parity`（见 [CLI](/reference/cli-and-scripts)）。

---

## 2. 配置加载

```python
from qchem_stack.config import load_experiment_config, validate_pre_quantum_contract

cfg = load_experiment_config("configs/example_h2.yaml")
validate_pre_quantum_contract(cfg)  # 可选：pre-quantum 门禁全集
```

`load_experiment_config` 亦从 `qchem_stack.sdk` 再导出。组合规则：[Pre-quantum YAML 矩阵](/reference/pre-quantum-yaml-matrix)。

---

## 3. 管线编排

```python
from qchem_stack.orchestration.pipeline import run_pipeline_sync, run_pipeline_from_config
# 或 from qchem_stack.sdk import ...
```

- `run_pipeline_sync(cfg)` — 化学 + 变分/ADAPT + 可选激发态 + 可选 Pauli 协议  
- `run_pipeline_from_config(path)` — 加载配置后同步跑；可选 `job_db` 入队 Pauli 作业  

结果字典含能量、`angles`、`repro` 等（schema 见 contracts）。

---

## 4. 后端：`BackendSpec` / `executor_from_spec`

```python
from qchem_stack.backends import BackendSpec, executor_from_spec

spec = BackendSpec(name="sv", provider="statevector", shots_per_circuit=1024)
exe = executor_from_spec(spec)  # → HamiltonianExpectationExecutor
```

`BackendSpec` 字段要点：`provider`（`statevector` / `qiskit` / `uqc` / …）、`shots_per_circuit`、`qiskit_mode`、UQC token 等。YAML 侧对应 `backend` 块 → 内部再转 `BackendSpec`。

见 [backends](/modules/backends) · [backend 字段](/reference/config-fields/backend)。

---

## 5. 化学求解器：`create_solver`

```python
from qchem_stack.chem.solvers import create_solver
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2.yaml")
solver = create_solver(cfg)  # 按 scf.driver 实例化 ChemIntegralSolver
```

未知 `scf.driver` → `UnknownSolverError`（可走 entry-point 插件）。见 [solvers](/modules/chem/solvers)。

---

## 6. 边界说明

| 面 | 稳定性 |
|----|--------|
| `qchem_stack.sdk` | **稳定** integrator facade |
| `config` / `orchestration.pipeline` / `backends` / `chem.solvers.create_solver` | 常用；以 SDK 再导出为准优先 |
| 内部子模块路径 | 可能随重构移动；勿在应用里深耦合 |

HTTP 作业面见 [HTTP + SQLite](/reference/http-api-sqlite-jobs) · [OpenAPI](/reference/openapi)。
