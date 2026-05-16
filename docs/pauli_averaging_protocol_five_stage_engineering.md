# Pauli 测量协议五阶段工程说明

本文解释 `src/qchem_stack/protocols/protocol.py` 中的 `PauliAveragingProtocol` 如何把量子化学 Hamiltonian 的期望值估计拆成五个工程阶段：

```text
instantiate -> build -> compile -> run -> evaluate
   初始化       构建      编译      运行      后处理
```

核心目标是把

```text
H = c0 I + c1 P1 + c2 P2 + ...
```

中的 Pauli 项按可共同测量的结构分组，尽量减少需要执行的测量电路数，然后由 shots / bit-string / joint eigenvalue histogram 重建能量期望值。

## 1. instantiate：协议对象初始化

`instantiate()` 当前主要记录协议生命周期状态：

```python
def instantiate(self) -> None:
    self._phase = ProtocolPhase.INSTANTIATE
```

真正的输入在创建 `PauliAveragingProtocol(...)` 时已经传入，包括：

- `hamiltonian`: OpenFermion `QubitOperator`
- `n_qubits`: 量子比特数
- `backend`: 后端配置，例如 statevector、Qiskit、shots 数
- `pass_bundle`: 编译 pass
- `measurement_grouping`: Pauli 分组策略
- `run_sampled` / `run_qiskit_shots`: 运行时是否走 shots histogram 路径

因此，`instantiate` 更接近 Vendor platform 风格的“协议已实例化”阶段，而不是数值计算阶段。

## 2. build：Pauli 分组与逻辑测量电路构建

`build(angles, hea_depth)` 是第一个关键阶段。它保存 ansatz 参数，并调用：

```python
build_measurement_plan(self.hamiltonian, self.n_qubits, grouping=self.measurement_grouping)
```

生成 `PauliMeasurementPlan`。

工程中有两类分组。

### tensor_product 分组

默认策略是 `measurement_grouping="tensor_product"`，底层使用 OpenFermion 的：

```python
group_into_tensor_product_basis_sets(h)
```

这类分组要求同一组 Pauli 项可以在同一个 tensor-product 单比特测量基下同时测量。

例如：

```text
Z0, Z1, Z0 Z1
```

都可以在 Z basis 中同时测量。一个 bit-string 样本就能同时给出这些 Pauli 项的本征值。

如果某组需要测 X 或 Y，工程会在测量前加入 basis-change Clifford：

- X basis: `H`
- Y basis: `SDG` + `H`
- Z basis: 不需要额外门

对应实现位于 `src/qchem_stack/backends/pauli_measure_expand.py`。

### greedy_commuting 分组

`measurement_grouping="greedy_commuting"` 使用 binary symplectic representation 判断 Pauli word 是否两两对易：

```text
X -> (1, 0)
Z -> (0, 1)
Y -> (1, 1)
```

若两个 Pauli word 的 symplectic inner product 为 0，则它们对易，可以放入同一个 commuting group。

例如：

```text
X0 X1, Y0 Y1, Z0 Z1
```

两两对易，但它们不是同一个简单 tensor-product 单比特测量基。更新后的工程对这种情况会生成一条显式的逻辑 IR：

```text
HEA ansatz + JOINT_PAULI_MEASURE
```

也就是说，`build` 阶段现在不仅支持普通单比特 basis-change 测量，也能在 IR 层表达一般对易 Pauli group 的联合测量。

## 3. compile：CircuitIR 到后端编译入口

`compile()` 对 `build` 生成的 `_logical_circuits` 应用 pass bundle：

```python
pre = self.pass_bundle.preoptimize_passes + self.pass_bundle.compiler_passes
self._compiled = [apply_pass_bundle(c, pre) for c in self._logical_circuits]
```

当前工程的 `CircuitIR` 是轻量中间表示：

```python
@dataclass
class CircuitIR:
    n_qubits: int
    operations: list[dict[str, Any]]
    boxes: list[str]
```

