---
title: 后端适配快速接入
description: 模板、运行时注册、pip entry points、registry 排障与冲突策略（与仓库插件指南互补）。
---

# 后端适配快速接入

本文即 Docusaurus 站内 **后端适配快速接入** 母稿；本地浏览：`cd docusaurus-site && npm start`。插件安装与发布另见仓库 [solver 插件安装与发布指南](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/solver_entrypoint_plugin_%E5%AE%89%E8%A3%85%E4%B8%8E%E5%8F%91%E5%B8%83%E6%8C%87%E5%8D%97.md)。

## 可选：脚手架

```bash
python scripts/create_solver_adapter_scaffold.py my_backend
python scripts/create_solver_adapter_scaffold.py my_backend --with-demo-register
python scripts/register_my_backend_demo.py
```

## 1) 模板与最小实现

- 模板：`src/qchem_stack/chem/solvers/custom_solver_template.py`
- MVP：`set_physical_data`、`compute_mean_field`（或 `run_molecular_mean_field`）、准确的 `capabilities`
- 返回：`MolecularMeanFieldResult`

## 2) 运行时注册

```python
from qchem_stack.chem.solvers import register_solver
from qchem_stack.chem.solvers.my_backend_solver import MyBackendIntegralSolver

register_solver("my_backend", MyBackendIntegralSolver.from_experiment_config)
```

若同名已存在，默认抛 `SolverRegistrationError`；仅在明确要替换时使用 `overwrite=True`。

```yaml
scf:
  driver: my_backend
```

`scf.driver` 为合法 **solver id**（非空、无内部空白，会规范化为小写）。`create_solver` 时：未注册抛 `UnknownSolverError`，非法 id 抛 `InvalidSolverIdError`。

## 3) 安装级插件（pip + entry points）

在独立包的 `pyproject.toml` 中声明：

```toml
[project.entry-points."qchem_stack.chem_solvers"]
my_backend = "my_plugin.solver:MyBackendIntegralSolver"
```

安装后首次访问 registry 即发现。示例：`examples/solver_plugin_entrypoint_demo/`。

## 4) 可观测性与冲突策略

```python
from qchem_stack.chem.solvers import registered_solvers_detail, set_entrypoint_conflict_policy

for sid, meta in registered_solvers_detail().items():
    print(sid, meta.source, meta.provider)  # source: builtin | entrypoint | runtime
```

多个 entry point 争抢同一名称时：

- `set_entrypoint_conflict_policy("warn")`（默认）：`RuntimeWarning`，保留排序后最先成功注册的一条。
- `set_entrypoint_conflict_policy("strict")`：抛 `SolverRegistrationError`，适合 CI。

## 5) 合同自检

```bash
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend --run-mean-field
```

更多脚本见 [命令行与脚本](/reference/cli-and-scripts)。

## 相关

- [P1 化学与嵌入](./chemistry-and-embedding)
- [命令行与脚本](/reference/cli-and-scripts)
