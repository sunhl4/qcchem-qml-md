---
title: backends · Qiskit
description: Qiskit 2.x 执行器、线序约定、estimator 模式与 Pauli shots 协议。
---

# backends · Qiskit

本页覆盖 `provider: qiskit`：态矢量 / Estimator 期望，以及可选的 Qiskit Pauli 比特串采样路径。

总册：[backends](../backends) · 设备比特串文档：仓库 `docs/技术文档_设备比特串与Qiskit采样路径.md`。

---

## 1. 文献与问题

| 角色 | 文献 / 软件 |
|------|-------------|
| Qiskit | IBM Qiskit 2.x；Primitives（Estimator） |
| 硬件高效 VQE | Kandala et al., Nature **549**, 242 (2017) |

需要与 Qiskit 生态（Aer、Primitives、硬件）互通时，本 provider 把 OpenFermion 哈密顿量与 HEA 电路接到 Qiskit 对象，并处理 **比特线序** 差异。

---

## 2. 理论思想

期望估计仍是

$$
E = \sum_k c_k\,\langle P_k\rangle
$$

在 Qiskit 中可走：

1. **Statevector**：精确（或模拟器态矢量）；  
2. **Estimator** primitive：抽象期望 API，便于接噪声 / 硬件；  
3. **Shots + counts**：对 Pauli 组测比特串，再经典后处理。

关键约定（本栈）：OpenFermion 轴 $q$ 映射到 Qiskit 线

$$
\mathrm{wire} = n_{\mathrm{qubits}} - 1 - q
$$

（LSB = 本栈 $q=0$）。对拍能量时必须使用同一 remap。

---

## 3. 本栈实现

`backends/qiskit_executor.py`：

| 类 | 何时 |
|----|------|
| `QiskitStatevectorHeaExecutor` | `qiskit_mode=statevector`（默认） |
| `QiskitPrimitivesHeaExecutor` | `qiskit_mode=estimator` |

辅助：`openfermion_to_sparse_pauli_op`、`hea_circuit_qiskit`。

**依赖**：`pip install qchem-stack[quantum]`（qiskit 2.x）。

**Pauli shots 旁路**：`qiskit_pauli_shots.py`；YAML

```yaml
quantum:
  run_qiskit_shots_pauli_protocol: true
```

与 `run_sampled_pauli_protocol` **互斥**。

---

## 4. YAML 参数表

```yaml
backend:
  name: qiskit_aer
  provider: qiskit
  shots_per_circuit: 4096
  qiskit_mode: statevector     # statevector | estimator
  # target_energy_stderr: 0.001
quantum:
  # run_qiskit_shots_pauli_protocol: true   # 可选采样协议
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `provider` | — | 必须 `qiskit` |
| `qiskit_mode` | `statevector` | 执行器分支 |
| `shots_per_circuit` | 配置 `2048` | Estimator / shots 路径 |
| `run_qiskit_shots_pauli_protocol` | `false` | 启用 counts 协议 |

---

## 5. Python 调用

```python
from qchem_stack.backends import BackendSpec, executor_from_spec, registered_backend_provider_ids

assert "qiskit" in registered_backend_provider_ids()

ex_sv = executor_from_spec(
    BackendSpec(name="aer", provider="qiskit", qiskit_mode="statevector")
)
ex_est = executor_from_spec(
    BackendSpec(name="aer", provider="qiskit", qiskit_mode="estimator", shots_per_circuit=2048)
)
print(type(ex_sv).__name__, type(ex_est).__name__)
```

管线：把 `backend.provider` 改为 `qiskit` 后 `run_pipeline_from_config(...)`。

---

## 6. 验证命令

```bash
pytest tests/quantum/test_qiskit_pauli_shots.py \
  tests/quantum/test_executor_backends.py -k qiskit -q

python -c "from qchem_stack.backends import registered_backend_provider_ids; assert 'qiskit' in registered_backend_provider_ids(); print('ok')"
```

若未装 `[quantum]` extra，注册或导入可能失败——先安装依赖。

---

## 7. 调参建议

| 目标 | 建议 |
|------|------|
| 与 statevector 对拍 | `qiskit_mode: statevector`；比对同一指纹 `qh` |
| 贴近硬件 API | `estimator` + 提高 shots |
| 比特串调试 | 开 `run_qiskit_shots_pauli_protocol`；读设备比特串文档 |
| 方差过大 | 提高 `shots_per_circuit` 或设 `target_energy_stderr` |
| 线序诡异 | 确认 OF→Qiskit remap；勿混用未 remap 的手工电路 |

---

## 8. 相关

- [statevector](./statevector) · [uqc](./uqc) · [backends 总册](../backends)  
- [Pauli 协议深读](/modules/quantum/algorithms/pauli-protocol) · [mitigation](/modules/mitigation)  
- 仓库：`docs/技术文档_设备比特串与Qiskit采样路径.md`
