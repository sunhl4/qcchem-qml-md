---
title: backends · UQC
description: UQC 云执行器插件：安装、BackendSpec 字段、mock/real 与验证。
---

# backends · UQC

本页覆盖可选云后端 `provider: uqc`（包 `qchem-stack-uqc`）。

总册：[backends](../backends) · 包 README：`packages/qchem-stack-uqc/README.md`。

---

## 1. 文献与问题

| 角色 | 背景 |
|------|------|
| 云量子访问 | 供应商 API + 转译 +（可选）缓解 |
| 本栈边界 | 核心库不强制依赖云 SDK；UQC 为可选插件 |

本地 `statevector` 无法覆盖真实队列、转译与设备噪声。UQC 插件把同一 `BackendSpec` / `HamiltonianExpectationExecutor` 接到云后端，并用 `mock` 模式保证无令牌时的集成测试。

---

## 2. 理论思想

云路径仍估

$$
E(\boldsymbol{\theta})=\sum_k c_k\,\langle P_k\rangle_{\boldsymbol{\theta}}
$$

但电路需 **transpile** 到设备原生门集，测量受有限 shots 与噪声影响。可选缓解（ZNE 等）在 UQC / mitigation 模块侧挂接，不改变算法层目标函数形式。

`uqc_mode: mock` 用确定性 / 注入行为代替真实提交，便于 CI。

---

## 3. 本栈实现

| 项 | 说明 |
|----|------|
| 执行器 | `UQCCloudHeaExecutor`（包内 `qchem_stack_uqc.uqc_executor`） |
| Shim | `backends/uqc_executor.py` |
| 注册 | `qchem_stack_uqc` **可导入时** 才注册 `uqc` |
| 相关 | `uqc_pauli_measurement.py`、`uqc_transpiler.py`、`uqc_mitigation.py`、`uqc_env.py` |

**安装**：

```bash
pip install -e packages/qchem-stack-uqc
```

---

## 4. YAML 参数表

```yaml
backend:
  name: uqc_device
  provider: uqc
  shots_per_circuit: 4096
  uqc_token: null              # 或环境注入；勿提交真实令牌到仓库
  uqc_backend_name: null
  uqc_mode: mock               # real | mock
  uqc_transpile_opt_level: 2   # 0–3
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `uqc_token` | `null` | API 令牌（`real` 需要） |
| `uqc_backend_name` | `null` | 目标后端名 |
| `uqc_mode` | `real` | 开发请用 `mock` |
| `uqc_transpile_opt_level` | `2` | 转译优化级别 0–3 |
| `shots_per_circuit` | 配置 `2048` | 采样数 |

---

## 5. Python 调用

```python
from qchem_stack.backends import BackendSpec, executor_from_spec, registered_backend_provider_ids

assert "uqc" in registered_backend_provider_ids()  # 需已安装插件

ex = executor_from_spec(
    BackendSpec(
        name="uqc_mock",
        provider="uqc",
        uqc_mode="mock",
        uqc_transpile_opt_level=2,
        shots_per_circuit=1024,
    )
)
print(type(ex).__name__)
```

令牌优先经环境 / secret 注入，避免写进 YAML 仓库副本。

---

## 6. 验证命令

```bash
pytest tests/quantum/test_uqc_grouped_pauli.py \
  tests/quantum/test_uqc_mock_md_ml_integration.py -q

python -c "from qchem_stack.backends import registered_backend_provider_ids; assert 'uqc' in registered_backend_provider_ids(); print('ok')"
```

若断言失败：先 `pip install -e packages/qchem-stack-uqc` 并确认导入路径。

---

## 7. 调参建议

| 场景 | 建议 |
|------|------|
| CI / 本地 | `uqc_mode: mock` |
| 真机试跑 | `real` + 有效 `uqc_token` / `uqc_backend_name`；小 shots 冒烟 |
| 深度过大 | 提高 `uqc_transpile_opt_level`；或减小 ansatz depth |
| 噪声 | 接 [mitigation](/modules/mitigation)；先在 mock 验证接线 |
| 未注册 | 检查可选包是否安装 |

---

## 8. 相关

- [backends 总册](../backends) · [qiskit](./qiskit) · [other-providers](./other-providers)  
- [mitigation](/modules/mitigation) · [Pauli 协议](/modules/quantum/algorithms/pauli-protocol)  
- `packages/qchem-stack-uqc/README.md`
