# Tangelo Examples / Notebook → 本仓库 YAML（D19）

**原则**：本栈 **不以 dict Solver 为主配置**；下列映射给出「与 Tangelo 教程等价」的 **封装 YAML** 与研究员工厂函数入口。

| Tangelo 教程意象（GitHub / Examples） | `qchem-stack` 封装 YAML | 备注 |
|--------------------------------------|-------------------------|------|
| `VQESolver` + `mol_H2_sto3g` + 默认 UCCSD/HEA | `configs/example_h2.yaml`（HEA+VQE+Pauli）、`configs/example_h2_uccsd.yaml` | 后端见 `backend.provider` |
| ADAPT / IQEB | `configs/example_h2_iqeb.yaml`、`tutorial_inquanto_chain_h2.yaml`（若适用） | registry：`quantum.algorithm` |
| QPE 演示轨 | `configs/example_h2_qpe_track.yaml`、`configs/example_h2_qpe_track_parity_integrations.yaml` | 含 TKET 探针与 export 合一 |
| ZNE 叙事 | `configs/example_h2_zne_circuit_fold.yaml` | 与 Qiskit Pauli 合一键见 mitigation 文档 |
| 分解 / DMET 玩具 | `configs/example_decomposition_plugin_toy.yaml`、`configs/example_h4_dmet_fragment_exact_small.yaml` | **非** Tangelo 数值等价 |

**程序化加载**：[`examples/tangelo_facade_demo.py`](../examples/tangelo_facade_demo.py)（`load_packaged_example(...)`）。
