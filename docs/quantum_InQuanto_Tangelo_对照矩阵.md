# Quantum 模块 InQuanto / Tangelo 公开能力对照矩阵

**目的**：在 L1 语义下，将 `qchem_stack.quantum` 与 InQuanto（Computable × Protocol）、Tangelo（BuiltInAnsatz / 激发态算法）公开叙事对齐；**不**宣称 L0 数值或闭源 API 等价。

**机读矩阵**：`qchem_stack.protocols.product_contract.ansatz_protocol_matrix_v1()`（CI：`tests/api/test_api_runs.py::test_capability_surface_matches_product_contract`）。

## Ansatz × Protocol 正交

| 能力 | InQuanto / Tangelo 叙事 | qchem_stack | L1 状态 |
|------|-------------------------|-------------|---------|
| Ansatz 准备与 Protocol 分离 | Computable + ProtocolList | `protocols/ansatz_prep.py` + `PauliAveragingProtocol` | yes |
| UCCSD JW 电路 | Pauli 旋转 / 稠密簇指数 | `uccsd_pauli_decomposition.py` + `decomposition_mode: pauli\|unitary` | yes（JW） |
| BK/SCBK UCCSD 电路 | 产品默认 | 未包装 | n/a（见 UCCSD 边界文档） |
| ExpectationValue | 能量期望 | `protocols/computables/expectation.py` | yes |
| QSE 矩阵 | H/S 子空间 | `protocols/computables/qse_matrices.py` | partial→yes（statevector + **qiskit** `pauli_transitions_qiskit`） |
| SCEOM M 矩阵 | 嵌套对易子 | `protocols/computables/sceom_matrix.py` | yes（HEA + UCCSD `prepare_state`） |
| Overlap² | 重叠惩罚 | `protocols/computables/overlap.py` + VQD deflation CSWAP sketch | partial→yes（statevector + Qiskit export） |
| ProtocolList 批跑 | 同 prep 多 computable | `protocols/protocol_list.py` | yes（本地顺序批跑） |

## 激发态算法

| 算法 | Tangelo / InQuanto | qchem_stack | 示例 YAML |
|------|-------------------|-------------|-----------|
| VQE + UCCSD | AlgorithmVQE | `uccsd_vqe.py` / Pauli protocol | `example_h2_uccsd_pauli_protocol.yaml` |
| QSE | AlgorithmQSE | `excited_qse.py` + `qse_transition.py` | `example_h2_uccsd_qse_pauli_qiskit.yaml` |
| VQD | AlgorithmVQD | `excited_vqd.py`；`optimizer_mode: three_computable`；`deflation_circuit` + Qiskit export | `example_h2_vqd_uccsd_three_computable.yaml`、`example_h2_vqd_deflation_circuit.yaml` |
| SCEOM | AlgorithmSCEOM | `sceom.py` + **`SCEOMMatrixComputable`**（HEA/UCCSD） | excited smoke / extended tests |
| SA-VQE | Tangelo SAOO-VQE 叙事 | `algorithms/sa_vqe.py` | `example_h2_sa_vqe.yaml` |

## QSE 扩展

| 键 | 值 | 说明 |
|----|-----|------|
| `quantum.excited.qse.shot_mode` | `pauli_transitions_qiskit` | Qiskit histogram 过渡振幅 |
| `quantum.excited.qse.expansion_pool` | `fermionic_singles` / `fermionic_singles_doubles` | UCCSD 参考基扩展 |

## 刻意 partial / n/a

- Nexus 分布式 ProtocolList / 云 batch scheduler
- 完整 QSCEOM 对称性 filter + InQuanto DataFrame parity
- BK/SCBK UCCSD Pauli 电路自动包装
- Tangelo 全套 BuiltInAnsatz：**executable**：HEA、UCCSD、**UCCGD**、**QCC**、**UpCCGSD**、**pUCCD**；**partial 别名**：VSQS→HEA；**研究插件**：iQCC、QITE；**`n/a`**：JKMN/HCB 映射（见 `fermion_mapping_registry`）

## Parity 导出新键

`export_parity_criteria_table.py` 导出：`uccsd_decomposition_mode`、`qse_expansion_pool`、`vqd_optimizer_mode`、`sceom_generator_strategy`。