`compile` 阶段的定位是把协议层的逻辑测量电路和具体后端隔开。当前实现中，pass bundle 主要处理元信息，例如 `qubit_reuse_hint` 和 `strip_boxes`。Qiskit shots 路径会在运行阶段进一步构造 Qiskit circuit 并调用 Qiskit `transpile`。

因此可以这样理解：

```text
build:
  产生“应该测什么”的逻辑 CircuitIR

compile:
  对 CircuitIR 做后端前的 pass / annotation / 资源统计准备
```

## 4. run：执行后端并生成 expectation

`run()` 是当前协议中最重的阶段。它会决定：

- 使用哪个 executor
- 使用哪个 measurement plan
- 每个 circuit 的 shots 数
- 是否根据 `target_energy_stderr` 推荐 shots
- 是否启用 PMSV / ZNE bookkeeping
- expectation 来源是 exact executor、statevector sampled shots，还是 Qiskit `get_counts`

### 默认 exact executor 路径

如果：

```python
run_sampled=False
run_qiskit_shots=False
```

则协议调用：

```python
exe.expectation_hea(self.hamiltonian, self.n_qubits, self.angles, self.hea_depth)
```

这通常是 statevector 精确期望值：

```text
<psi(theta)|H|psi(theta)>
```

这条路径不会真正从 bit-string histogram 重建能量。它仍会使用 measurement plan 估算 shots budget 和 stderr，并在 `_counts` 中记录：

```text
expectation_source = executor_exact_or_device_mean
energy_stderr_model = conservative_sum_bound_equal_shots
```

### run_sampled=True：statevector 上的 grouped shots 模拟

如果：

```python
run_sampled=True
```

协议先构造 HEA statevector：

```python
psi = hea_state(self.angles, self.n_qubits, self.hea_depth)
```

然后调用：

```python
energy_estimate_grouped_shot_simulation(...)
```

这条路径是真正的 shots 重建路径。

对于 `tensor_product` group，流程是：

1. 按 group 的 `basis_key` 把 statevector 旋转到测量基。
2. 按 computational-basis 概率抽样 bit-string。
3. 从 bit-string 计算组内每个 Pauli word 的本征值。
4. 乘以系数并组内求和。
5. 多个 group 的均值相加，再加 identity 项。

能量估计形式为：

```text
E ~= c_identity
   + sum_groups mean_over_shots(
       sum_terms_in_group c_t * lambda_t(sample)
     )
```

其中 `lambda_t(sample)` 是 Pauli word 在该 shot 上的本征值，取值为 `+1` 或 `-1`。

### 一般对易 group 的联合投影测量

更新后的工程补上了 `greedy_commuting` 的真实 grouped sampled 路径。

以前，若一个 group 没有 tensor-product `basis_key`，工程会退化为组内逐 Pauli 项采样。这样虽然分组计划里显示为一个 group，但执行语义上并不是真正的一次联合测量。

现在对于 `basis_key is None` 的 commuting group，`energy_estimate_grouped_shot_simulation` 会使用联合投影采样：

```text
对每个 shot:
  从原始 ansatz state 开始
  按组内 Pauli word 顺序做 projective measurement
  因为组内 Pauli 两两对易，顺序测量等价于采样联合本征值分布
  同一个 shot 得到整组 Pauli word 的 eigenvalue tuple
  用这一组 eigenvalue 同时重建组内能量
```

这使得如下 Hamiltonian 可以真正用一个 commuting group 测量：

```text
H = c1 X0 X1 + c2 Y0 Y1 + c3 Z0 Z1
```

这些项两两对易，但不是同一个简单 tensor-product basis。现在使用：

```python
PauliAveragingProtocol(
    hamiltonian=h,
    n_qubits=2,
    backend=BackendSpec(name="sim", shots_per_circuit=25000),
    measurement_grouping="greedy_commuting",
    run_sampled=True,
    record_histograms=True,
)
```

会得到：

```text
n_measurement_circuits = 1
total_shots_budget = shots_per_circuit
shot_noise_model = grouped_simultaneous_or_joint_projective
```

