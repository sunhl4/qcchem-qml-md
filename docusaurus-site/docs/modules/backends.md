---
title: backends 模块
description: BackendSpec、执行器工厂、providers 表、shots 与 Pauli grouping。
---

# backends 模块

`qchem_stack.backends` 提供与 provider 无关的执行器抽象及采样辅助。本页是总册；各 provider 见分册。

相关选型：[后端与 profile](/guide/backends-and-profiles)。

---

## 1. 文献与问题

| 角色 | 文献 / 背景 |
|------|-------------|
| 变分期望 | Peruzzo et al.; McClean et al. |
| 泡利测量与分组 | Yen / Izmaylov；qubit-wise commuting 分组 |
| 本栈契约 | `HamiltonianExpectationExecutor` |

变分与 Pauli 协议阶段需要统一接口估 $\langle\hat{H}\rangle$，而不把算法绑死在某一模拟器。YAML `backend:` → `BackendSpec` → `executor_from_spec` 即该边界。

---

## 2. 理论思想

$$
E = \sum_k c_k\, \langle P_k \rangle
$$

有限 shots 下，未分组方差近似：

$$
\mathrm{Var}(\hat{E}) \approx \sum_k \frac{c_k^2\bigl(1-\langle P_k\rangle^2\bigr)}{n_k}
$$

对易泡利可合并到同一测量基，降低电路数。`shot_budget` / `recommended_shots_per_circuit` 给出保守 stderr 与推荐 shots。

---

## 3. 本栈：`BackendSpec` 与工厂

### 3.1 运行时 dataclass

`backends/spec.py`：

```python
@dataclass
class BackendSpec:
    name: str
    provider: Literal[
        "statevector", "qiskit", "ionstack", "uqc", "qulacs", "cirq", "braket"
    ] = "statevector"
    shots_per_circuit: int = 1024
    target_energy_stderr: float | None = None
    supports_mid_circuit_measure: bool = False
    native_twoq: str = "CX"
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    ionstack_endpoint: str | None = None
    uqc_token: str | None = None
    uqc_backend_name: str | None = None
    uqc_mode: Literal["real", "mock"] = "real"
    uqc_transpile_opt_level: int = 2
    meta: dict = field(default_factory=dict)
```

注意：YAML 配置默认 `shots_per_circuit: 2048`，与 dataclass 默认 `1024` 不同；以 `backend_spec_from_config` 结果为准。

### 3.2 工厂

`backends/factory.py`：

- `executor_from_spec(spec) -> HamiltonianExpectationExecutor`  
- `register_backend_provider(provider, factory, *, overwrite=False)`  
- Entry point 组：`qchem_stack.backends_executors`  
- 别名：`statevector` / `numpy` / `local`；`ion_stack` → `ionstack`  
- `uqc` 仅在 `qchem_stack_uqc` 可导入时注册  

配置桥：`config/io.py` → `backend_spec_from_config(cfg)`（并入 `compiler.native_twoq`）。

协议：`expectation_hea(...)`、`expectation_state(...)`（`executor_base.py`）。

辅助：`pauli_grouping.py`、`shot_budget.py`、`pauli_shot_sim.py`、`profiles.py`。

---

## 4. Providers 表

| `provider` | 安装 | 分册 |
|------------|------|------|
| `statevector`（`numpy`/`local`） | core | [statevector](./backends/statevector) |
| `qiskit` | `pip install qchem-stack[quantum]` | [qiskit](./backends/qiskit) |
| `uqc` | `pip install -e packages/qchem-stack-uqc` | [uqc](./backends/uqc) |
| `ionstack` | core（注入或 mock） | [other-providers](./backends/other-providers) |
| `qulacs` | optional `qulacs` | [other-providers](./backends/other-providers) |
| `cirq` | optional `cirq` | [other-providers](./backends/other-providers) |
| `braket` | optional `amazon-braket-sdk` | [other-providers](./backends/other-providers) |

权威列表亦见仓库 `docs/backends.md`。

---

## 5. YAML 参数表

```yaml
backend:
  name: statevector_sim
  provider: statevector
  shots_per_circuit: 2048
  target_energy_stderr: null
  qiskit_mode: statevector
  ionstack_endpoint: null
  uqc_token: null
  uqc_backend_name: null
  uqc_mode: real
  uqc_transpile_opt_level: 2
  meta: {}
```

| 字段 | 配置默认 | 作用 |
|------|----------|------|
| `provider` | `statevector` | 工厂键 |
| `shots_per_circuit` | `2048` | 采样路径 |
| `target_energy_stderr` | `null` | 驱动 shot budget |
| `qiskit_mode` | `statevector` | `statevector` \| `estimator` |
| `uqc_*` | 见上 | UQC 云参数 |
| `meta` | `{}` | 如 ionstack `expectation_fn` |

Qiskit 比特串采样另见：`quantum.run_qiskit_shots_pauli_protocol: true`（与 `run_sampled_pauli_protocol` 互斥）。

---

## 6. Python 调用

```python
from qchem_stack.backends import (
    BackendSpec,
    executor_from_spec,
    registered_backend_provider_ids,
    list_backend_profile_ids,
    build_measurement_plan,
    recommended_shots_per_circuit,
)

print(sorted(registered_backend_provider_ids()))
print(list_backend_profile_ids())

spec = BackendSpec(name="demo", provider="statevector")
ex = executor_from_spec(spec)
print(type(ex).__name__)
```

从实验配置：

```python
from qchem_stack.config import load_experiment_config, backend_spec_from_config
from qchem_stack.backends import executor_from_spec as _ex

cfg = load_experiment_config("configs/example_h2.yaml")
spec = backend_spec_from_config(cfg)
print(spec.provider, type(_ex(spec)).__name__)
```

---

## 7. 验证命令

```bash
pytest tests/backends/test_p4_backend_conformance.py \
  tests/backends/test_backend_capability_conformance.py \
  tests/quantum/test_executor_backends.py -q

python -c "from qchem_stack.backends import registered_backend_provider_ids, executor_from_spec, BackendSpec; assert 'statevector' in registered_backend_provider_ids(); print(type(executor_from_spec(BackendSpec(name='sv', provider='statevector'))).__name__)"
```

期望：退出码 `0`；打印执行器类名（如 `StatevectorHeaExecutor`）。

---

## 8. 调参建议

| 目标 | 建议 |
|------|------|
| 本地精确开发 | `provider: statevector` |
| 对齐 Qiskit 生态 | [qiskit](./backends/qiskit)；注意线序 remap |
| 控 stderr | 设 `target_energy_stderr` + grouping |
| 云 / 硬件 | UQC 或注入 ionstack；先 mock |
| 缺依赖 | 工厂失败 → 装对应 extra，或换 provider |

---

## 9. 相关

- 分册：[statevector](./backends/statevector) · [qiskit](./backends/qiskit) · [uqc](./backends/uqc) · [other-providers](./backends/other-providers)  
- [protocols](/modules/protocols) · [mitigation](/modules/mitigation) · [切换后端教程](/tutorial/switch-backend-compare)  
- 仓库：`docs/backends.md`
