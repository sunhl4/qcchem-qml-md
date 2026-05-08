# 技术文档：设备比特串与 Qiskit 采样路径（`get_counts` → Pauli 平均）

## 1. 目的与边界

本仓库是 **独立开源** 的编排与协议栈，**不声称** 与 Quantinuum 闭源 InQuanto 的二进制同构。本文档说明：在**公开、可复现的契约**下，如何实现与公开资料中「**run（采样）→ 测量直方图 → 能量（期望）**」同构的 **Qiskit 比特串路径**，与已有的 **状态向量蒙特卡洛**（`run_sampled_pauli_protocol` / `pauli_shot_sim`）和 **执行器精确期望** 路径的关系。

| 能力 | 说明 |
|------|------|
| **有** | 对每组对易 Pauli，构造 **HEA + 单比特基变更 + 全比特测量** 的 Qiskit 线路；`Aer` 或真实 `Backend.run(..., shots=...)`；`get_counts`；按与 `pauli_shot_sim` **同一套** 张量/计算基索引，把 `histogram` 重组成 \(\langle H\rangle\) 的估计及分组方差近似。 |
| **无** | 不绑定 IBM Quantum 账号、Nexus 作业队列、InQuanto 内部对象名或未公开 API；不保证与闭源 InQuanto 的数值逐比特一致。 |

**前置条件**：下列三条路径均在 **`quantum.use_pauli_protocol: true`** 且管线实际构造 `PauliAveragingProtocol` 时生效。若 `use_pauli_protocol: false`，管线在 `pre_pauli_protocol` 之后直接跳过 Pauli 阶段（无 `protocol_counts` 中的本节字段）；见 `orchestration/pipeline.py` 中 `pauli_protocol_skipped` 分支。

**机读分类（CI / gap）**：`qchem_stack.protocols.inquanto_contract.protocol_expectation_semantics_public()` 将上述开关组合映射到 `protocol_counts_expectation_source` / `protocol_counts_energy_stderr_model`，与 parity 导出同源维护。

**对标叙事**：在「公开的产品故事」上，本路径与 InQuanto 文档中常见的 **Computable → Protocol / shot schedule → counts → expectation** 一致；实现落点在 `qchem_stack.backends.qiskit_pauli_shots` 与 `PauliAveragingProtocol.run` 的 `run_qiskit_shots` 分支。

## 2. 三条 Pauli 协议能量路径对比

记 Hamiltonian 的 Pauli 分解为 \(H=\sum_P c_P P\)。分组测量计划将 \(\{P\}\) 划分为对易组 \(G_k\)；每组一次（或若干次子 shots）线路读出计算基计数，再把各 Pauli 本征值在采样基上累加得到 \(\hat E\)。能量不确定度 `energy_stderr` 在各路径下采用不同模型（见各路径的 `energy_stderr_model`）。

1. **默认**（`run_sampled_pauli_protocol: false` 且 `run_qiskit_shots_pauli_protocol: false`）  
   由 `HamiltonianExpectationExecutor.expectation_hea` 提供 \(\langle H\rangle\)（`statevector` / `QiskitStatevector` 等 **精确或设备解析期望**，取决于 `BackendSpec`）。`protocol_counts` 写入：`expectation_source: executor_exact_or_device_mean`，`energy_stderr_model: conservative_sum_bound_equal_shots`（`backends/shot_budget.energy_estimate_with_uncertainty` 的保守上界，可按 `target_energy_stderr` 反推有效 `shots_per_circuit`）。

2. **状态向量分组蒙特卡洛**（`run_sampled_pauli_protocol: true`）  
   在 `hea_state` 上按组从计算基分布 **采样**，与 InQuanto 式「模拟 shot」一致。直方图来自**模拟**计数。实现：`backends/pauli_shot_sim.py`。`protocol_counts`：`expectation_source: grouped_shot_simulation_statevector`，`energy_stderr_model: sample_stderr_independent_groups_approx`。

