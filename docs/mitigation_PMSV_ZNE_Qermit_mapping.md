# PMSV / ZNE vs 公开 Qermit（errmit）文档映射（L1）

**范围**：仅对照 [Noise mitigation（errmit）](https://www.quantinuum.com/) 的**公开叙事**；不声称与 Qermit 闭源运行时或 Vendor platform 默认数值一致。

| 公开概念 | `qchem_stack` 机读落点 | 备注 |
|----------|------------------------|------|
| Mitigation DAG / MitRes 形图 | `mitigation/qermit_analog.py` 报告 JSON；`GET /v1/meta/capability-surface` → `mitigation_execution_model` | 结构类比，非商业执行引擎 |
| 线性执行迹 | `mitigation_dag_execution`（pipeline 输出侧车） | 与异步 MitEx **批量**调度不对标 |
| PMSV（原型） | `MitigationSpec.pmsv_*`；`protocol_counts["pmsv_report"]`；export `protocol_pmsv_report_from_run` | 存根 + 可扩展 report |
| ZNE 标度 | `MitigationSpec.zne_scales`；parity / export | 与公开「多噪声标度」叙事对齐 |
| PEC / quasi-probability（文献占位） | ``mitigation_pec_literature_stub_v1``（可选 YAML） | ``mitigation.pec_literature_stub_enabled``；非 MitRes |
| ZNE mode（YAML） | `MitigationSpec.zne_mode`（`scalar_stub` \| `circuit_scale_fold`） | `resource_estimation_preview_v1` 顶键 **`mitigation_zne_mode_yaml`** / **`mitigation_zne_scales_yaml`**；**`--results`** 时另附 **`parity_snapshot_mitigation_zne_*`**（与 `repro.parity_snapshot` 同源）；**`methods_resource_unified_v1`** 从 **`run_summary`** 镜像相同 `_yaml` 键，便于与 preview 对拍 |
| 设备 SPAM（若启用） | `mitigation` 包层级存根 | 矩阵中 `partial` |

### ZNE 端到端（开放栈 L1）

1. **YAML**：`mitigation.zne_enabled: true` 与 `mitigation.zne_scales`（浮点列表）定义标度序列；与 `MitigationSpec` 校验一致。
2. **运行时**：Pauli / 协议阶段在启用 ZNE 时把标度写入 `repro.parity_snapshot.mitigation_zne_scales`（及相关的 `mitigation_execution_class` 口径），供 Methods 与 `export_parity_criteria_table` 同源导出。
3. **导出块**：`resource_estimation_preview_v1.mitigation_zne_variants_v1` 列出 `modes_supported` 与 YAML `mitigation.zne.mode` / `zne.scales`（非闭源 Qermit 运行时）。
3. **与 PMSV**：二者可独立开关；`protocol_counts` / PMSV report 块见上表「PMSV」行。全链**不**等价 Qermit 闭源外推器 — 仅保证机读字段与 errmit **公开**多标度叙事可对读。
4. **回归**：矩阵 `partial` 行须引用本文 + **`product_gap_categories()`**（**`id=mitigation_batch_scheduler`**）并与 **`GET /v1/meta/capability-surface`** 载荷中的 **`mitigation_execution_model`** 一致。

### P2 进阶块（双月）：probabilistic error cancellation（文献向）

**状态（实现）**：当 YAML 设置 ``mitigation.pec_literature_stub_enabled: true`` 时，``repro.parity_snapshot`` 写入 ``mitigation_pec_literature_stub_v1``（``schema: mitigation_pec_literature_stub_v1``）。仍为 **占位**，不执行 quasi-probability 采样或商业 MitRes 调度。

- **方向**：与 errmit 公开叙事中的 **PEC / quasi-probability** 类思路 **可对读**，与现有 ``qermit_analog`` **并行**注册；不冒充 Qermit 二进制。  
- **闸门**：编排 / `parity_snapshot` / **`export_parity_criteria_table`** 与 `scripts/check_parity_export_sample.py` CI 抽样一致；代表配置 ``configs/example_h2_pec_literature_stub.yaml``。  
- **代表配置（ZNE 主线不变）**：延续 ``configs/example_h2_zne_circuit_fold.yaml``。

**ZNE × Qiskit Pauli 路径（机读合一）**：当 ``mitigation.zne_enabled`` 与 ``quantum.run_qiskit_shots_pauli_protocol`` 同时为真时，管线在 ``repro.parity_snapshot`` 写入 ``zne_qiskit_unification_v1``（``schema: zne_qiskit_unification_v1``）：串联 YAML 的 ``mitigation_zne_mode``、协议摘要里的 ``protocol_counts.zne_mode``、可选 ``zne_circuit_fold_fallback_reason``，以及固定 ``epistemic_bound`` 文案（开放栈：``circuit_scale_fold`` 仅作用于已编译 Pauli 执行路径上的 HEA 深度放大；shot 能量仍可能走标量 stub 标度）。代表 YAML：``configs/example_h2_zne_circuit_fold.yaml``。

权威 JSON：**HTTP `GET /v1/meta/capability-surface`** 返回 **`mitigation_execution_model`**（`schema: mitigation_execution_model_v1`）；产品差距行见 **`qchem_stack.protocols.product_contract.product_gap_categories()`**（**`id=mitigation_batch_scheduler`**）。

### MitigationSpec YAML 键（机读审计）

与 `qchem_stack.config.MitigationSpec` 嵌套块一一对应（YAML `mitigation.*`）：`execution_class`；`zne.enabled`、`zne.mode`、`zne.scales`；`pmsv.enabled`、`pmsv.stabilizers`、`pmsv.retention_rate`、`pmsv.report_extension`、`pmsv.extra`；`stubs.spam_calibration`、`stubs.pec_literature`、`stubs.classical_shadows`、`stubs.classical_shadows_budget_pairs`。加载时仍接受旧扁平键（`pmsv_enabled` 等）并由 migration 迁入子块。回归：`tests/mitigation/test_mitigation_output_schema.py`。

**公开 errmit 手册钉扎（维护）**：本文档编写时对照 [Quantinuum errmit 手册](https://www.quantinuum.com/)，锚定日期见 [与Vendor platform能力差距与实施计划 — 附录 C](public_parity_matrix.md#appendix-c)「公开文档钉扎」。
