---
title: chem 模块
description: 经典化学层导航枢纽：平均场、积分、映射、嵌入与 PreQuantumInput。
---

# chem 模块

`qchem_stack.chem` 把分子问题变成下游可消费的 `PreQuantumInput` / `QubitHamiltonian`。

本页是 **导航枢纽**；深读内容在子页（手册级：文献 → 理论 → 本栈数学 → YAML → 调用 → 验证 → 调参）。

---

## 1. 定位

| 项 | 说明 |
|----|------|
| 源码 | `src/qchem_stack/chem/` |
| 管线阶段 | `scf`、`pre_quantum` |
| 上游 | `config`（`molecule` / `scf` / `active_space` / `embedding`） |
| 下游 | `quantum`、`protocols`、`orchestration` |
| 选型 | [P1 化学与嵌入](/guide/chemistry-and-embedding) |

典型链：

```text
ExperimentConfig
  → create_solver(cfg)
  → classical mean-field reference
  → build_pre_quantum_input  (resolve_pre_quantum_path)
  → PreQuantumInput (pre_quantum_input_v1)
```

---

## 2. 理论速写

$$
\hat{H} = E_{\mathrm{nuc}} + \sum_{pq} h_{pq}\, a_p^\dagger a_q + \frac{1}{2}\sum_{pqrs} g_{pqrs}\, a_p^\dagger a_q^\dagger a_s a_r
$$

$$
\hat{H}_{\mathrm{qubit}} = M(\hat{H}) = \sum_k c_k\, P_k
$$

活性空间限制轨道指标；嵌入则把 $M(\hat{H})$ 建在杂质 / 片段子空间上。主 `qh` 在变分前固定。

---

## 3. 深读目录

### 3.1 核心交接

| 主题 | 深读 |
|------|------|
| Solver 注册表（PySCF / Psi4 / precomputed） | [solvers](./solvers) |
| `QubitHamiltonian` / 指纹 / `PreQuantumInput` | [hamiltonian](./hamiltonian) |
| 费米子–比特映射 | [mappings](./mappings) |
| 在线 SCF ↔ precomputed bundle | [dual-ingress](./dual-ingress) |

### 3.2 活性空间

| 主题 | 深读 |
|------|------|
| AVAS 策略与 CASSCF 审计 / 积分 | [avas-casscf](./avas-casscf) |

### 3.3 嵌入

| 主题 | 深读 |
|------|------|
| 模式总览与 `PreQuantumPath` | [embedding](./embedding) |
| DMET + 密度反馈 | [embedding-dmet](./embedding-dmet) |
| Mulliken MO projection | [embedding-projection](./embedding-projection) |
| Schmidt 生产管线（RHF only） | [embedding-schmidt](./embedding-schmidt) |

---

## 4. 公开 API（速查）

```python
from qchem_stack.chem.solvers.registry import create_solver, registered_solver_ids
from qchem_stack.chem.fermion_mapping_registry import list_documented_fermion_qubit_mappings
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path
from qchem_stack.sdk import run_pipeline_from_config

print(registered_solver_ids())
print(list_documented_fermion_qubit_mappings())

cfg = load_experiment_config("configs/example_h2.yaml")
print(resolve_pre_quantum_path(cfg))
out = run_pipeline_from_config("configs/example_h2.yaml")
print(out["pre_quantum_input"]["hamiltonian_fingerprint"][:16])
```

业务代码优先走编排 / SDK；不必手写全链。

---

## 5. YAML 索引

| YAML 区 | 作用 | 深读 |
|---------|------|------|
| `scf.driver` / `scf.*` | 经典后端 | [solvers](./solvers) |
| `active_space.*` | CAS / 映射 | [hamiltonian](./hamiltonian) · [mappings](./mappings) |
| `chemistry_extended.avas` / `casscf` | AVAS–CASSCF | [avas-casscf](./avas-casscf) |
| `embedding.mode` | 嵌入分支 | [embedding](./embedding) |
| `scf.precomputed.bundle_path` | 离线车道 | [dual-ingress](./dual-ingress) |

---

## 6. 验证命令

```bash
python -c "from qchem_stack.chem.fermion_mapping_registry import list_documented_fermion_qubit_mappings; print(list_documented_fermion_qubit_mappings())"

python -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print(o['pre_quantum_input']['hamiltonian_fingerprint'][:16])"

pytest tests/chem/test_pre_quantum_path.py tests/chem/test_hamiltonian_fingerprint.py -q
```

---

## 7. 边界与相关

- PySCF 是**示例后端**，不是架构特权依赖；新驱动走 `ChemIntegralSolver` + entry point。  
- 深度参考：`docs/说明_chem模块技术参考手册.md`  
- 选型：[费米子映射](/guide/fermion-qubit-mappings) · [双线路](/guide/dual-classical-ingress) · [P1 化学与嵌入](/guide/chemistry-and-embedding)  
- 下游算法：[算法深读索引](/modules/quantum/algorithms/)
