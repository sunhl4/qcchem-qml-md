# PMSV / ZNE vs 公开 Qermit（errmit）文档映射（L1）

**范围**：仅对照 [Noise mitigation（errmit）](https://docs.quantinuum.com/inquanto/manual/errmit.html) 的**公开叙事**；不声称与 Qermit 闭源运行时或 InQuanto 默认数值一致。

| 公开概念 | `qchem_stack` 机读落点 | 备注 |
|----------|------------------------|------|
| Mitigation DAG / MitRes 形图 | `mitigation/qermit_analog.py` 报告 JSON；`GET /v1/meta/capability-surface` → `mitigation_execution_model` | 结构类比，非商业执行引擎 |
| 线性执行迹 | `mitigation_dag_execution`（pipeline 输出侧车） | 与异步 MitEx **批量**调度不对标 |
| PMSV（原型） | `MitigationSpec.pmsv_*`；`protocol_counts["pmsv_report"]`；export `protocol_pmsv_report_from_run` | 存根 + 可扩展 report |
| ZNE 标度 | `MitigationSpec.zne_scales`；parity / export | 与公开「多噪声标度」叙事对齐 |
| 设备 SPAM（若启用） | `mitigation` 包层级存根 | 矩阵中 `partial` |

### ZNE 端到端（开放栈 L1）

1. **YAML**：`mitigation.zne_enabled: true` 与 `mitigation.zne_scales`（浮点列表）定义标度序列；与 `MitigationSpec` 校验一致。
2. **运行时**：Pauli / 协议阶段在启用 ZNE 时把标度写入 `repro.parity_snapshot.mitigation_zne_scales`（及相关的 `mitigation_execution_class` 口径），供 Methods 与 `scripts/export_parity_criteria_table.py` 同源导出。
3. **与 PMSV**：二者可独立开关；`protocol_counts` / PMSV report 块见上表「PMSV」行。全链**不**等价 Qermit 闭源外推器 — 仅保证机读字段与 errmit **公开**多标度叙事可对读。
4. **回归**：矩阵 `partial` 行须引用本文 + gap `qermit_graph` 嵌套的 `mitigation_execution_model`。

### P2 进阶块（双月占位）：probabilistic error cancellation（文献向）

**状态**：仅文档占位（P2-W4），**不**在本迭代新增默认 DAG 节点或 `parity_snapshot` 顶键。

- **方向**：对照 errmit 公开叙事中的 **PEC / quasi-probability** 类思路，未来可选增加「shadow 通道 + 线性 combinator」实验块，与现有 `qermit_analog` **并行**注册，避免冒充商业 MitRes 调度。  
- **闸门**：任何新 `parity_snapshot` 键须先入 [inquanto_contract.py](../src/qchem_stack/protocols/inquanto_contract.py) 文档化集合 + 本文表格行 + `pytest` 最小单测。  
- **代表配置**：延续 ZNE 主线 `configs/example_h2_zne_circuit_fold.yaml`；PEC 若落地须新增独立 YAML 并加入 `scripts/check_parity_export_sample.py` 抽样表。

**ZNE × Qiskit Pauli 路径（机读合一）**：当 ``mitigation.zne_enabled`` 与 ``quantum.run_qiskit_shots_pauli_protocol`` 同时为真时，管线在 ``repro.parity_snapshot`` 写入 ``zne_qiskit_unification_v1``（``schema: zne_qiskit_unification_v1``）：串联 YAML 的 ``mitigation_zne_mode``、协议摘要里的 ``protocol_counts.zne_mode``、可选 ``zne_circuit_fold_fallback_reason``，以及固定 ``epistemic_bound`` 文案（开放栈：``circuit_scale_fold`` 仅作用于已编译 Pauli 执行路径上的 HEA 深度放大；shot 能量仍可能走标量 stub 标度）。代表 YAML：``configs/example_h2_zne_circuit_fold.yaml``。

权威 JSON：`inquanto_gap_categories` 中 `id=qermit_graph` 嵌套 `mitigation_execution_model`（`schema: mitigation_execution_model_v1`）。

**公开 errmit 手册钉扎（维护）**：本文档编写时对照 [Quantinuum errmit 手册](https://docs.quantinuum.com/inquanto/manual/errmit.html)，锚定日期见 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)「公开文档钉扎」。
