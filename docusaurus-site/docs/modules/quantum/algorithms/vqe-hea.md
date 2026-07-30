---
title: VQE 与硬件高效 ansatz（HEA）
description: 混合变分本征求解完整手册：文献、HEA 电路、优化、YAML/Python API、端到端示例。
---

# VQE 与硬件高效 ansatz（HEA）

本页是 **使用者手册级** 说明（风格对齐 PennyLane / InQuanto 算法章）：先讲问题与理论，再落到本栈电路、优化器、配置字段与可复制调用。

相关选型：[算法菜单](/guide/algorithm-and-ansatz-menu) · 后端：[statevector](/modules/backends/statevector) · [Qiskit](/modules/backends/qiskit)。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| VQE 实验提出 | A. Peruzzo et al., *A variational eigenvalue solver on a photonic quantum processor*, [Nat. Commun. **5**, 4213 (2014)](https://doi.org/10.1038/ncomms5213) |
| 混合变分理论 | J. R. McClean et al., *The theory of variational hybrid quantum-classical algorithms*, [New J. Phys. **18**, 023023 (2016)](https://doi.org/10.1088/1367-2630/18/2/023023) |
| HEA / 超导硬件 | A. Kandala et al., *Hardware-efficient variational quantum eigensolver for small molecules and quantum magnets*, [Nature **549**, 242 (2017)](https://doi.org/10.1038/nature23879) |
| 贫瘠高原 | McClean et al., *Barren plateaus in quantum neural network training landscapes*, [Nat. Commun. **9**, 4812 (2018)](https://doi.org/10.1038/s41467-018-07090-4) |

---

## 2. 要解决什么问题

电子结构的基态能量

$$
E_0 = \min_{|\psi\rangle}\,\langle\psi|\hat{H}|\psi\rangle
$$

在经典上对大活性空间困难；在量子上，通用 **量子相位估计（QPE）** 需要深电路与容错。  
**VQE** 把问题改成「浅层参数化电路 + 经典优化」：量子设备只负责估能量（或梯度），经典计算机更新参数。

**HEA**（hardware-efficient ansatz）不按化学激发构造电路，而用设备友好的旋转 + 纠缠层重复堆叠，适合先验证管线、小分子烟雾测试；化学精度通常不如 [UCCSD](./uccsd)。

---

## 3. 理论思想

### 3.1 混合循环

1. 制备 $|\psi(\boldsymbol{\theta})\rangle = U(\boldsymbol{\theta})|0\rangle^{\otimes n}$。  
2. 将 $\hat{H}=\sum_k c_k P_k$ 分组测量，得到

$$
E(\boldsymbol{\theta})=\sum_k c_k\,\langle P_k\rangle_{\boldsymbol{\theta}}
$$

3. 经典优化器求 $\boldsymbol{\theta}^\star=\arg\min E(\boldsymbol{\theta})$。  
4. 重复直到收敛或达到 `maxiter`。

### 3.2 为何有效 / 风险

- **优点**：电路深度可控；可接噪声缓解；易换成不同后端。  
- **风险**：贫瘠高原（随机初始化时梯度方差指数小）；局部极小；HEA 缺乏粒子数对称性时可能落到错误扇区。

---

## 4. 数学实现（本栈）

### 4.1 HEA 电路（`hea_state`）

实现：`qchem_stack.quantum.statevector.hea_state`。

- 初态：$|0\rangle^{\otimes n}$。  
- 每一层 $d=0,\ldots,D-1$，对每个比特 $q$ 依次施加 $R_y(\theta)$、$R_x(\phi)$，再做 **线性 CNOT 链**（`entangler="linear_cnot"`）：

$$
\mathrm{CNOT}_{0,1}\,\mathrm{CNOT}_{1,2}\,\cdots\,\mathrm{CNOT}_{n-2,n-1}
$$

- 参数总数：

$$
n_{\mathrm{params}} = 2\, n\, D
$$

其中 $D=$ `quantum.vqe.depth`，$n=$ 量子比特数。

旋转矩阵（与源码一致）：

$$
R_y(\theta)=\begin{pmatrix}\cos\frac{\theta}{2}&-\sin\frac{\theta}{2}\\ \sin\frac{\theta}{2}&\cos\frac{\theta}{2}\end{pmatrix},\quad
R_x(\phi)=\begin{pmatrix}\cos\frac{\phi}{2}&-i\sin\frac{\phi}{2}\\ -i\sin\frac{\phi}{2}&\cos\frac{\phi}{2}\end{pmatrix}
$$

### 4.2 能量评估

类：`qchem_stack.quantum.algorithms.vqe.VQE`。

- 默认执行器：`StatevectorHeaExecutor`（精确态矢量）。  
- `build()` 装配 `ExpectationValue` + `ProtocolRunner`（可挂辅助量与梯度表达式）。  
- `run()` 用 SciPy `minimize`，目标函数每次调用 `evaluate_objective` 或 `expectation_hea`。

### 4.3 优化器

| `optimizer_method` | 说明 |
|--------------------|------|
| `COBYLA`（默认） | 无梯度；适合噪声/黑盒期望 |
| `L-BFGS-B` | 准牛顿；需较光滑目标 |
| `Nelder-Mead` | 单纯形；小维度可用 |

初值：默认 `seed` 下均匀 $U(-\pi,\pi)^{n_{\mathrm{params}}}$；YAML 亦可 `initial_parameters_strategy: zeros`。

### 4.4 结果对象

`VQEResult`：

| 字段 | 含义 |
|------|------|
| `energy` | 最优能量 |
| `angles` | 最优参数向量 |
| `nfev` | 目标函数评估次数 |
| `gradient_at_optimum` | 若 runner 提供梯度 |
| `auxiliary_values` | 辅助可观测量 |
| `meta` | SciPy message、optimizer 名、可选 `energy_trace` |

报告 schema：`algorithm_vqe_report_v1`（`generate_report()`）。

---

## 5. 在管线中的位置

```text
config → SCF → pre_quantum (QubitHamiltonian)
      → variational plugin (algorithm=vqe, ansatz=hea)
      → VQE.build().run(...)
      → out["energy_after_variational"], algorithm_report, repro
      → （可选）excited / Pauli protocol / mitigation
```

编排：`orchestration` → `quantum.variational_plugins`。

---

## 6. 参数详表

### 6.1 YAML

```yaml
schema_version: "2"
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  vqe:
    depth: 1                          # D ≥ 1；参数数 = 2*n_qubits*depth
    maxiter: 200                      # SciPy maxiter
    optimizer_method: COBYLA          # COBYLA | L-BFGS-B | Nelder-Mead
    initial_parameters_strategy: random_uniform  # 或 zeros
backend:
  name: statevector_sim
  provider: statevector
  shots_per_circuit: 2048             # 精确路径可忽略；shots 路径会用到
```

最小可运行：`configs/example_h2.yaml`（H₂ / STO-3G / CAS(2,2) / JW / HEA depth 1）。

| 字段路径 | 类型 | 默认 | 作用 |
|----------|------|------|------|
| `quantum.algorithm` | str | `vqe` | 选用 VQE 插件 |
| `quantum.variational.ansatz` | str | `hea` | HEA 流形 |
| `quantum.vqe.depth` | int≥1 | `1` | HEA 层数 $D$ |
| `quantum.vqe.maxiter` | int≥1 | `200` | 经典迭代上限 |
| `quantum.vqe.optimizer_method` | enum | `COBYLA` | SciPy 方法 |
| `quantum.vqe.initial_parameters_strategy` | enum | `random_uniform` | 初值策略 |
| `backend.provider` | str | — | `statevector` / `qiskit` / … |
| `random_seed`（实验顶层） | int | — | 影响随机初值 |

### 6.2 Python 类 API

```python
VQE(
    hamiltonian,                 # QubitHamiltonian
    depth=1,
    executor=None,               # 默认 StatevectorHeaExecutor
    objective_expression=None,   # 覆盖默认 ExpectationValue
    auxiliary_expressions=None,  # 额外可观测量
    gradient_expression=None,
    optimizer_method="COBYLA",
)
VQE.build(protocol_objective=None, protocol_gradient=None)
VQE.run(
    maxiter=200,
    initial_parameters=None,
    seed=0,
    executor=None,
    record_energy_trace=False,   # True 时 meta["energy_trace"] 记录每次能量
)
```

注册表：

```python
from qchem_stack.quantum.ansatz_registry import ANSATZ_REGISTRY
ANSATZ_REGISTRY["hea"].implementation
# 'qchem_stack.quantum.algorithms.vqe.VQE'
ANSATZ_REGISTRY["hea"].capabilities
# {'supports_gradient': True, 'supports_auxiliary': True}
```

---

## 7. 函数调用与端到端示例

### 7.1 推荐：配置驱动

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml")
print(out["energy_after_variational"])
print(out.get("algorithm_report", {}).get("schema") if isinstance(out.get("algorithm_report"), dict) else out.get("algorithm_report"))
assert "repro" in out
```

### 7.2 直接构造（调试 / 二次开发）

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from pathlib import Path

cfg = load_experiment_config("configs/example_h2.yaml")
out = run_pipeline_sync(cfg, cfg_path=Path("configs/example_h2.yaml"))
# 或在已有 QubitHamiltonian 上：
# from qchem_stack.quantum.algorithms.vqe import VQE
# vqe = VQE(qh, depth=cfg.quantum.vqe.depth, optimizer_method=cfg.quantum.vqe.optimizer_method)
# vqe.build()
# result = vqe.run(maxiter=cfg.quantum.vqe.maxiter, seed=cfg.random_seed)
```

### 7.3 验证命令

```bash
python -c "
from qchem_stack.sdk import run_pipeline_from_config
o=run_pipeline_from_config('configs/example_h2.yaml')
e=o.get('energy_after_variational')
assert e is not None and e < 0
print('E=', e, 'n_qubits_hint_ok', 'repro' in o)
"
```

### 7.4 期望输出

- 退出码 `0`  
- `E=` 为负的 Hartree 能量（H₂ STO-3G CAS(2,2) 典型约 $-1.1$ 量级，依随机种子/迭代略有浮动）  
- `repro` 存在  

---

## 8. 调参建议

| 现象 | 尝试 |
|------|------|
| 能量明显高于 FCI/文献 | 增大 `depth`；换 `uccsd`；检查映射与活性空间 |
| 不收敛 / `nfev` 打满 | 增大 `maxiter`；换 `optimizer_method`；固定 `zeros` 初值做对照 |
| 换后端能量跳变 | 先 `statevector` 对齐，再开 shots；见 [Pauli 协议](./pauli-protocol) |
| 要化学激发结构 | 用 [UCCSD](./uccsd) 或 [ADAPT](./adapt-vqe) |

---

## 9. 边界与相关

- HEA **不**保证粒子数；UCCSD/JW 更安全。  
- 深度增大 → 参数与贫瘠高原风险同时上升。  
- 下一篇：[UCCSD](./uccsd) · [ADAPT](./adapt-vqe) · [自定义插件](./custom-plugin)
