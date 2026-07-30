---
title: backends · statevector
description: 精确态矢量执行器：StatevectorHeaExecutor、别名与验证。
---

# backends · statevector

本页是默认 **精确态矢量** 后端手册：本地 NumPy 参考实现，适合算法开发与回归。

总册：[backends](../backends) · 对照：[qiskit](./qiskit)。

---

## 1. 文献与问题

| 角色 | 背景 |
|------|------|
| 态矢量模拟 | Nielsen & Chuang；量子电路经典模拟 |
| VQE 参考能量 | 精确 $\langle\psi|H|\psi\rangle$，无 shot 噪声 |

在算法正确性验证阶段，需要与解析 / FCI / 高 shots 极限可对得上的基准。`statevector` provider 提供该基准，并作为多数示例配置默认值。

---

## 2. 理论思想

给定参数化电路 $U(\boldsymbol{\theta})$ 与初态 $|0\rangle^{\otimes n}$：

$$
|\psi(\boldsymbol{\theta})\rangle = U(\boldsymbol{\theta})|0\rangle^{\otimes n}
$$

$$
E(\boldsymbol{\theta}) = \langle\psi(\boldsymbol{\theta})|\hat{H}|\psi(\boldsymbol{\theta})\rangle
= \sum_k c_k\,\langle\psi|P_k|\psi\rangle
$$

态矢量路径直接用稀疏 / 稠密算符作用计算期望，**不**采样；`shots_per_circuit` 可忽略（配置仍可写，供切换采样后端时复用）。

复杂度大致随 $2^n$ 内存与时间增长；仅适合小 $n$（本栈化学示例多为 CAS 后数比特）。

---

## 3. 本栈实现

| 项 | 说明 |
|----|------|
| 类 | `StatevectorHeaExecutor`（`backends/executor_base.py`） |
| 内核 | `qchem_stack.quantum.statevector`：`hea_state`、`expectation_qubit_operator` |
| 工厂 | `_statevector_factory` — **忽略**多数 spec 字段 |
| Provider id | `statevector`、`numpy`、`local`（同一工厂） |

实现 `HamiltonianExpectationExecutor`：`expectation_hea`、`expectation_state`。

与 Qiskit statevector 模式的差异：无 OpenFermion↔Qiskit 线序 remap；结果以本栈内部比特序为准。

---

## 4. YAML 参数表

```yaml
backend:
  name: statevector_sim
  provider: statevector    # 或 numpy / local
  shots_per_circuit: 2048  # 精确路径可忽略
```

| 字段 | 作用 |
|------|------|
| `provider` | `statevector` \| `numpy` \| `local` |
| `name` | 逻辑名（日志 / repro） |
| `shots_per_circuit` | 切到采样后端时才有意义 |

最小示例：`configs/example_h2.yaml`。

---

## 5. Python 调用

```python
from qchem_stack.backends import BackendSpec, executor_from_spec, registered_backend_provider_ids

assert "statevector" in registered_backend_provider_ids()
assert "numpy" in registered_backend_provider_ids()

ex = executor_from_spec(BackendSpec(name="sv", provider="statevector"))
print(type(ex).__name__)  # StatevectorHeaExecutor

# 与 VQE 联用时通常由编排注入；亦可手动：
# energy = ex.expectation_hea(hamiltonian, angles, depth=...)
```

---

## 6. 验证命令

```bash
pytest tests/quantum/test_quantum_runtime.py \
  tests/backends/test_backend_output_contract.py -k statevector -q

python -c "from qchem_stack.backends import registered_backend_provider_ids; assert 'statevector' in registered_backend_provider_ids(); print('ok')"
```

期望打印 `ok`。

端到端：

```bash
python -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print(o.get('energy_after_variational'))"
```

---

## 7. 调参建议

| 场景 | 建议 |
|------|------|
| 日常开发 | 保持 `statevector`；先收敛算法再换硬件 |
| 比特数增大 | 内存爆炸 → 换 `qulacs` / 采样路径，或缩小 CAS |
| 与 Qiskit 对拍 | 同一 `qh` 指纹下比能量；注意线序（见 [qiskit](./qiskit)） |
| 噪声研究 | 不要用本 provider；改 shots / 真机 / 噪声模型 |

---

## 8. 相关

- [backends 总册](../backends) · [qiskit](./qiskit) · [other-providers](./other-providers)  
- 算法：[VQE / HEA](/modules/quantum/algorithms/vqe-hea)  
- 选型：[后端与 profile](/guide/backends-and-profiles)