3. **Qiskit 比特串路径**（`run_qiskit_shots_pauli_protocol: true`）  
   每条（子）线路在 Qiskit 上 `run` 指定 `shots`，直方图来自 `result().get_counts()`。实现：`backends/qiskit_pauli_shots.py`。`protocol_counts`：`expectation_source: qiskit_shot_counts_get_counts`，`energy_stderr_model: empirical_shot_variance_independent_groups_approx`。

**PMSV**：若启用 PMSV 且 `retention_rate<1`，协议层对 `energy_stderr` 额外乘 `1/sqrt(retention_rate)` 记入 `pmsv_stderr_scale`（与 ZNE 电路放大不同：仍为协议层 stderr 缩放）。

配置约束（`QuantumSpec`）：`run_sampled_pauli_protocol` 与 `run_qiskit_shots_pauli_protocol` **不能同时为 true**（`PauliAveragingProtocol.run` 与 `QuantumSpec` 模型校验一致）。

## 3. 线路与线序约定

- **HEA 线路**：`backends/qiskit_executor.hea_circuit_qiskit` 与 `hea_state` 一致：逻辑比特 `q` 映射到 Qiskit 物理线 `n_qubits - 1 - q`（与 OpenFermion 张量轴 `0..n-1` 对齐的惯例）。
- **基变更**：与 `pauli_measure_expand.basis_change_operations` 同构：\(X \to H\)；\(Y \to S^\dagger H\)；在 Qiskit 侧作用在**对应物理线**上（见 `qiskit_pauli_shots._append_pauli_basis_to_qiskit`）。
- **测量**：`measure_all()`，得到 `get_counts` 的比特串；键的解析方式见下一节。

## 4. 计算基索引（`comp_index`）与 Qiskit 比特串的映射

`pauli_shot_sim` 中，计算基以 **OpenFermion 逻辑比特 `q` 为 `comp_index` 的比特位**（`q=0` 为 LSB）：

- `pauli_shot_sim._pauli_eigenvalue_on_comp_bit(term, comp_index, n_qubits, basis_key)` 依赖该约定。

Qiskit 的 `get_counts` 使用 **按物理线** 的比特串，MSB 在左。设 `K = int(bitstring, 2)`（`n` 位），则与上述 **逻辑** 张量下标 `i` 的关系为 **对 `n` 位按位取反（bit-reversal）**：

\[
i = \text{bit\_reverse\_n}(K, n)
\]

该关系由 `hea_circuit` 的线序与 `Statevector` / `hea_state` 的 axis 序对齐验证，实现见 `qiskit_pauli_shots._bit_reverse_n` 与 `qiskit_bitstring_to_comp_index`。

**直方图模式**：`protocol_counts.measurement_histogram_rows` 中，按组保存 `histogram_comp_index: { "0": n0, "1": n1, ... }`，与 `pauli_shot_sim` 的 `statevector` 模式同一 schema，并带有 `source: "qiskit_shot_counts"` 便于筛选。

**原始 Qiskit 键**：`protocol_counts["qiskit_pauli_shot_meta"]["qiskit_counts_per_group"]` 中保留 `raw_qiskit_counts`（Qiskit 原样键，便于与外部判据对账）。

## 5. `greedy_commuting` 且无合成 `basis_key` 的分组

与 `pauli_shot_sim` 相同：对组内**每个** Pauli 项单独做一条「HEA + 该项的 basis + 测量」线路，**均分** `shots_per_circuit` 为 `sub_shots`（与 statevector 模拟中的 fallback 结构一致）。该路径会放大线路数，适合中小 Hamiltonian。

## 6. `protocol_counts` 中与本路径相关的键

- `expectation_source`: **`qiskit_shot_counts_get_counts`**
- `energy_stderr_model`: **`empirical_shot_variance_independent_groups_approx`**
- `qiskit_pauli_shot_meta`: 含 `total_shots_used`、`qiskit_counts_per_group`、可选 `measurement_histogram_rows`
- `pmsv_report`：仍按协议层的 toy 缩放/记账（**不是** 真实硬件 readout 层析）；若 `retention_rate < 1` 会缩放 stderr 报告值

