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

权威 JSON：`inquanto_gap_categories` 中 `id=qermit_graph` 嵌套 `mitigation_execution_model`（`schema: mitigation_execution_model_v1`）。

**公开 errmit 手册钉扎（维护）**：本文档编写时对照 [Quantinuum errmit 手册](https://docs.quantinuum.com/inquanto/manual/errmit.html)，锚定日期见 [L1_InQuanto_alignment_signoff.md](/parity/l1-signoff)「公开文档钉扎」。
