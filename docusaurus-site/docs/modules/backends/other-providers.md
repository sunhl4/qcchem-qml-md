---
title: backends · 其他 providers
description: ionstack、qulacs、cirq、braket 与 entry point 扩展。
---

# backends · 其他 providers

本页汇总非默认模拟器 / 云注入类 provider，以及如何用 entry point 扩展工厂。

总册：[backends](../backends) · 仓库：`docs/backends.md`。

---

## 1. 文献与问题

| Provider | 典型用途 |
|----------|----------|
| IonStack | 注入自定义 `expectation_fn` 或 mock 端点 |
| Qulacs | 轻量 C++ 态矢量加速 |
| Cirq | Google 生态电路 |
| Braket | Amazon Braket SDK 路径 |

算法层只依赖 `HamiltonianExpectationExecutor`。只要工厂能从 `BackendSpec` 构造执行器，即可替换模拟器而不改 VQE / 协议代码。

---

## 2. 理论思想

所有 provider 最终仍计算（或估计）

$$
E = \sum_k c_k\,\langle P_k\rangle
$$

差异在于：电路表示、比特线序、是否采样、以及依赖是否可选。扩展时保持 **同一 `qh` 指纹** 下与 `statevector` 对拍，再接入外部系统。

---

## 3. 本栈实现一览

| `provider` | 执行器 | 路径 | 依赖 / 备注 |
|------------|--------|------|-------------|
| `ionstack` | `IonStackHeaExecutor` | `ionstack_executor.py` | 注入 `meta['expectation_fn']`，或 `ionstack_endpoint: mock` + `mock_energy` |
| `qulacs` | `QulacsHeaExecutor` | `qulacs_executor.py` | `pip install qulacs`；OF→Qulacs 线序 remap |
| `cirq` | `CirqHeaExecutor` | `cirq_executor.py` | optional `cirq` |
| `braket` | `BraketHeaExecutor` | `braket_executor.py` | optional `amazon-braket-sdk` |

别名：`ion_stack` → `ionstack`。

**非 provider**：`backends/pytket_bridge.py` 提供资源行等桥接，**不是**注册表中的执行 provider。

### Entry points

组名：`qchem_stack.backends_executors`  

- 可为工厂可调用对象，或带 `from_backend_spec(spec)` 的类  
- 进程内：`register_backend_provider(provider, factory, overwrite=False)`

---

## 4. YAML 参数表

### ionstack

```yaml
backend:
  name: ion_mock
  provider: ionstack
  ionstack_endpoint: mock
  meta:
    mock_energy: -1.0
  # 或在 Python 侧注入 meta.expectation_fn
```

### qulacs / cirq / braket

```yaml
backend:
  name: qulacs_local
  provider: qulacs          # cirq | braket
  shots_per_circuit: 2048
```

| 字段 | 适用 | 作用 |
|------|------|------|
| `ionstack_endpoint` | ionstack | `mock` 等 |
| `meta.mock_energy` | ionstack mock | 固定能量烟雾 |
| `meta.expectation_fn` | ionstack | 自定义可调用（Python） |
| `provider` | 全部 | 工厂键 |

---

## 5. Python 调用

```python
from qchem_stack.backends import (
    BackendSpec,
    executor_from_spec,
    registered_backend_provider_ids,
    register_backend_provider,
)

ids = registered_backend_provider_ids()
assert {"qulacs", "cirq", "braket", "ionstack"} <= set(ids)

ex = executor_from_spec(BackendSpec(name="ql", provider="qulacs"))
print(type(ex).__name__)

# 自定义 provider
# register_backend_provider("my_backend", my_factory)
```

IonStack 注入示例：

```python
spec = BackendSpec(
    name="ion",
    provider="ionstack",
    meta={"expectation_fn": lambda *a, **k: -1.136},
)
```

---

## 6. 验证命令

```bash
pytest tests/quantum/test_qulacs_backend_conformance.py \
  tests/backends/test_p4_backend_conformance.py -q

python -c "from qchem_stack.backends import registered_backend_provider_ids; s=set(registered_backend_provider_ids()); assert {'qulacs','cirq','braket'}<=s; print('ok')"
```

可选依赖缺失时，个别 conformance 可能 skip——以测试输出为准。

---

## 7. 调参建议

| Provider | 建议 |
|----------|------|
| ionstack | 先 `mock`；再注入真实 `expectation_fn` |
| qulacs | 大一点的 $n$ 可先于裸 NumPy；对拍 statevector |
| cirq / braket | 装 optional；夜间 CI 有 conformance |
| 插件 | entry point 名勿与内置冲突；`overwrite=True` 仅调试 |

---

## 8. 相关

- [backends 总册](../backends) · [statevector](./statevector) · [qiskit](./qiskit) · [uqc](./uqc)  
- [切换后端教程](/tutorial/switch-backend-compare)  
- 仓库：`docs/backends.md`