如果 `record_histograms=True`，`measurement_histogram_rows` 会记录：

```text
mode = commuting_joint_projective
histogram_eigenvalues = {"+,+,-": count, ...}
```

这里的 histogram 不是普通 computational bit-string，而是一般 commuting group 的联合本征值 histogram。对于 tensor-product group，仍然记录 computational-basis histogram。

### run_qiskit_shots=True：Qiskit get_counts 路径

如果：

```python
run_qiskit_shots=True
```

协议调用：

```python
energy_estimate_grouped_qiskit_shots(...)
```

该路径会：

1. 构造 Qiskit HEA circuit。
2. 对 tensor-product group 添加 basis-change gates。
3. `measure_all()`。
4. 调用 backend `run(...).result().get_counts()`。
5. 将 Qiskit bitstring 映射回本工程的 computational index。
6. 由 empirical histogram 重建 group expectation。

Qiskit bitstring 顺序和 OpenFermion/statevector 约定不同，因此工程使用：

```python
qiskit_bitstring_to_comp_index(...)
```

做 bit-order 规约。

当前 Qiskit shots 路径对 tensor-product group 是真实 `get_counts` 重建；对没有 `basis_key` 的一般 commuting group，仍保留逐项 fallback。一般 commuting group 的硬件级 Clifford 联合测量合成可以作为后续扩展接入 `JOINT_PAULI_MEASURE` IR。

## 5. evaluate：取出最终期望值

`evaluate()` 很薄：

```python
def evaluate(self) -> float:
    self._phase = ProtocolPhase.EVALUATE
    return float(self._counts.get("expectation", 0.0))
```

因此要注意：

```text
histogram -> expectation
```

的实质计算发生在 `run()` 阶段。`evaluate()` 只是进入后处理阶段并返回 `_counts["expectation"]`。

## 推荐使用方式

如果目标是演示 Pauli averaging 的标准 tensor-product measurement reduction：

```python
proto = PauliAveragingProtocol(
    hamiltonian=h,
    n_qubits=n_qubits,
    backend=BackendSpec(name="sim", shots_per_circuit=4096),
    measurement_grouping="tensor_product",
    run_sampled=True,
    record_histograms=True,
)
```

如果目标是演示一般对易 Pauli group 的联合测量能力：

```python
proto = PauliAveragingProtocol(
    hamiltonian=h,
    n_qubits=n_qubits,
    backend=BackendSpec(name="sim", shots_per_circuit=4096),
    measurement_grouping="greedy_commuting",
    run_sampled=True,
    record_histograms=True,
)
```

典型调用顺序：

```python
proto.instantiate()
proto.build(angles, hea_depth=1)
proto.compile()
proto.run()
energy = proto.evaluate()
```

## 工程状态总结

当前 `PauliAveragingProtocol` 的五阶段语义可以概括为：

```text
instantiate:
  建立协议对象和生命周期状态。

build:
  从 Hamiltonian 生成 Pauli measurement plan。
  tensor_product group 合成 HEA + basis-change + measure。
  greedy_commuting group 在无 tensor basis 时生成 HEA + JOINT_PAULI_MEASURE。

compile:
  对 CircuitIR 应用 pass bundle，为后端编译和资源统计保留入口。

run:
  exact executor 路径直接计算 <psi|H|psi>。
  run_sampled 路径从 grouped shots / joint eigenvalue histogram 重建 expectation。
  run_qiskit_shots 路径从 Qiskit get_counts 重建 tensor-product group expectation。

evaluate:
  返回 run 阶段写入的 expectation。
```

这套协议的核心价值是：把 VQE 中昂贵的 Hamiltonian expectation 测量，从“每个 Pauli 项单独跑电路”提升为“按可共同测量结构分组，一组 shots 同时服务多个 Pauli 项”，并在 `_counts` 中保留 expectation source、stderr model、shots budget、Pauli support 和 histogram 审计信息。
