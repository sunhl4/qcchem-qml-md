# Solver Entrypoint Demo Plugin

这个目录演示“外部 pip 包通过 entry points 自动接入 `qchem_stack` solver registry”。

## 1) 安装插件

在 `qchem_stack` 的同一 Python 环境执行：

```bash
pip install -e ./examples/solver_plugin_entrypoint_demo
```

## 2) 验证 registry 自动发现

```bash
python - <<'PY'
from qchem_stack.chem.solvers import registered_solver_ids
print("entrypoint_demo" in registered_solver_ids())
print(sorted(registered_solver_ids()))
PY
```

## 3) 使用插件后端

将配置中的 `scf.driver` 改为：

```yaml
scf:
  driver: entrypoint_demo
```

然后照常跑 pipeline 或 `create_solver(cfg)`。

## 4) 你应该替换的内容

- `demo_solver.py` 里的 `run_molecular_mean_field`：改为真实后端 SCF 调用
- `capabilities`：按真实能力声明 flags
- `get_integrals`：若要支持活性空间哈密顿量路径，补齐 AO/MO 积分导出

## 5) 10 分钟插件接入 checklist

| # | 动作 | 验证 |
|---|------|------|
| 1 | `pip install -e ./examples/solver_plugin_entrypoint_demo` | `entrypoint_demo` ∈ `registered_solver_ids()` |
| 2 | 复制 `demo_solver.py` 为新 backend id | `capabilities.backend_id` 与 YAML `scf.driver` 一致 |
| 3 | 实现 `run_molecular_mean_field`（或 PBC 路径） | `pytest tests/test_create_solver_adapter_scaffold_script.py -q`（scaffold 可选） |
| 4 | 在 `pyproject.toml` 注册 `[project.entry-points."qchem_stack.solvers"]` | 重启 Python；无 entry point skip warning |
| 5 | 用代表 YAML 跑通：`configs/example_h2.yaml` 改 `scf.driver` | `run_pipeline_from_config(...)` 返回 `scf_energy` |
| 6 | 若需活性空间：实现 `get_integrals` + 声明 `supports_restricted_active_space_qubit_hamiltonian` | `python scripts/check_solver_adapter_contract.py`（若适用） |
| 7 | 提交 PR：README 片段 + 最小测试或 smoke 说明 | CI `lint` + `test` 绿 |

**variational / 量子后端插件**：经典 SCF 用 entry point；变分或采样后端走 `BackendSpec` / registry 文档（见根目录 `CONTRIBUTING.md` 插件章节）。

## 6) 常见问题

- `Unknown scf.driver='entrypoint_demo'`：通常是插件没装到当前环境
- 启动 warning 提示 entry point 跳过：检查 `pyproject.toml` 的 entry point value 和导入路径
