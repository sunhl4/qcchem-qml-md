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

## 5) 常见问题

- `Unknown scf.driver='entrypoint_demo'`：通常是插件没装到当前环境
- 启动 warning 提示 entry point 跳过：检查 `pyproject.toml` 的 entry point value 和导入路径
