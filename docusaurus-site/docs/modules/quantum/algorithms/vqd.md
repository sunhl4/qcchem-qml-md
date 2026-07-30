---
title: VQD（变分量子亏损）
description: Higgott VQD 完整手册：惩罚目标、重叠模式、YAML 全字段与调用。
---

# VQD（Variational Quantum Deflation）

激发态侧车完整说明。产品对照：仓库 `docs/技术文档_VQD紧缩激发与跨栈对照.md`。  
实现：`qchem_stack.quantum.algorithms.excited_vqd.VQD` + `run_vqd_deflation`。

---

## 1. 文献

O. Higgott, D. Wang, S. Brierley, *Variational Quantum Computation of Excited States*, [Quantum **3**, 156 (2019)](https://doi.org/10.22331/q-2019-07-01-156)。

---

## 2. 理论思想

基态 VQE 找到 $|\psi_0\rangle$ 后，再次最小化 $\langle H\rangle$ 会塌回基态。  
**VQD** 对第 $k$ 个态在目标中加入与已求态的重叠惩罚，顺序求出激发能级。

本栈在 **变分基态完成之后** 由 `orchestration.excited_stages` 调度（`after_variational: true`），结果写入 `out["vqd"]` 等侧车键，不替换主路径基态语义。

---

## 3. 数学实现

### 3.1 目标函数

$$
E_k(\boldsymbol{\theta})
= \langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle
+ \sum_{i<k}\beta_i\,
\bigl|\langle\psi_i|\psi(\boldsymbol{\theta})\rangle\bigr|^{p}
$$

- $\beta_i$：`penalty_weight`（统一）或 `penalty_weights`（逐级）  
- $p$：`overlap_exponent`（实现中有下限裁剪）  
- $|\psi(\boldsymbol{\theta})\rangle$：默认 HEA；可注入 `prepare_state`（如 UCCSD.prepare_state）

### 3.2 重叠模式 `overlap_mode`

| 值 | 含义 |
|----|------|
| `statevector_overlap` | 精确态矢量重叠（默认、调试最稳） |
| `tangelo_circuit_analogy` | 电路类比元数据路径 |
| `deflation_circuit` | deflation 电路风格 |

### 3.3 优化模式 `optimizer_mode`

| 值 | 含义 |
|----|------|
| `collapsed` | 单一标量目标（默认） |
| `three_computable` | 目标/重叠/权重三通道统计报告 |

### 3.4 初值策略 `init_strategy`

`legacy` · `reuse_ground_perturb` · `previous_layer_perturb` · `random_uniform`，噪声尺度 `init_noise_scale`。

### 3.5 流程（概念）

```text
level 0: 标准变分（或复用已有基态）
for k = 1 .. n_states-1:
    构造带惩罚的目标
    经典优化 → |ψ_k⟩, E_k
    可选：重叠预警 max_overlap_warn
```

---

## 4. 参数详表（YAML）

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: uccsd          # 或 hea
  excited:
    vqd:
      after_variational: true
      n_states: 2
      penalty_weight: 5.0
      penalty_weights: null
      overlap_exponent: 1.0
      cobyla_maxiter: 150
      optimizer_method: COBYLA
      init_strategy: legacy
      init_noise_scale: 0.15
      max_overlap_warn: 0.05
      overlap_mode: statevector_overlap
      optimizer_mode: collapsed
      shots_objective: 0
      shots_overlap: 0
      shots_weight: 0
```

| 字段 | 含义 |
|------|------|
| `n_states` | 含基态在内的态数（≥2） |
| `penalty_weight` / `penalty_weights` | $\beta$；后者长度应为 `n_states-1` |
| `cobyla_maxiter` | 每级优化预算 |
| `shots_*` | 非零时走采样预算（精确为 0） |

代表：`configs/example_h2_vqd_uccsd.yaml`、`example_h2_vqd_deflation_circuit.yaml`。

### Python 构造要点

```python
VQD(
    hamiltonian,
    n_states=2,
    depth=1,
    penalty_weight=5.0,
    penalty_weights=None,
    overlap_exponent=1.0,
    cobyla_maxiter=150,
    optimizer_method="COBYLA",
    prepare_state=None,          # 例如 uccsd.prepare_state
    n_var_parameters=None,        # prepare_state 时必填
    init_strategy="legacy",
    overlap_mode="statevector_overlap",
    optimizer_mode="collapsed",
)
```

---

## 5. 函数调用与验证

```python
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids
from qchem_stack.sdk import run_pipeline_from_config

assert "vqd" in list_registered_excited_ids()
out = run_pipeline_from_config("configs/example_h2_vqd_uccsd.yaml")
vqd = out.get("vqd")
print(type(vqd).__name__, list(vqd)[:15] if isinstance(vqd, dict) else vqd)
print("excited_resource_summary" in out)
```

### 验证命令

```bash
python -c "from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids; assert 'vqd' in list_registered_excited_ids(); print('ok')"
```

### 期望输出

- `ok`  
- 管线含 `vqd` 结构；常有 `excited_resource_summary`  

---

## 6. 调参

| 现象 | 处理 |
|------|------|
| 激发态塌回基态 | 增大 $\beta$；换 `init_strategy`；确认 `after_variational` |
| 优化极难 | 减小 $\beta$；增大 `cobyla_maxiter`；先 `statevector_overlap` |
| 重叠预警频繁 | 调 `max_overlap_warn` 或检查流形是否表达激发 |

---

## 7. 相关

- [QSE](./qse)（子空间一次对角化）· [SCEOM](./sceom)  
- [UCCSD](./uccsd) · [选型](/guide/excited-states-vqd-qse-sceom)
