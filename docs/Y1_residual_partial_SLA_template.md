# Y1 残余 `partial` 与 SLA 模板（Q4 / 年度签off）

**用途**：矩阵或差距表中仍为 `partial` 且**本年内未收束为 yes** 的项，必须有一行 SLA，避免「口头对齐」。筛选候选时可用机读 backlog：`jq '.nodes[] | select(.status=="partial")'` 见 `docs/inquanto-node-backlog.generated.json`。

| gap.id 或矩阵节 | 残余能力摘要 | 目标状态（yes / 仍 partial） | 目标季度 | 负责人 | 依赖（PySCF / GPU / …） |
|------------------|--------------|------------------------------|----------|--------|-------------------------|
| `ucc_chem_ansatz` | 化学 UCC 池与闭源默认非逐条对齐 | partial + 公开计数/refs | Y1-Q4 | | |
| `tensornet` | TN 化学尺度收缩 | partial + 小体系 L3 | Y2-Q1 | | cupy/cuquantum 可选 |
| `drivers_cosmo_pbc` | 全 driver 表面 / 多 k / 溶剂边界 | partial_kmesh | Y1-Q4 | | PySCF 版本 |
| `composable_computable` | 与闭源 Computable 融合顺序 | rich_optional（workflow-preview） | Y1-Q4 | | |
| `integrations_closure_layer` | 产品默认闭包 | reference_v1 | 长期 | | 仅 L1 |

**签off 规则**

- **云/硬件**：不进入本表（刻意不对齐）。
- **闭源不可检证**：允许长期 `partial`，但须每季度复核公开文档是否新增可检证项。

**年度结束时**：未达标行 → 复制至下年路线图或降级为文档级 `n/a` 并说明原因。
