# UCCSD、JW 映射与 BK / SCBK 电路边界（工程裁断）

本文档裁断 [公开 parity 矩阵 §2](public_parity_matrix.md) 中 **AlgorithmVQE + `variational_ansatz: uccsd`** 的 **L1 范围**，避免被误读为在 **Bravyi–Kitaev / SCBK** 参考态上已实现与 Vendor platform 闭源堆栈 **L0 电路语义**对齐。

## 已支持（明确）

- **Jordan–Wigner**：`active_space.fermion_qubit_mapping: jordan_wigner`（默认）下，UCCSD 簇算符经 OpenFermion 流程映射为 **Pauli 字符串**，与 **同一映射下** 构建的 `QubitHamiltonian` 一致。
- **稠密簇指数**（`UCCSDVQE`）或 **一阶 Trotter 层重复**（`UCCSDTrotterVQE` + `quantum.variational.uccsd_trotter_steps`），见 [`quantum/algorithms/uccsd_vqe.py`](../src/qchem_stack/quantum/algorithms/uccsd_vqe.py) 与示例 `configs/example_h2_uccsd*.yaml`。
- **JW 电路路径**（`uccsd_circuit.py` + `uccsd_circuit_qiskit.py`）：AnsatzPrep / PauliAveraging 与 Qiskit 采样可导出 UCCSD prep CircuitIR；**Pauli 门分解**（`uccsd_pauli_decomposition.py`，默认 `quantum.uccsd.decomposition_mode: pauli`）替换稠密 `UNITARY` 占位，资源统计含 2Q/depth；parity 门禁见 `tests/quantum/test_uccsd_pauli_decomposition.py`、`tests/quantum/test_uccsd_circuit_parity.py`。示例：`configs/example_h2_uccsd_pauli_protocol.yaml`。

## 刻意不宣称（`n/a`）

- 在 **BK / SCBK** 映射的哈密顿量上，**不**随仓库提供「自动重标定」的 UCCSD 乘积公式包装；变分层仍可用 **HEA** + 该哈密顿量。**UCCSD ansatz 电路** 仍以 **JW–UCCSD** 语义实现；混用需用户自行承担解释与误差（非本仓 L1 契约）。

## 若需 BK/SCBK 上的化学激发线路

单独立项：显式 fermion–Pauli 语义、参考态与门分解策略，并配套可检证回归（小体系 + 能量/项数不变量），否则保持本裁断。
