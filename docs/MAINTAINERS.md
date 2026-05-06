# 维护角色（公开 parity / L1 签字）

**用途**：为 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)、[InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md) 等文档提供**流程上的「负责人」锚点**，而不绑定具体自然人姓名（合并 PR 时可按组织惯例填入所有者）。

| 角色 | 职责 |
|------|------|
| **Parity / 契约维护** | 矩阵 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 与 `inquanto_contract`、`inquanto_gap_categories` 同源；公开站改版时执行差距登记（见 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §5）。 |
| **度量与台账** | 月度更新台账 §3；主表 yes/partial/n/a 可用 `python scripts/count_parity_matrix_main_tables.py` 对照手填（脚本结论需与 gap 语义一致）。 |
| **签字合并 gate** | L1 清单合并前：全绿 `pytest`、`python scripts/check_parity_export_sample.py`；必要时在 signoff 表末行写明 **实名 + 日期**。 |

**替换约定**：若组织要求实名签字，在 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md) 末行将占位符换为实际维护人或架构负责人。
