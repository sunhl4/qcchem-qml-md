# 租户与配额

**状态**：占位骨架（Wave W0）。**目标**：把 **workspace / tenant** 与 **公平队列、配额** 写成可验收的 HTTP 与运维文档 — 对标 InQuanto+Nexus 联合叙事中的「项目与资源」，但以 **开源栈可检证** 为约束。

## 建议字段（契约级）

| 概念 | 说明 |
|------|------|
| `workspace_label` | 逻辑隔离边界；映射到 SQLite 中的外键或独立 DB 文件策略（产品选型）。 |
| 配额 | 每 workspace 并发 run 数、最大 wall time；**默认拒绝无限占满** 模拟器池。 |
| 公平性 | 队列算法（FIFO + 小作业穿插）与 **可观测指标**（等待时间分位数）。 |

## 与 backlog

节点 backlog 中 `platform_dimensions.cloud_tenant` 与本页应对齐；关闭 wave 时在 PR 描述中引用 `appendix_c_node_index` 或 `breadcrumb`。
