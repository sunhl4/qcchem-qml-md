# CompilerSpec × protocol_counts × run_summary（联合叙事 · D14）

**用途**：Methods 表中可同时引用 **编译意图**（YAML `compiler.*`）、**Pauli 协议摘要**（运行态 `protocol_counts`）与 **`repro.run_summary`** 的稳定字段，不必宣称与闭源 TKET/Qermit 融合顺序一致。

| 层次 | 典型字段 | 写入阶段 |
|------|-----------|-----------|
| 配置（意图） | `compiler.optimization_level`、`compiler.native_twoq`、`compiler_preoptimize_passes` | YAML → `parity_snapshot`（配置快照段） |
| 编译产物（可选） | `tket_first_compiled_circuit_probe`（`parity_integrations.tket_first_circuit_stats`） | Pauli 协议后 `_finalize_open_stack_parity_snapshot` |
| 协议摘要 | `protocol_counts.expectation_source`、`zne_mode`、`pmsv_report` | `PauliAveragingProtocol` |
| run_summary | `protocol_expectation_source`、`pauli_averaging_protocol_ran`、`n_circuits`（若有） | `_attach_run_summary` |

**诚实边界**：默认路径未必跑 TKET；pytket 为可选依赖 — 见 [`技术文档_CircuitIR与TKET桥接及作业契约.md`](技术文档_CircuitIR与TKET桥接及作业契约.md)。

**QPE 演示轨**：`Algorithm*QPE` 侧 `run_summary` / `protocol_counts` 与上文并列时可Methods引用 [`src/qchem_stack/qpe_qec_demo/README.md`](../src/qchem_stack/qpe_qec_demo/README.md)（双轨 YAML、Bayesian stub）。