## 7. 配置参考（YAML）

最小片段：

```yaml
backend:
  provider: "qiskit"
  shots_per_circuit: 2048
  meta:
    qiskit_shots_backend: "aer"          # 默认无此项亦视作文内默认 Aer
    qiskit_transpile_optimization: 0     # 透传给 transpile

quantum:
  use_pauli_protocol: true
  pauli_grouping: "tensor_product"
  run_qiskit_shots_pauli_protocol: true
  record_pauli_measurement_histograms: true
```

完整示例见仓库内 `configs/example_h2_qiskit_shots.yaml`。

### 7.1 `backend.meta` 参考

| 键 | 含义 |
|----|------|
| `qiskit_shots_backend` | 字符串 `"aer"` / `"aer_simulator"` 时构造 `AerSimulator`；或 **Python 中已构造** 的 `Backend` 实例（需有 `.run`）。 |
| `aer_method` | 传给 `AerSimulator(method=...)`，默认 `automatic`。 |
| `qiskit_transpile_optimization` | `transpile(..., optimization_level=...)`，默认 `0`（可重复性优先时建议 0）。 |

### 7.2 与 IBM 硬件对接（概要）

1. 使用 IBM Provider 取得目标 `Backend` 实例。  
2. 将实例赋给 **`backend.meta["qiskit_shots_backend"]`**（在 Python 中加载配置后写回，或在自定义脚本中构建 `BackendSpec`）。  
3. 为降低插入误差，可酌情提高 `qiskit_transpile_optimization` 并依设备校准配置 **layout / scheduling**（属 Qiskit 使用范畴，本栈仅透传 transpile）。  

**诚实说明**：与 InQuanto 的「Nexus + H1」一站体验不同，本仓库不内置凭证与队列，仅保留 **Qiskit 标准接口** 以便对接任意 provider。

## 8. 与 InQuanto **公开** 契约的对齐点（非闭源同构）

- **阶段模型**：`PauliAveragingProtocol` 仍为 instantiate → build → compile → run → evaluate；`run` 在 Qiskit 路径下改变 **能量来源** 为比特串直方图估计，**不改变** 资源行 `dataframe_circuit_shot_rows` 的生成逻辑。  
- **可导出资源**：`resource_rows` / `pauli_measurement_ledger`、parity 导出处仍可与 `export_parity_criteria_table` 联动（能量字段以本次 `expectation_source` 为准）。  
- **不声称项**：`Computable` 类型级与 TKET/Quantinuum 私有的 1:1 绑定；Nexus 作业 ID 语义；H-series 真机校准细节。

## 9. 测试与回归

- `tests/test_qiskit_pauli_shots.py`：线序/比特反转、`energy_estimate_grouped_qiskit_shots` 与 Qiskit 精确期望在**大 shots** 下接近、以及 `PauliAveragingProtocol` 的 **run_qiskit_shots** 端到端。  
- 需安装 `qchem_stack[quantum]`（`qiskit` + `qiskit-aer`）。

## 10. 故障排查

| 现象 | 可能原因 |
|------|----------|
| `ImportError: Qiskit Pauli shots require qiskit` | 未安装 `pip install qchem_stack[quantum]` |
| 能量与精确期望差很大且 stderr 大 | 正常 shot noise；增大 `shots_per_circuit` 或 `target_energy_stderr` 间接增大推荐 shots |
| `greedy` 下极慢 | 无 `basis_key` 时每项一线路；可改用 `tensor_product` 或缩小 Hamiltonian / 先跑精确路径 |

---

*文档版本与代码：`expectation_source` / `energy_stderr_model` 以 `protocols/protocol.py` 中 `PauliAveragingProtocol.run` 写入 `proto._counts` 的字符串为准；Qiskit 路径下 `expectation_source = qiskit_shot_counts_get_counts`。直方图 schema 与 `pauli_shot_sim` 的 `measurement_histogram_rows` 一致（并增加 `source: "qiskit_shot_counts"` 便于筛选）。*
