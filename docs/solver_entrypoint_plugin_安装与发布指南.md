# Solver Entry Point 插件安装与发布指南

本文对应 `chem/solvers/registry.py` 的新机制：`qchem_stack` 在启动时会自动扫描 Python entry points（group: `qchem_stack.chem_solvers`），把外部后端注册为 `scf.driver` 可选值。

## 1. 设计目标（为什么要用 entry points）

- **安装即接入**：`pip install` 后无需手动 `import` + `register_solver(...)`
- **运行时解耦**：主仓库不依赖具体三方后端包，插件按需安装
- **版本自治**：插件独立发版，不阻塞主仓库迭代
- **冲突可控**：同名 backend id 默认拒绝覆盖，避免静默踩踏

## 2. 最小插件包结构

建议目录：

```text
your-solver-plugin/
  pyproject.toml
  src/
    your_solver_plugin/
      __init__.py
      solver.py
```

`solver.py` 中实现 `ChemIntegralSolver` 形状（至少提供 `from_experiment_config`、`compute_mean_field`、`capabilities`）。

## 3. `pyproject.toml` 关键配置

```toml
[project]
name = "your-solver-plugin"
version = "0.1.0"
dependencies = ["qchem-stack>=0.1.0", "numpy>=1.24"]

[project.entry-points."qchem_stack.chem_solvers"]
your_backend = "your_solver_plugin.solver:YourBackendIntegralSolver"
```

说明：

- `your_backend` 必须与 YAML 的 `scf.driver` 对齐（会被规范化为小写）
- entry point value 可以是：
  - **可调用工厂**：`factory(cfg) -> ChemIntegralSolver`
  - **类对象**：类上提供 `from_experiment_config(cfg)`

## 4. 安装与使用

```bash
# 在主仓库环境中安装插件（开发模式）
pip install -e ./path/to/your-solver-plugin

# 检查 registry 是否可见
python - <<'PY'
from qchem_stack.chem.solvers import registered_solver_ids, registered_solvers_detail

print(sorted(registered_solver_ids()))
for sid, meta in registered_solvers_detail().items():
    print(sid, meta.source, meta.provider)
PY
```

YAML 使用：

```yaml
scf:
  driver: your_backend
  method: RHF
```

## 5. 本仓库推荐验证流程

1. 结构/协议检查（不跑数值）  
   `python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver your_backend`
2. 数值路径检查（可选）  
   `python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver your_backend --run-mean-field`
3. 管线连通检查  
   使用任意 `configs/example_*.yaml`，将 `scf.driver` 切到你的 backend

## 5.1 可观测性（排障）

`registered_solvers_detail()` 返回**只读**映射：每个 `solver_id` 对应 `source`（`builtin` / `entrypoint` / `runtime`）与 `provider`（例如 entry point 的 `module:attr` 字符串或内置注册路径），便于确认「当前进程里到底是谁提供了该 driver」。

## 6. 常见错误与排障

- **`Unknown scf.driver=...`（`UnknownSolverError`）**  
  `scf.driver` 语法合法且已规范化，但该 id 未在 registry 中注册：检查插件是否安装到**当前** Python 环境、entry point group 是否为 `qchem_stack.chem_solvers`。

- **`InvalidSolverIdError`**  
  `scf.driver` 非法（例如全空白、规范化后仍含空白字符）。应在 YAML / 配置层修正。

- **启动时 warning: Skipping solver entry point ...**  
  常见原因：entry point 导入失败（依赖缺失、模块路径错误、目标不是可调用工厂且类上无 `from_experiment_config`）。  
  若日志里是 **同一 solver 名称被多个 entry point 争抢**，属于 **id 冲突**：默认策略为 `warn`，会跳过后续条目并保留排序后最先成功注册的那条。

### 6.1 entry point 冲突策略（`warn` / `strict`）

```python
from qchem_stack.chem.solvers import set_entrypoint_conflict_policy

set_entrypoint_conflict_policy("warn")   # 默认：冲突时 RuntimeWarning，保留首次成功注册
set_entrypoint_conflict_policy("strict") # CI / 生产硬门禁：冲突时直接抛 SolverRegistrationError
```

- **同名注册失败（already registered）**（`SolverRegistrationError`）  
  与「多个 entry point 抢同一名字」不同：指在**不允许覆盖**的前提下重复注册。处理方式：修改插件 id、卸载冲突包、或在**明确可控**的场景对运行时 `register_solver(..., overwrite=True)` 使用覆盖（不建议用于随意安装的 entry point 插件）。

## 7. 何时用“运行时注册”而非 entry points

以下场景可继续使用 `register_solver(...)`：

- notebook / 单脚本实验
- 临时本地调试（不需要安装发布）
- 同一进程内动态替换实现

面向团队交付、CI/CD、可重复部署时，优先使用 entry points 插件模型。

## 8. 参考示例

- 外部插件骨架示例：`examples/solver_plugin_entrypoint_demo/`
- 适配器生成器（仓库内实现）：`scripts/create_solver_adapter_scaffold.py`
- 合同检查器：`scripts/check_solver_adapter_contract.py`
- 适配快速上手（Docusaurus）：`docusaurus-site/docs/guide/backend-adapter-quickstart.md`
