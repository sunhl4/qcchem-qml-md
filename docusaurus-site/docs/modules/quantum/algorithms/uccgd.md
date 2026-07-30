---
title: UCCGD
description: 广义双激发幺正耦合簇完整手册：生成元、映射约束、YAML/API。
---

# UCCGD（Unitary Coupled Cluster Generalized Doubles）

本页说明闭壳层 **广义 doubles** 变分 ansatz：相对 UCCSD 扩大双激发索引范围，仍走稠密乘积指数路径。

实现：`qchem_stack.quantum.algorithms.uccgd_vqe.UCCGDVQE`（继承 `UCCSDVQE`）。生成元：`build_spin_uccgd_fermion_generators`。

---

## 1. 文献

广义 / 成对 UCC 变体见 Lee et al. k-UpCCGSD（[JCTC **15**, 311 (2019)](https://doi.org/10.1021/acs.jctc.8b01004)）及后续 generalized excitation 工作。本栈 `uccgd` 为 **自旋轨道广义 doubles + singles** 的开放实现切片。

---

## 2. 理论思想

标准 UCCSD 限制 occupied→virtual。**广义 doubles** 放宽双激发指标（实现中：singles $a^\dagger i$ 加上更广的 $a^\dagger b^\dagger ji$ 组合），提高表达力，参数数与门深通常大于 UCCSD。

态仍为

$$
|\psi\rangle
= \Biggl(\prod_k e^{\theta_k(T_k-T_k^\dagger)}\Biggr)|\mathrm{HF}\rangle
$$

---

## 3. 数学实现（本栈）

1. 要求 `fermion_space` 与 **方阵编码**：$n_{\mathrm{so}}=n_{\mathrm{qubits}}$（JW/BK）。  
2. **拒** `symmetry_conserving_bravyi_kitaev`。  
3. `antihermitian_cluster_matrices` → 乘积 `expm` 传播（同 UCCSD）。  
4. COBYLA 最小化 $\langle H\rangle$；报告 `uccgd_algorithm_report_v1`。

池侧对照：ADAPT 可用 `fermionic_generalized_doubles`（[算符池](./operator-pools)）。

---

## 4. 参数

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: uccgd
  vqe:
    maxiter: 80
    optimizer_method: COBYLA
active_space:
  fermion_qubit_mapping: jordan_wigner   # 或 bravyi_kitaev
```

| 配置 |
|------|
| `configs/example_h2_uccgd.yaml` |
| `configs/example_h2_uccgd_pauli_protocol.yaml` |

优化器字段同 [VQE/HEA](./vqe-hea)。无额外 UCCGD 专用 YAML 块；参数个数由活性空间生成元数决定。

---

## 5. 函数调用与验证

```python
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
from qchem_stack.sdk import run_pipeline_from_config

assert "uccgd" in list_registered_ansatz_ids()
out = run_pipeline_from_config("configs/example_h2_uccgd.yaml")
print(out.get("energy_after_variational"))
```

### 验证命令

```bash
python3 -c "from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids; assert 'uccgd' in list_registered_ansatz_ids(); print('ok')"
```

---

## 6. 边界与相关

- 比 UCCSD 更贵；先 [UCCSD](./uccsd) 跑通再换。  
- 成对压缩见 [pUCCD / QCC](./qcc-paired)。  
- [映射](/modules/chem/mappings)
