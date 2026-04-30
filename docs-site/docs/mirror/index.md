---
title: 公开文档对照（审计视图）
---

# 公开文档对照（审计视图）

本区与 [Quantinuum 公开 InQuanto 文档树](https://docs.quantinuum.com/inquanto/) **结构对齐**，用于盘点「公开文档里有什么 ↔ 我们有什么」。它是 **透明对标附件**，**不是** qchem-stack 的产品说明书——产品介绍与任务路径请以 [四柱指南](/guide/) 为准。

每个节点在站内都有一页（未实现的节点保留**占位**），并标注 `shipped` / `partial` / `placeholder` / `not-applicable`。目标是让读者与合作方**独立审计**能力边界，而非复述官方文案。

## 状态图例

| 徽章 | 含义 |
|---|---|
| <StatusBadge status="shipped" /> | 已在 `qchem_stack` 等价或更优地落地 |
| <StatusBadge status="partial" /> | 字段或行为已就绪，但与 InQuanto **公开**语义不完全等价 |
| <StatusBadge status="placeholder" /> | 公开树中存在对应节点，本仓库尚未实现，预留路由（见里程碑） |
| <StatusBadge status="not-applicable" /> | 公开 parity 矩阵明示不对齐（云 / 计费 / 专有硬件等） |

<MirrorTree locale="zh" />

> 数据来自 `docs-site/scripts/inquanto-tree.yaml`（manifest）与 `scripts/scaffold-mirror.mjs`。修改 manifest 后执行 `npm run scaffold:mirror` 同步页面与本组件。
