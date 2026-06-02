# PySCFDriver → ChemIntegralSolver 迁移指南

> **Status (v0.6.0):** `PySCFDriver` and `chem/drivers/pyscf_driver*.py` have been **removed**. Use the paths below exclusively.

本文档帮助从 legacy `PySCFDriver` 迁移到统一经典化学接口 `ChemIntegralSolver` + bridge 交换层。

## 推荐路径（新代码）

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.chem.bridges.facade import classical_mean_field_reference_from_config
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input

cfg = load_experiment_config("configs/example_h2.yaml")
reference = classical_mean_field_reference_from_config(cfg)
pqi = build_pre_quantum_input(cfg, reference)
```

或直接：

```python
from qchem_stack.orchestration.pipeline import run_pipeline_sync

out = run_pipeline_sync(cfg, cfg_path=Path("configs/example_h2.yaml"))
```

## Import 对照表

| Legacy | 推荐替代 |
|--------|----------|
| `from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver` | `from qchem_stack.chem.solvers.registry import create_solver` |
| `PySCFDriver(system, method=...).run_rhf()` | `create_solver(cfg).compute_mean_field(...)` |
| `molecular_hamiltonian_from_classical_reference(...)` | `build_pre_quantum_input(cfg, reference)`（旧 API 仍可用但 `DeprecationWarning`） |
| `classical_mean_field_reference_from_config` 前的手写 PySCF | `qchem_stack.chem.bridges.facade.classical_mean_field_via_solver_bridge` |

## 能力位与多后端

- 新代码应通过 `SolverCapabilities` 探测后端能力，而非 `isinstance(..., PySCFMol)`。
- Psi4、precomputed bundle 等后端见 [`说明_经典化学后端驱动_registry与能力位.md`](说明_经典化学后端驱动_registry与能力位.md)。

## Deprecation 时间线

- **v0.6.0（当前）**：`PySCFDriver` 已移除；`chem.drivers` 仅保留 `PySCFRHFResult` 类型别名。
- 历史版本曾发出 `DeprecationWarning`；见 CHANGELOG `[0.6.0]` Removed 条目。

## 相关文档

- [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md) §1.1、§1.2
- [`统一经典化学接口_ChemIntegralSolver与下游无关性.md`](统一经典化学接口_ChemIntegralSolver与下游无关性.md)
- [`说明_scf配置.md`](说明_scf配置.md)
