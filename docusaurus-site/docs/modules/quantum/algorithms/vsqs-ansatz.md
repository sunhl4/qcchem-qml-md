---
title: VSQS ansatz
description: 变分调度量子模拟完整手册：H(τ) 插值、Trotter、YAML 字段。
---

# VSQS（Variational Scheduled Quantum Simulation）

按调度参数插值 $H_{\mathrm{init}}\to H_{\mathrm{final}}$，Trotter 层变分优化末态能量。论文锚点：arXiv:2003.09913（源码注释）。

实现：`qchem_stack.quantum.algorithms.vsqs_vqe.VSQSVQE`。

---

## 1. 理论思想

绝热/调度直觉：缓慢把易制备参考哈密顿变到目标分子 $H$。VSQS 用可学习调度 $(a_i,b_i)$ 控制各区间上对 $H_{\mathrm{init}}$ / $H_{\mathrm{final}}$ 的 Trotter 指数，使末态 $\langle H_{\mathrm{final}}\rangle$ 最低。

---

## 2. 数学实现（本栈）

1. `build_vsqs_h_init`：由 `hamiltonian.meta["spatial_mo_h1"]` / `spatial_mo_h2` 构造 HF 派生初哈密顿  
2. $H_{\mathrm{final}}$ = 目标量子比特 $H$  
3. 区间数 `intervals`（≥2）→ 参数个数 $(intervals-1)\times 2$  
4. 初值：`vsqs_initial_angles` 线性 ramp + 小噪声  
5. Trotter 阶 `1|2`；COBYLA 优化调度角  

拒 `hard_core_boson`；需 `fermion_space` 与空间积分 meta。

---

## 3. 参数详表

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: vsqs
    vsqs_intervals: 2      # ≥2
    vsqs_time: 1.0
    vsqs_trotter_order: 1  # 1 | 2
  vqe:
    maxiter: 200
```

| 字段 | 默认 | 解析 |
|------|------|------|
| `vsqs_intervals` | `2` | `resolve_vsqs_intervals` |
| `vsqs_time` | `1.0` | `resolve_vsqs_time` |
| `vsqs_trotter_order` | `1` | `resolve_vsqs_trotter_order` |

代表：`configs/example_h2_vsqs.yaml`。报告：`vsqs_algorithm_report_v1`。

---

## 4. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config
out = run_pipeline_from_config("configs/example_h2_vsqs.yaml")
print(out.get("energy_after_variational"))
```

```bash
python3 -c "from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids; assert 'vsqs' in list_registered_ansatz_ids(); print('ok')"
```

---

## 5. 相关

- [VQE](./vqe-hea) · [VQS 轨迹侧车](./vqs) · [dual-ingress / 空间积分](/modules/chem/dual-ingress)
