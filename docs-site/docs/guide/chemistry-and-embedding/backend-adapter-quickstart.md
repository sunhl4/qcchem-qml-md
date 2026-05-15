# 后端适配快速接入（模板 + 自检）

本文给你一条最短路径，把新的经典计算化学软件接到 `qchem_stack` 的统一输入输出接口。

可选：先自动生成骨架，再填 TODO。

```bash
python scripts/create_solver_adapter_scaffold.py my_backend
# 同时生成可执行的注册 + 合同自检演示脚本（默认 scripts/register_my_backend_demo.py；
# 与 scripts/check_solver_adapter_contract.py 等价检查，同进程执行）：
python scripts/create_solver_adapter_scaffold.py my_backend --with-demo-register
python scripts/register_my_backend_demo.py
```

## 1) 复制模板并改名

模板文件：`src/qchem_stack/chem/solvers/custom_solver_template.py`

建议复制为你自己的实现，例如：

- `src/qchem_stack/chem/solvers/my_backend_solver.py`
- 将 `CustomExternalIntegralSolver` 改为 `MyBackendIntegralSolver`
- 将 `capabilities.backend_id` 改为你的后端标识

## 2) 实现最小方法

MVP 至少实现：

- `set_physical_data(cfg)`
- `compute_mean_field(periodic=False)`（或 `run_molecular_mean_field`）
- `capabilities`（准确声明支持范围）

返回值必须是 `MolecularMeanFieldResult`。

## 3) 注册到 solver registry

可在运行时注册（推荐先这样做）：

```python
from qchem_stack.chem.solvers import register_solver
from qchem_stack.chem.solvers.my_backend_solver import MyBackendIntegralSolver

register_solver("my_backend", MyBackendIntegralSolver.from_experiment_config)
```

同名后端已存在时，默认会抛 `SolverRegistrationError`；若你**明确**要替换实现，使用 `overwrite=True`：

```python
register_solver("my_backend", MyBackendIntegralSolver.from_experiment_config, overwrite=True)
```

然后在配置里使用：

```yaml
scf:
  driver: my_backend
```

`scf.driver` 为任意非空、无内部空白的 **solver id** 字符串（会规范化为小写）；未知 id 在 `create_solver` 时抛 `UnknownSolverError`，非法 id（例如全空白）抛 `InvalidSolverIdError`。

### 3a) 安装级插件（pip + entry points）

无需在业务代码里 `register_solver`：在独立 Python 包的 `pyproject.toml` 中声明 entry point group `qchem_stack.chem_solvers`，安装后首次访问 registry 时会自动发现。详见仓库内 [Solver Entry Point 插件安装与发布指南](../../../../docs/solver_entrypoint_plugin_安装与发布指南.md) 与示例 `examples/solver_plugin_entrypoint_demo/`。

### 3b) 可观测性与 entry point 冲突策略

排查「谁注册了这个 driver」时：

```python
from qchem_stack.chem.solvers import registered_solvers_detail, set_entrypoint_conflict_policy

# 只读映射：solver_id -> (source: builtin|entrypoint|runtime, provider 字符串)
for sid, meta in registered_solvers_detail().items():
    print(sid, meta.source, meta.provider)
```

多个插件对**同一** entry point 名称注册冲突时：

- `set_entrypoint_conflict_policy("warn")`（**默认**）：打 `RuntimeWarning` 并**保留按 name/value 排序后最先成功注册**的那条。
- `set_entrypoint_conflict_policy("strict")`：冲突时直接抛 `SolverRegistrationError`，适合 CI / 生产硬门禁。

如果你想先看一份可运行示例（不改业务代码）：

- 适配器示例：`src/qchem_stack/chem/solvers/mock_external_solver_example.py`
- 一键演示脚本：`python scripts/demo_mock_external_backend.py`
- 该示例已标出 `TODO[1]`、`TODO[2]`、`TODO[3]` 三个必改锚点（能力声明 / SCF 调用 / 积分导出）

## 4) 跑适配合同自检脚本

脚本：`scripts/check_solver_adapter_contract.py`

```bash
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend --run-mean-field
```

如果你的后端还没实现数值 SCF，可先不加 `--run-mean-field`，先通过结构契约检查。

## 5) 打通活性空间哈密顿量路径（可后做）

若你还没有提供活性空间积分，保持：

- `supports_restricted_active_space_qubit_hamiltonian=False`

这时 pipeline 会给出精确错误，但不会影响插件路径（`embedding.mode=plugin`）。

当你实现了 `CanonicalActiveSpaceIntegralPack` 等价能力后，再把该 capability 切为 `True`。

## 6) 回归建议

- `tests/test_chem_integral_solver_tangelo_aliases.py`
- `tests/test_solver_adapter_contract.py`
- `tests/test_orchestration_pipeline.py`
- `tests/test_mock_external_backend_example.py`
- （可选）`python scripts/check_solver_adapter_contract.py ... --run-mean-field --require-mean-field-success`

## 相关文档

- [多后端统一输入输出适配合同](/guide/chemistry-and-embedding/backend-adapter-unified-io)
- [命令行与脚本](/reference/cli-and-scripts)
- 仓库内：[Solver Entry Point 插件安装与发布指南](../../../../docs/solver_entrypoint_plugin_安装与发布指南.md)
- Docusaurus 站点镜像（`npm start`）：仓库 `docusaurus-site/docs/guide/backend-adapter-quickstart.md`
