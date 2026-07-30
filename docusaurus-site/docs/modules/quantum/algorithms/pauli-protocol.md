---
title: Pauli 平均协议深读
description: 分组测量完整手册：五阶段、对易分组、shots 模式、YAML/API 与缓解挂载。
---

# Pauli 平均协议深读

本页是测量层完整手册：为何分组、辛几何对易、五阶段协议、`quantum.pauli` 全字段、与后端/缓解的衔接。

实现：`qchem_stack.protocols.protocol.PauliAveragingProtocol`；分组：`backends.pauli_grouping`；工程说明：仓库 `docs/pauli_averaging_protocol_five_stage_engineering.md`。

选型：[Pauli 协议与 shots](/guide/pauli-protocol-and-shots)。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| VQE 测量 | McClean et al., [NJP **18**, 023023 (2016)](https://doi.org/10.1088/1367-2630/18/2/023023) |
| 对易分组 | Gokhale、Yen 等 Pauli grouping 工作；OpenFermion tensor-product 分组 |
| 本栈工程 | `docs/pauli_averaging_protocol_five_stage_engineering.md` · 设备比特串文档 |

---

## 2. 要解决什么问题

哈密顿量

$$
\hat{H}=\sum_k c_k P_k
$$

若每个 Pauli 单独测，电路次数 ≈ 项数。把可对易的项放进同一组，共用一套测量基变换，可大幅减少电路行数。协议层再统一：编译、发射、直方图、stderr、ZNE/PMSV 挂载。

---

## 3. 理论思想

两 Pauli 串对易当且仅当辛内积为 0（二进制 symplectic 表示）：

$$
\langle(x,z),(x',z')\rangle
= x\cdot z' + z\cdot x' \pmod 2
$$

本栈：

- `tensor_product`：OpenFermion `group_into_tensor_product_basis_sets`（同测量基族）  
- `greedy_commuting`：贪心把项塞进两两对易的集合  

能量估计：

$$
\hat{E}=\sum_k c_k\,\widehat{\langle P_k\rangle}
$$

有限 shots 时附带 `energy_stderr_model`（见 `protocol_counts`）。

---

## 4. 五阶段协议（本栈）

`PauliAveragingProtocol` 阶段（`ProtocolPhase`）：

| 阶段 | 方法 | 内容 |
|------|------|------|
| Instantiate | `instantiate` | 初始化 |
| Build | `build(angles, …)` | 逻辑测量电路 + ansatz 制备 |
| Compile | `compile` | `CompilerPassBundle` |
| Run | `run` / `run_energy_estimation` | 精确 executor **或** 采样 **或** Qiskit shots |
| Evaluate | counts / 能量键 | `protocol_counts`、管线 `energy_pauli_protocol` 等 |

Shot 模式 **互斥**：

| 模式 | 开关 | 语义 |
|------|------|------|
| 精确 | 默认（两采样均为 false） | executor 精确期望 |
| 分组 MC | `run_sampled=true` | statevector 分组蒙特卡洛 |
| Qiskit | `run_qiskit_shots=true` | Aer/设备 `get_counts` |

`run_sampled` ∧ `run_qiskit_shots` → 配置/运行期错误。

可选：`record_histograms`、`pauli_support_max_terms`、classical shadows、ZNE scales、PMSV。

---

## 5. 参数详表

```yaml
quantum:
  pauli:
    use_protocol: true
    grouping: tensor_product       # greedy_commuting
    run_sampled: false
    run_qiskit_shots: false
    record_histograms: false
    support_max_terms: null
backend:
  provider: statevector            # 或 qiskit
  # shots / device 字段见 BackendSpec
mitigation:
  # zne / pmsv 等可与协议挂载（见 mitigation 模块）
```

| 字段 | 含义 |
|------|------|
| `use_protocol` | 是否启用 Pauli 五阶段 |
| `grouping` | `tensor_product` \| `greedy_commuting` |
| `run_sampled` | 分组 MC |
| `run_qiskit_shots` | Qiskit 直方图路径 |
| `record_histograms` | 是否保留直方图 |
| `support_max_terms` | 截断 Pauli 支持（调试） |

代表配置：

| 文件 |
|------|
| `configs/example_h2_uccsd_pauli_protocol.yaml` |
| `configs/example_h2_qiskit_shots.yaml` |
| `configs/example_h2_sampled.yaml` |

解析辅助：`config.quantum_helpers.resolve_pauli_grouping`、`pauli_run_sampled` 等；resolvers 写入 `use_pauli_protocol`、`pauli_grouping`…

### Python 核心对象

```python
from qchem_stack.backends.pauli_grouping import (
    build_measurement_plan,
    greedy_commuting_groups,
    pauli_terms_commute,
)
from qchem_stack.protocols.protocol import PauliAveragingProtocol

# plan = build_measurement_plan(h_op, n_qubits, grouping="tensor_product")
# proto = PauliAveragingProtocol(
#     hamiltonian=h_op,
#     n_qubits=n,
#     backend=backend_spec,
#     measurement_grouping="tensor_product",
#     run_sampled=False,
#     run_qiskit_shots=False,
# )
```

---

## 6. 函数调用与验证

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.sdk import run_pipeline_from_config

cfg = load_experiment_config("configs/example_h2_uccsd_pauli_protocol.yaml")
print(cfg.quantum.pauli.use_protocol, cfg.quantum.pauli.grouping)

out = run_pipeline_from_config("configs/example_h2_uccsd_pauli_protocol.yaml")
print("protocol_counts" in out, "energy_pauli_protocol" in out or "energy_after_variational" in out)
```

### 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
from qchem_stack.backends.pauli_grouping import build_measurement_plan
from openfermion.ops import QubitOperator
c=load_experiment_config('configs/example_h2_uccsd_pauli_protocol.yaml')
assert c.quantum.pauli.use_protocol
h=QubitOperator('X0')+QubitOperator('Z1')
p=build_measurement_plan(h, 2, grouping=c.quantum.pauli.grouping)
print('ok', c.quantum.pauli.grouping, type(p).__name__)
"
```

### 期望输出

- `ok`、grouping 名、`PauliMeasurementPlan`  

---

## 7. 调参

| 目标 | 建议 |
|------|------|
| 先通管线 | `use_protocol=true`，两采样 false |
| 估 shot 噪声 | `run_sampled=true` + 足够 shots |
| 对接 Aer/设备 | `run_qiskit_shots` + Qiskit backend |
| 减电路行 | 试 `greedy_commuting` vs `tensor_product` |
| 作业异步 | 管线 job enqueue + `PauliAveragingProtocol.process_job` |

---

## 8. 相关

- [protocols 模块](/modules/protocols) · [backends](/modules/backends) · [缓解](/modules/mitigation) · [UCCSD+协议示例](/modules/quantum/algorithms/uccsd)
