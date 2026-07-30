---
title: SA-VQE（态平均变分）
description: 态平均最小模型完整手册：重叠惩罚目标、HEA、YAML/API。
---

# SA-VQE（State-Averaged VQE）

本页详述本栈 **最小 SA-VQE**：HEA 上的「能量 + 参考态重叠惩罚」。用于多态烟雾与契约，**不是**完整轨道优化 SA-CASSCF / 文献级多态平均。

实现：`qchem_stack.quantum.algorithms.sa_vqe.SAVQE`。算法 ID：`sa_vqe`。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 经典态平均 CASSCF | Roos et al., Chem. Phys. **48**, 157 (1980) 等 |
| 量子 SA / 多态 VQE | Yalouz et al., [Quantum Sci. Technol. **6**, 024004 (2021)](https://doi.org/10.1088/2058-9565/abd334) 及 SSVQE 系列 |

---

## 2. 要解决什么问题

锥形交叉、光化学需要同时描述若干电子态。经典 SA 混合密度进轨道优化；量子侧常见：多态平均能量，或惩罚避免塌到同一态。

本栈取工程最小模型：固定参考 HEA 态，惩罚重叠，推动优化器离开参考流形但仍保持低能量。

---

## 3. 理论与数学

$$
L(\boldsymbol{\theta})
= E(\boldsymbol{\theta})
+ w\,\bigl|\langle\psi_{\mathrm{ref}}|\psi(\boldsymbol{\theta})\rangle\bigr|^2
$$

其中 $|\psi\rangle=\mathrm{HEA}(\boldsymbol{\theta})$，$|\psi_{\mathrm{ref}}\rangle=\mathrm{HEA}(\boldsymbol{\theta}_{\mathrm{ref}})$。

流程：

1. 采样或给定 `reference_angles` → $|\psi_{\mathrm{ref}}\rangle$  
2. COBYLA 最小化 $L$  
3. 返回 `SAVQEResult(energy, angles, nfev, meta)`；报告 schema `algorithm_sa_vqe_report_v1`

与 [VQD](./vqd) 区别：VQD 顺序求激发序；SA-VQE 此处是 **单参考重叠惩罚**，非完整态平均哈密顿。

---

## 4. 参数详表

```yaml
quantum:
  algorithm: sa_vqe
  variational:
    ansatz: hea          # 算法选择忽略 ansatz；电路仍为 HEA
  vqe:
    depth: 1
    maxiter: 200
```

| 来源 | 字段 | 默认 | 说明 |
|------|------|------|------|
| YAML | `vqe.depth` | `1` | HEA 深度 |
| YAML | `vqe.maxiter` | `200` | COBYLA 预算 |
| 类构造 | `penalty_weight` | `2.0` | **当前无 YAML 暴露** |
| `run` | `seed`, `reference_angles` | 随机小角 | 参考未设时均匀 $[-0.2,0.2]$ |

代表：`configs/example_h2_sa_vqe.yaml`。  
管线：`variational_plugins.builtins.run_sa_vqe_branch`。

---

## 5. 函数调用与验证

```python
from qchem_stack.quantum.algorithms.sa_vqe import SAVQE
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_sa_vqe.yaml")
print(out.get("energy_after_variational"), "algorithm_report" in out)

# 直接：SAVQE(qh, depth=1, penalty_weight=2.0).run(maxiter=200, seed=0)
```

### 验证命令

```bash
python3 -c "from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids; assert 'sa_vqe' in list_registered_algorithm_ids(); print('ok')"
```

### 期望输出

- `ok`；管线含 `energy_after_variational` 与 `repro`  

---

## 6. 调参与边界

| 现象 | 处理 |
|------|------|
| 仍塌到参考 | 增大 `penalty_weight`（需改代码/构造）；或换 [VQD](./vqd) |
| 要真正 SA-CASSCF | 用经典 [AVAS/CASSCF](/modules/chem/avas-casscf) + 量子基态，勿指望本最小模型 |
| 仅 HEA | 无 UCCSD 流形 SA |

---

## 7. 相关

- [VQE/HEA](./vqe-hea) · [VQD](./vqd) · [QSE](./qse)
