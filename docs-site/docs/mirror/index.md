---
title: 公开文档镜像（审计视图）
---

# 公开文档镜像（审计视图）

<div class="qcs-mirror-audit-banner">

本区按**第三方公开文档**的目录结构做镜像索引，用于回答「公开文档里描述的能力 ↔ 本仓库实现到哪一步」。它是**审计附录**，**不是** qchem-stack 的产品说明书——产品介绍与任务路径请以 [四柱指南](/guide/) 为准。

每个节点在站内都有一页（未实现的节点保留**占位**），并标注 `shipped` / `partial` / `placeholder` / `not-applicable`。目标是让读者与合作方**独立核对**能力边界，而非复述外部文案。

</div>

## 状态图例

| 徽章 | 含义 |
|---|---|
| <StatusBadge status="shipped" /> | 已在 `qchem_stack` 落地或可替代实现 |
| <StatusBadge status="partial" /> | 字段或行为已就绪，但与参考文档公开语义可能不完全一致 |
| <StatusBadge status="placeholder" /> | 参考目录中存在对应节点，本仓库尚未实现，预留路由（见里程碑） |
| <StatusBadge status="not-applicable" /> | 按设计不对齐（云、计费、专有硬件等） |

<MirrorTree locale="zh" />

> 数据来自 `docs-site/scripts/mirror-doc-tree.yaml`（manifest）与 `scripts/scaffold-mirror.mjs`。修改 manifest 后执行 `npm run scaffold:mirror` 同步页面与本组件。
