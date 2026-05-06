# Y1 残余 `partial` 与 SLA 模板（Q4 / 年度签off）

**用途**：矩阵或差距表中仍为 `partial` 且**本年内未收束为 yes** 的项，必须有一行 SLA，避免「口头对齐」。

完整表格见仓库 **`docs/Y1_residual_partial_SLA_template.md`**。

| gap.id 或矩阵节 | 残余能力摘要 | 目标状态（yes / 仍 partial） | 目标季度 |
|------------------|--------------|------------------------------|----------|
| `ucc_chem_ansatz` | 化学 UCC 池与闭源默认非逐条对齐 | partial + JW UCCSD/Trotter YAML | Y1-Q4 |
| `tensornet` | TN 化学尺度收缩 | **n/a**（stub；不宣称 `inquanto-cutensornet`） | Y2-Q2 |
| `drivers_cosmo_pbc` | 全 driver 表面 / 多 k / 溶剂边界 | partial_kmesh | Y1-Q4 |
| `composable_computable` | 与闭源 Computable 融合顺序 | rich_optional（workflow-preview） | Y1-Q4 |
| `integrations_closure_layer` | 产品默认闭包 | reference_v1 | 长期 |
| `dmet_scf_loop` | 完整 DMET bath / 闭源 bath 拟合 | partial + 文档钩子 | Y2-Q1 |
| `qermit_graph`（ZNE×Qiskit） | circuit_fold 与 Qiskit shots 合一 | partial + `zne_qiskit_unification_v1` | Y1-Q4 |
| `AlgorithmBayesianQPE` / Phayes | 非 Phayes 产品深度 | partial + stub 键 | 长期 |

**签off**：云/硬件不进入本表；闭源不可检证项允许长期 `partial`，须季度复核公开文档。
