---
title: tensornet 模块
description: 稠密期望参考、cutensornet stub 与 quantum.tensornet YAML。
---

# tensornet 模块

`qchem_stack.tensornet` 提供小规模稠密期望值参考与 cuTensorNet **协议 stub**（非默认生产路径）。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| Dense reference | 显式 $2^n$ 态向量/算符，对照 Pauli 协议期望 |
| cuTensorNet stub | 收缩引擎占位；可探测 cupy / cuquantum，默认 stub |
| 闭包元数据 | `integrations/tensornet_closure.tensornet_closure_strategy` |
| 选型语境 | 大系统张量网仍属研究/对照，非主 VQE 路径 |

**不要**把 stub 当作已交付的 GPU 张量网运行时。

---

## 2. 理论

对 $n$ 量子比特纯态 $|\psi\rangle$ 与泡利串（或 qubit 算符）$P$：

$$
\langle P \rangle = \langle \psi | P | \psi \rangle
$$

稠密路径内存 $\propto 2^n$，推荐 $n \lt 16$（`max_qubits_recommended: 16`）。  
张量网络将同一期望分解为可收缩网络，降低大 $n$ 峰值内存；本包 GPU 路径当前为 stub。

---

## 3. 实现

### Dense reference

| 符号 | 路径 |
|------|------|
| `expectation_qubit_operator_dense` | `tensornet/dense_expectation_reference.py` |
| `dense_expectation_api_descriptor` | 同上 — schema `DENSE_EXPECTATION_REFERENCE_V1` |

### cuTensorNet stub

| 符号 | 路径 |
|------|------|
| `run_cutensornet_expectation_stub(n_qubits, *, requested_backend="stub")` | `tensornet/cutensornet_protocol_stub.py` |
| Schema | `CUTENSORTNET_PROTOCOL_STUB_V1` |
| Backends | `stub`、`opt_einsum`、`cupy_if_available`、`cuquantum_if_available` |

解析器：`tensornet_expectation_stub_enabled`、`resolve_tensornet_contraction_engine`（`config/quantum_resolvers.py`）。

管线：protocol finalize sidecar 可写 `out["tensornet_protocol_stub"]`。  
Parity：`parity_integrations.tensornet_closure_reference` 附着策略元数据。

---

## 4. YAML（`quantum.tensornet`）

```yaml
schema_version: "2"
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  tensornet:
    expectation_stub: false
    contraction_engine: stub
    # stub | opt_einsum | cupy_if_available | cuquantum_if_available
parity_integrations:
  tensornet_closure_reference: false
```

| 键 | 类型 / 默认 | 含义 |
|----|-------------|------|
| `expectation_stub` | `bool` / `False` | 是否跑 stub 期望路径 |
| `contraction_engine` | 枚举 / `stub` | 收缩后端请求 |

规格类：`QuantumTensornetSpec`（`config/quantum_specs.py`）。

---

## 5. Python

```python
from qchem_stack.tensornet import (
    expectation_qubit_operator_dense,
    dense_expectation_api_descriptor,
    run_cutensornet_expectation_stub,
)

print(dense_expectation_api_descriptor())
stub = run_cutensornet_expectation_stub(4, requested_backend="stub")
print(stub.get("schema") if isinstance(stub, dict) else type(stub).__name__)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.tensornet import dense_expectation_api_descriptor; d=dense_expectation_api_descriptor(); print(d if isinstance(d, str) else sorted(d.keys())[:5] if isinstance(d, dict) else type(d).__name__)"
```

期望：含 `schema` / `function` 等键或描述片段。

```bash
python3 -c "from qchem_stack.tensornet import run_cutensornet_expectation_stub; r=run_cutensornet_expectation_stub(2); print(type(r).__name__, list(r)[:4] if isinstance(r, dict) else r)"
```

期望：退出码 `0`；stub 字典或可打印结果。

---

## 7. 调优建议

- 对照实验：$n \lt 16$ 用 dense；更大系统勿开 dense。  
- 生产默认 `expectation_stub: false`。  
- 有 cupy/cuquantum 时可试 `cupy_if_available` / `cuquantum_if_available`，仍按 stub 语义解读结果。  
- 对标开关与主能量路径隔离，避免污染基线。

---

## 8. 相关

- [protocols](./protocols) · [backends](./backends) · [integrations](./integrations) · [contracts](./contracts)  
- [Pauli 深读](./quantum/algorithms/pauli-protocol)
