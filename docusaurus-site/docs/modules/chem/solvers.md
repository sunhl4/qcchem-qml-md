---
title: chem · Solver 注册表
description: ChemIntegralSolver、create_solver、PySCF/Psi4/precomputed 能力位与扩展。
---

# chem · Solver 注册表

本页说明经典积分 / 平均场后端如何经统一协议接入管线，以及各驱动的能力边界。

相关：[哈密顿量](./hamiltonian) · [双线路](./dual-ingress) · [AVAS–CASSCF](./avas-casscf)。

---

## 1. 文献与问题

| 角色 | 文献 / 软件 |
|------|-------------|
| SCF / 积分 | Roothaan–Hall; PySCF; Psi4 |
| 插件化后端 | 本栈 `ChemIntegralSolver` Protocol + entry points |

量子化学变分链需要：分子几何 → 平均场参考 →（可选）活性空间积分 / 嵌入载荷。不同引擎（PySCF、Psi4、离线 bundle）能力不同；业务代码必须经 `create_solver(cfg)` 解析，禁止硬编码某一驱动的特权导入。

---

## 2. 理论思想

闭壳层 RHF 能量：

$$
E_{\mathrm{RHF}} = \mathrm{Tr}\bigl(D\,(h + F)\bigr)/2 + E_{\mathrm{nuc}}
$$

其中 $D$ 为 AO 密度，$F$ 为 Fock 矩阵。后续 CAS / 嵌入在 MO 或 AO 表象上抽取积分。  
本栈把「能跑哪些钩子」编码为 `SolverCapabilities` 位；管线按位门控，而不是按驱动名硬分支（Psi4 部分能力经 PySCF shadow 委托，见 `capability_notes`）。

---

## 3. 本栈对象与数学交接

### 3.1 `ChemIntegralSolver`（Protocol）

`chem/solvers/base.py` 表面：

| 成员 | 作用 |
|------|------|
| `capabilities` | `SolverCapabilities` |
| `set_physical_data(cfg)` | 绑定分子 / 基组等 |
| `compute_mean_field(*, periodic=False)` | → `MolecularMeanFieldResult` |
| `get_integrals(...)` | 在线积分（precomputed 无） |
| `build_embedding_input_system(...)` | 嵌入 AO/MO 载荷 |

`MolecularMeanFieldResult`：`mf`、`e_tot`、`mo_energy`、`driver_meta`。

### 3.2 注册表

`chem/solvers/registry.py`：

```python
create_solver(cfg) -> ChemIntegralSolver
register_solver(name, factory, *, overwrite=False)
```

- Entry point 组：`qchem_stack.chem_solvers`  
- 内置 id：`pyscf`、`psi4`、`precomputed`、`custom_external_template`  
- 配置加载时 `validate_scf_driver_registered`

### 3.3 实现类

| Class | 路径 | 工厂 |
|-------|------|------|
| `PySCFIntegralSolver` | `solvers/pyscf_solver.py` | `from_experiment_config` |
| `Psi4IntegralSolver` | `solvers/psi4_solver.py` | 同上 |
| `PrecomputedIntegralSolver` | `solvers/precomputed_solver.py` | 同上 |

**能力预设**（`integration/presets.py` 概念）：

- **pyscf**：PBC、Schmidt、projection、AVAS、CASSCF audit、RDM/NEVPT2、`get_integrals` 等全表面  
- **psi4**：同名字位；许多项 `native=False`（shadow）  
- **precomputed**：仅 SCF 参考 + bundle 内哈密顿量；无 live 积分 / 嵌入钩子

---

## 4. YAML 参数表

```yaml
scf:
  driver: pyscf              # pyscf | psi4 | precomputed | 已注册插件 id
  method: RHF                # RHF | ROHF | UHF
  # basis / 分子几何见 molecule 块
  pyscf:
    max_cycle: null
    chkfile: null
    init_guess: null
    level_shift: null
    use_newton: false
    diis_space_dimension: null
    density_fit: false
    density_fit_auxbasis: null
  psi4:
    # 与 pyscf 控制面同形
  precomputed:
    bundle_path: null        # driver=precomputed 时必需
```

| 字段 | 默认 | 约束 |
|------|------|------|
| `scf.driver` | `pyscf` | 必须已注册 |
| `scf.method` | `RHF` | Schmidt / AVAS 等常强制 RHF |
| `scf.pyscf.*` | 见上 | 仅 `driver=pyscf` 时有意义 |
| `scf.precomputed.bundle_path` | `null` | 相对 YAML 目录解析 |

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.solvers.registry import (
    create_solver,
    registered_solver_ids,
    register_solver,
)

cfg = load_experiment_config("configs/example_h2.yaml")
print("pyscf" in registered_solver_ids())
solver = create_solver(cfg)
print(type(solver).__name__, solver.capabilities)

# 插件扩展（进程内）
# register_solver("my_scf", my_factory)
```

桥接平均场（推荐业务入口）：

```python
from qchem_stack.chem.bridges import classical_mean_field_via_solver_bridge

ref = classical_mean_field_via_solver_bridge(cfg)
print(ref.e_tot)
```

Entry point 脚手架：见 `examples/solver_plugin_entrypoint_demo/`。

---

## 6. 验证命令

```bash
pytest tests/chem/test_solver_registry_contract.py \
  tests/chem/test_pyscf_solver_adapter.py \
  tests/chem/test_psi4_solver_smoke.py \
  tests/chem/test_precomputed_solver_roundtrip.py -q

python -c "from qchem_stack.chem.solvers.registry import create_solver, registered_solver_ids; from qchem_stack.config import load_experiment_config; print('pyscf' in registered_solver_ids()); print(type(create_solver(load_experiment_config('configs/example_h2.yaml'))).__name__)"
```

期望：`True` 与 `PySCFIntegralSolver`（或当前驱动对应类名）。

---

## 7. 调参建议

| 场景 | 建议 |
|------|------|
| 默认开发 | `pyscf` + RHF；小分子用 `max_cycle` 收敛诊断 |
| 引擎对照 | 同分子换 `psi4`，比对 `e_tot` 与哈密顿指纹（见 parity 测试） |
| 无 PySCF CI | `driver: precomputed` + [双线路](./dual-ingress) |
| 难收敛 | `level_shift`、`use_newton`、`density_fit`（PySCF） |
| 嵌入 / AVAS | 确认 `capabilities` 对应位为真；precomputed 会挡住 live 钩子 |

---

## 8. 相关

- [双线路](./dual-ingress) · [哈密顿量](./hamiltonian) · [AVAS–CASSCF](./avas-casscf)  
- 仓库：`docs/说明_经典化学后端驱动_registry与能力位.md` · `src/qchem_stack/chem/README.md`  
- 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
