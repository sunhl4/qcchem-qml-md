---
title: chem · AVAS 与 CASSCF
description: AVAS 活性空间策略、CASSCF 轨道审计与积分旋转。
---

# chem · AVAS 与 CASSCF

本页说明如何用 AVAS 自动选定活性空间，以及可选的 CASSCF 轨道优化审计 / 积分路径。

相关：[哈密顿量](./hamiltonian) · [Solver](./solvers) · [chem 索引](/modules/chem/)。

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| AVAS | Sayfutyarova et al., J. Chem. Theory Comput. **13**, 4063 (2017) |
| CASSCF | Roos 等；PySCF `mcscf`；Psi4 `casscf` |
| 本栈对照 | 仓库 `docs/活性空间指定与AVAS_理论实践与开源对照.md` |

手工指定 CAS$(n_e,n_o)$ 依赖化学直觉。AVAS（Atomic Valence Active Space）用目标 AO 标签投影，从 RHF MO 中自动挑出价活性空间，降低试错成本。CASSCF 可进一步旋转轨道；本栈区分 **audit-only** 与 **for integrals** 两种开关。

---

## 2. 理论思想

AVAS：构造投影算符到选定原子价 AO，对占据 / 虚轨道做投影本征分析，按阈值挑出活性 MO，得到 $(n_{\mathrm{cas}}, n_{\mathrm{elec}})$。  
CASSCF：在固定活性空间上变分优化

$$
E = \langle \Psi_{\mathrm{CAS}} | \hat{H} | \Psi_{\mathrm{CAS}} \rangle
$$

并更新 `mo_coeff`。本栈若开启 `orbital_optimization_for_integrals`，则在抽取 CASCI 积分前旋转轨道；若仅 `orbital_optimization_audit`，则记录审计而不改变主积分路径语义（以配置与 hook 实现为准）。

---

## 3. 本栈实现

| API | 路径 | 作用 |
|-----|------|------|
| `apply_avas_projection` | `active_space/avas_projection.py` | PySCF `mcscf.avas.AVAS`；Psi4 经 shadow |
| `casscf_energy_and_maybe_orbitals` | `active_space/pyscf_active_space_hooks.py` | PySCF CASSCF |
| `Psi4ActiveSpaceHooks` | `active_space/psi4_active_space_hooks.py` | Psi4 `energy("casscf")` |
| hooks registry | `active_space/hooks_registry.py` | `pyscf` / `psi4` |

策略解析：`active_space/resolution.py`。  
积分：`integrals/pyscf_active_space.py`、`integrals/psi4_active_space.py`。

### AVAS 约束

- 仅分子分支（无 PBC）  
- `scf.method='RHF'`  
- 写入 `driver_meta`：`resolved_active_space_meta`、`avas_atomic_projection_executed`

### CASSCF 约束

- PySCF hooks：上游 tag `pyscf`；无 PBC  
- Psi4 hooks：`scf.method=RHF`；无 PBC  
- 审计 schema：`casscf_orbital_audit_v1`  
- `precomputed` 驱动排除 live AVAS/CASSCF 钩子  

---

## 4. YAML 参数表

```yaml
active_space:
  strategy: avas                 # cas | manual | avas | avas_stub
chemistry_extended:
  avas:
    ao_labels: ["H 1s"]          # 必需（按分子调整）
    threshold: 0.2
    minao: minao
    with_iao: false
    openshell_option: 2
    canonicalize: true
    ncore: 0
  casscf:
    orbital_optimization_audit: false
    orbital_optimization_for_integrals: false
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `active_space.strategy` | `cas` | 设为 `avas` 启用 |
| `chemistry_extended.avas.ao_labels` | `[]` | 目标 AO 标签（必需） |
| `avas.threshold` | `0.2` | AVAS 阈值 |
| `avas.minao` | `minao` | 最小基投影 |
| `avas.ncore` | `0` | 冻结芯 |
| `casscf.orbital_optimization_audit` | `false` | 写审计 |
| `casscf.orbital_optimization_for_integrals` | `false` | 旋转后再抽积分 |

示例：`configs/example_h2_avas_casscf_workflow.yaml`、`example_h2_avas.yaml`、`example_h2_psi4_avas.yaml`。

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.sdk import run_pipeline_from_config

cfg = load_experiment_config("configs/example_h2_avas_casscf_workflow.yaml")
print(cfg.active_space.strategy)

out = run_pipeline_from_config("configs/example_h2_avas_casscf_workflow.yaml")
print(out["pre_quantum_input"]["hamiltonian_fingerprint"][:24])
```

能力门控：

```python
from qchem_stack.chem.solvers.registry import create_solver

solver = create_solver(cfg)
print(solver.capabilities)  # 需支持 AVAS / CASSCF 相关位
```

---

## 6. 验证命令

```bash
pytest tests/chem/test_pyscf_avas_resolve.py \
  tests/chem/test_avas_capability_gate.py \
  tests/chem/test_active_space_hooks_registry.py \
  tests/chem/test_active_space_strategy_unified.py -q

python -c "from qchem_stack.config import load_experiment_config; print(load_experiment_config('configs/example_h2_avas_casscf_workflow.yaml').active_space.strategy)"
```

期望打印 `avas`。

---

## 7. 调参建议

| 目标 | 建议 |
|------|------|
| 活性空间过大 | 提高 `threshold`；收紧 `ao_labels` |
| 过小 / 漏轨道 | 降低 `threshold`；检查 `minao` / `with_iao` |
| 只要自动 CAS 尺寸 | `strategy: avas`，CASSCF 两开关保持 `false` |
| 轨道优化实验 | 先开 `orbital_optimization_audit`；确认后再开 `for_integrals` |
| Psi4 | 用 `example_h2_psi4_avas.yaml`；注意 shadow 能力 |

---

## 8. 相关

- [哈密顿量](./hamiltonian) · [Solver](./solvers) · [双线路](./dual-ingress)  
- 仓库：`docs/活性空间指定与AVAS_理论实践与开源对照.md`  
- 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
