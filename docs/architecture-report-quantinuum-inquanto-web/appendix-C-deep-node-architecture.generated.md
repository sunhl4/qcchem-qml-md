---
title: Appendix C — Per-node architecture decomposition (generated)
description: Rule-based IA/security/cloud/test checklist per manifest node (295 nodes). Not hand prose.
edit: false
---

> **Do not hand-edit.** 由 `mirror-doc-tree.yaml` **全量扁平节点** 规则生成；每一节结构相同，便于 diff 与评审。
> 非「编造功能」，未在 manifest 出现的字段一律写 **—** 或 **推断** 模板句。

**Source pin**: 2026-04-30 · **Upstream doc version**: 5.2.3 · **Nodes**: 295

## 本附录的阅读方法

- 按 **breadcrumb** 与 InQuanto 公开 URL 对照。
- **§7 兄弟节点** 来自 manifest 树结构，用于发现 **遗漏交叉链接**。
- **§11** 合并云/安全/SEO/i18n/CI 检查单；不适用项仍保留以证明 **已评审**。

---
# 节点 1 / 295 — `introduction`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction` |
| slug | `introduction` |
| title_zh / en | 介绍 / Introduction |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/ |
| pillar / diataxis / class_leaf | meta / concept / no |
| mirror_path | `/mirror/introduction/` |

- **L1 分区**: `introduction` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 2 / 295 — `introduction.overview`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction / overview` |
| slug | `overview` |
| title_zh / en | 产品概览（参考文档镜像） / Product overview (reference mirror) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/overview.html |
| pillar / diataxis / class_leaf | meta / concept / no |
| mirror_path | `/mirror/introduction/overview/` |

- **L1 分区**: `introduction` → **L2..n**: `overview`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `installation` — Installation（安装）· `shipped`
- `quickstart` — Quick-start guide（快速上手）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/overview/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 3 / 295 — `introduction.installation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction / installation` |
| slug | `installation` |
| title_zh / en | 安装 / Installation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/installation.html |
| pillar / diataxis / class_leaf | meta / tutorial / no |
| mirror_path | `/mirror/introduction/installation/` |

- **L1 分区**: `introduction` → **L2..n**: `installation`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `overview` — Product overview (reference mirror)（产品概览（参考文档镜像））· `shipped`
- `quickstart` — Quick-start guide（快速上手）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/installation/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 4 / 295 — `introduction.installation.system_requirements`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction / installation / system_requirements` |
| slug | `system_requirements` |
| title_zh / en | 系统要求 / System requirements |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/system_requirements.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/introduction/installation/system_requirements/` |

- **L1 分区**: `introduction` → **L2..n**: `installation` → `system_requirements`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `troubleshooting` — Troubleshooting（故障排除）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/installation/system_requirements/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 5 / 295 — `introduction.installation.troubleshooting`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction / installation / troubleshooting` |
| slug | `troubleshooting` |
| title_zh / en | 故障排除 / Troubleshooting |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/troubleshooting.html |
| pillar / diataxis / class_leaf | meta / concept / no |
| mirror_path | `/mirror/introduction/installation/troubleshooting/` |

- **L1 分区**: `introduction` → **L2..n**: `installation` → `troubleshooting`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `system_requirements` — System requirements（系统要求）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/installation/troubleshooting/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 6 / 295 — `introduction.quickstart`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `introduction / quickstart` |
| slug | `quickstart` |
| title_zh / en | 快速上手 / Quick-start guide |
| reference_doc_url | https://docs.quantinuum.com/inquanto/introduction/quickstart.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/introduction/quickstart/` |

- **L1 分区**: `introduction` → **L2..n**: `quickstart`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `introduction`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **Manifest 摘要（zh）**: H2/STO-3G 上以 UCCSD ansatz 与 VQE 在态向量后端跑出的最小工作流。
- **Manifest 摘要（en）**: Minimal H2/STO-3G UCCSD VQE workflow on a state-vector backend.
- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `overview` — Product overview (reference mirror)（产品概览（参考文档镜像））· `shipped`
- `installation` — Installation（安装）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.express`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/introduction/quickstart/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 7 / 295 — `manual`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual` |
| slug | `manual` |
| title_zh / en | 用户手册 / Manual |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/ |
| pillar / diataxis / class_leaf | meta / concept / no |
| mirror_path | `/mirror/manual/` |

- **L1 分区**: `manual` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 8 / 295 — `manual.howto`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / howto` |
| slug | `howto` |
| title_zh / en | 参考手册 · 使用说明 / Reference manual · How-to |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/howto.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/howto/` |

- **L1 分区**: `manual` → **L2..n**: `howto`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/howto/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 9 / 295 — `manual.geometry`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / geometry` |
| slug | `geometry` |
| title_zh / en | 几何 / Geometry |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/geometry.html |
| pillar / diataxis / class_leaf | P1 / concept / no |
| mirror_path | `/mirror/manual/geometry/` |

- **L1 分区**: `manual` → **L2..n**: `geometry`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 经典量子化学基础（HF、活性空间、分子几何）。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.molecule`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/geometry/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 10 / 295 — `manual.express`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / express` |
| slug | `express` |
| title_zh / en | Express 数据集 / Express data sets |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/express.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/manual/express/` |

- **L1 分区**: `manual` → **L2..n**: `express`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.express`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/express/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 11 / 295 — `manual.symmetry`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / symmetry` |
| slug | `symmetry` |
| title_zh / en | 对称性 / Symmetry |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/symmetry.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/symmetry/` |

- **L1 分区**: `manual` → **L2..n**: `symmetry`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/symmetry/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 12 / 295 — `manual.spaces_operators`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / spaces_operators` |
| slug | `spaces_operators` |
| title_zh / en | 空间 / 算符 / 状态 / 映射 / Spaces, operators, states and mappings |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/spaces.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/spaces_operators/` |

- **L1 分区**: `manual` → **L2..n**: `spaces_operators`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.hamiltonian`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/spaces_operators/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 13 / 295 — `manual.spaces_operators.interfacing_qchem`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / spaces_operators / interfacing_qchem` |
| slug | `interfacing_qchem` |
| title_zh / en | 与外部量化包接口（FCIDUMP） / Interfacing with quantum chemistry packages (FCIDUMP) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/spaces.html#interfacing-quantum-chemistry |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/spaces_operators/interfacing_qchem/` |

- **L1 分区**: `manual` → **L2..n**: `spaces_operators` → `interfacing_qchem`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `qubit_mapping` — Qubit mapping（量子比特映射）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/spaces_operators/interfacing_qchem/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 14 / 295 — `manual.spaces_operators.qubit_mapping`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / spaces_operators / qubit_mapping` |
| slug | `qubit_mapping` |
| title_zh / en | 量子比特映射 / Qubit mapping |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/spaces.html#qubit-mapping |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/spaces_operators/qubit_mapping/` |

- **L1 分区**: `manual` → **L2..n**: `spaces_operators` → `qubit_mapping`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `interfacing_qchem` — Interfacing with quantum chemistry packages (FCIDUMP)（与外部量化包接口（FCIDUMP））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.hamiltonian.molecular_hamiltonian_from_classical_reference`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/spaces_operators/qubit_mapping/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 15 / 295 — `manual.ansatze`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / ansatze` |
| slug | `ansatze` |
| title_zh / en | Ansatze 概览 / Ansatze overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/ansatzae_overview.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/ansatze/` |

- **L1 分区**: `manual` → **L2..n**: `ansatze`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.ansatze`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/ansatze/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 16 / 295 — `manual.ansatze.ucc_family`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / ansatze / ucc_family` |
| slug | `ucc_family` |
| title_zh / en | UCC 家族 / UCC family |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/ansatze/ucc_family.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/ansatze/ucc_family/` |

- **L1 分区**: `manual` → **L2..n**: `ansatze` → `ucc_family`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `hardware_efficient` — Hardware-efficient ansatz（硬件高效 ansatz（HEA））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/ansatze/ucc_family/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 17 / 295 — `manual.ansatze.hardware_efficient`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / ansatze / hardware_efficient` |
| slug | `hardware_efficient` |
| title_zh / en | 硬件高效 ansatz（HEA） / Hardware-efficient ansatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/ansatze/hea.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/ansatze/hardware_efficient/` |

- **L1 分区**: `manual` → **L2..n**: `ansatze` → `hardware_efficient`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `ucc_family` — UCC family（UCC 家族）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.ansatze.hea`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/ansatze/hardware_efficient/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 18 / 295 — `manual.minimizers`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / minimizers` |
| slug | `minimizers` |
| title_zh / en | 极小化器 / Minimizers |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/minimizers.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/manual/minimizers/` |

- **L1 分区**: `manual` → **L2..n**: `minimizers`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.minimizers`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/minimizers/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 19 / 295 — `manual.computables`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / computables` |
| slug | `computables` |
| title_zh / en | Computables 概览 / Computables overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/computables_overview.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/computables/` |

- **L1 分区**: `manual` → **L2..n**: `computables`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.computable`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/computables/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 20 / 295 — `manual.computables.atomic`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / computables / atomic` |
| slug | `atomic` |
| title_zh / en | 原子 computable / Atomic computables |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/computables/atomic.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/computables/atomic/` |

- **L1 分区**: `manual` → **L2..n**: `computables` → `atomic`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `composite` — Composite computables（复合 computable）· `placeholder`
- `primitives` — Primitive computables（原语 computable）· `placeholder`
- `evaluating_w_protocols` — Evaluating with protocols（用 Protocol 求值）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/computables/atomic/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 21 / 295 — `manual.computables.composite`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / computables / composite` |
| slug | `composite` |
| title_zh / en | 复合 computable / Composite computables |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/computables/composite_computables.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/computables/composite/` |

- **L1 分区**: `manual` → **L2..n**: `computables` → `composite`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `atomic` — Atomic computables（原子 computable）· `partial`
- `primitives` — Primitive computables（原语 computable）· `placeholder`
- `evaluating_w_protocols` — Evaluating with protocols（用 Protocol 求值）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/computables/composite/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 22 / 295 — `manual.computables.primitives`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / computables / primitives` |
| slug | `primitives` |
| title_zh / en | 原语 computable / Primitive computables |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/computables/primitives.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/computables/primitives/` |

- **L1 分区**: `manual` → **L2..n**: `computables` → `primitives`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `atomic` — Atomic computables（原子 computable）· `partial`
- `composite` — Composite computables（复合 computable）· `placeholder`
- `evaluating_w_protocols` — Evaluating with protocols（用 Protocol 求值）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/computables/primitives/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 23 / 295 — `manual.computables.evaluating_w_protocols`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / computables / evaluating_w_protocols` |
| slug | `evaluating_w_protocols` |
| title_zh / en | 用 Protocol 求值 / Evaluating with protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/computables/evaluating_w_protocols.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/computables/evaluating_w_protocols/` |

- **L1 分区**: `manual` → **L2..n**: `computables` → `evaluating_w_protocols`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `atomic` — Atomic computables（原子 computable）· `partial`
- `composite` — Composite computables（复合 computable）· `placeholder`
- `primitives` — Primitive computables（原语 computable）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.computable`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/computables/evaluating_w_protocols/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 24 / 295 — `manual.protocols`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols` |
| slug | `protocols` |
| title_zh / en | Protocols 概览（五阶段） / Protocols overview (five stages) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols_overview.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/` |

- **L1 分区**: `manual` → **L2..n**: `protocols`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **Manifest 摘要（zh）**: instantiate → build → compile → run → evaluate 五阶段；可挂噪声缓解、资源估计、测量优化。
- **Manifest 摘要（en）**: Five-stage workflow (instantiate → build → compile → run → evaluate) with mitigation, resource estimation, measurement optimization hooks.
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.PauliAveragingProtocol`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 25 / 295 — `manual.protocols.statevector`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / statevector` |
| slug | `statevector` |
| title_zh / en | 态向量 Protocol / Statevector protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/statevector.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/statevector/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `statevector`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `averaging` — Averaging protocols（平均（Pauli）Protocol）· `shipped`
- `overlap` — Overlap protocols（重叠 / 投影 Protocol）· `placeholder`
- `derivatives` — Derivative protocols（导数 Protocol）· `placeholder`
- `phase_estimation` — Quantum phase estimation protocols（量子相位估计 Protocol）· `placeholder`
- `resource_estimation` — Resource estimation（资源估计）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/statevector/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 26 / 295 — `manual.protocols.averaging`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / averaging` |
| slug | `averaging` |
| title_zh / en | 平均（Pauli）Protocol / Averaging protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/expval.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/averaging/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `averaging`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `statevector` — Statevector protocols（态向量 Protocol）· `partial`
- `overlap` — Overlap protocols（重叠 / 投影 Protocol）· `placeholder`
- `derivatives` — Derivative protocols（导数 Protocol）· `placeholder`
- `phase_estimation` — Quantum phase estimation protocols（量子相位估计 Protocol）· `placeholder`
- `resource_estimation` — Resource estimation（资源估计）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.PauliAveragingProtocol`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/averaging/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 27 / 295 — `manual.protocols.overlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / overlap` |
| slug | `overlap` |
| title_zh / en | 重叠 / 投影 Protocol / Overlap protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/overlap.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/overlap/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `overlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `statevector` — Statevector protocols（态向量 Protocol）· `partial`
- `averaging` — Averaging protocols（平均（Pauli）Protocol）· `shipped`
- `derivatives` — Derivative protocols（导数 Protocol）· `placeholder`
- `phase_estimation` — Quantum phase estimation protocols（量子相位估计 Protocol）· `placeholder`
- `resource_estimation` — Resource estimation（资源估计）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/overlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 28 / 295 — `manual.protocols.derivatives`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / derivatives` |
| slug | `derivatives` |
| title_zh / en | 导数 Protocol / Derivative protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/derivative.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/derivatives/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `derivatives`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `statevector` — Statevector protocols（态向量 Protocol）· `partial`
- `averaging` — Averaging protocols（平均（Pauli）Protocol）· `shipped`
- `overlap` — Overlap protocols（重叠 / 投影 Protocol）· `placeholder`
- `phase_estimation` — Quantum phase estimation protocols（量子相位估计 Protocol）· `placeholder`
- `resource_estimation` — Resource estimation（资源估计）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/derivatives/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 29 / 295 — `manual.protocols.phase_estimation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / phase_estimation` |
| slug | `phase_estimation` |
| title_zh / en | 量子相位估计 Protocol / Quantum phase estimation protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/qpe.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/phase_estimation/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `phase_estimation`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `statevector` — Statevector protocols（态向量 Protocol）· `partial`
- `averaging` — Averaging protocols（平均（Pauli）Protocol）· `shipped`
- `overlap` — Overlap protocols（重叠 / 投影 Protocol）· `placeholder`
- `derivatives` — Derivative protocols（导数 Protocol）· `placeholder`
- `resource_estimation` — Resource estimation（资源估计）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.qpe_qec_demo`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/phase_estimation/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 30 / 295 — `manual.protocols.resource_estimation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / protocols / resource_estimation` |
| slug | `resource_estimation` |
| title_zh / en | 资源估计 / Resource estimation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/protocols/resource_estimation.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/protocols/resource_estimation/` |

- **L1 分区**: `manual` → **L2..n**: `protocols` → `resource_estimation`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉测量电路、Pauli 分解与 shots 语义。
- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `statevector` — Statevector protocols（态向量 Protocol）· `partial`
- `averaging` — Averaging protocols（平均（Pauli）Protocol）· `shipped`
- `overlap` — Overlap protocols（重叠 / 投影 Protocol）· `placeholder`
- `derivatives` — Derivative protocols（导数 Protocol）· `placeholder`
- `phase_estimation` — Quantum phase estimation protocols（量子相位估计 Protocol）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.PauliAveragingProtocol.dataframe_circuit_shot`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/protocols/resource_estimation/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 31 / 295 — `manual.algorithms`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms` |
| slug | `algorithms` |
| title_zh / en | Algorithms 概览 / Algorithms overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms_overview.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `embedding` — Embeddings and DMET（嵌入与 DMET）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 32 / 295 — `manual.algorithms.vqe`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms / vqe` |
| slug | `vqe` |
| title_zh / en | VQE / VQE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms/algorithms_vqe.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/vqe/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms` → `vqe`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `adapt` — ADAPT-VQE family（ADAPT-VQE 家族）· `partial`
- `excited` — Excited states (VQD / QSE / SCEOM)（激发态（VQD / QSE / SCEOM））· `partial`
- `qpe` — Quantum phase estimation algorithms（量子相位估计算法）· `placeholder`
- `time_evolution` — Time evolution (VQS / McLachlan)（时间演化（VQS / McLachlan））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.vqe`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/vqe/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 33 / 295 — `manual.algorithms.adapt`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms / adapt` |
| slug | `adapt` |
| title_zh / en | ADAPT-VQE 家族 / ADAPT-VQE family |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms/algorithms_adapt.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/adapt/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms` → `adapt`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `vqe` — VQE（VQE）· `shipped`
- `excited` — Excited states (VQD / QSE / SCEOM)（激发态（VQD / QSE / SCEOM））· `partial`
- `qpe` — Quantum phase estimation algorithms（量子相位估计算法）· `placeholder`
- `time_evolution` — Time evolution (VQS / McLachlan)（时间演化（VQS / McLachlan））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.adapt`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/adapt/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 34 / 295 — `manual.algorithms.excited`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms / excited` |
| slug | `excited` |
| title_zh / en | 激发态（VQD / QSE / SCEOM） / Excited states (VQD / QSE / SCEOM) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms/algorithms_excited.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/excited/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms` → `excited`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `vqe` — VQE（VQE）· `shipped`
- `adapt` — ADAPT-VQE family（ADAPT-VQE 家族）· `partial`
- `qpe` — Quantum phase estimation algorithms（量子相位估计算法）· `placeholder`
- `time_evolution` — Time evolution (VQS / McLachlan)（时间演化（VQS / McLachlan））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.excited`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/excited/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 35 / 295 — `manual.algorithms.qpe`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms / qpe` |
| slug | `qpe` |
| title_zh / en | 量子相位估计算法 / Quantum phase estimation algorithms |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms/algorithms_qpe.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/qpe/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms` → `qpe`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `vqe` — VQE（VQE）· `shipped`
- `adapt` — ADAPT-VQE family（ADAPT-VQE 家族）· `partial`
- `excited` — Excited states (VQD / QSE / SCEOM)（激发态（VQD / QSE / SCEOM））· `partial`
- `time_evolution` — Time evolution (VQS / McLachlan)（时间演化（VQS / McLachlan））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.qpe_qec_demo`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/qpe/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 36 / 295 — `manual.algorithms.time_evolution`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / algorithms / time_evolution` |
| slug | `time_evolution` |
| title_zh / en | 时间演化（VQS / McLachlan） / Time evolution (VQS / McLachlan) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/algorithms/te_vqs.html |
| pillar / diataxis / class_leaf | P2 / concept / no |
| mirror_path | `/mirror/manual/algorithms/time_evolution/` |

- **L1 分区**: `manual` → **L2..n**: `algorithms` → `time_evolution`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 熟悉变分量子算法与线性代数记号。
- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `vqe` — VQE（VQE）· `shipped`
- `adapt` — ADAPT-VQE family（ADAPT-VQE 家族）· `partial`
- `excited` — Excited states (VQD / QSE / SCEOM)（激发态（VQD / QSE / SCEOM））· `partial`
- `qpe` — Quantum phase estimation algorithms（量子相位估计算法）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/algorithms/time_evolution/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 37 / 295 — `manual.embedding`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / embedding` |
| slug | `embedding` |
| title_zh / en | 嵌入与 DMET / Embeddings and DMET |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/dmet.html |
| pillar / diataxis / class_leaf | P1 / concept / no |
| mirror_path | `/mirror/manual/embedding/` |

- **L1 分区**: `manual` → **L2..n**: `embedding`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 经典量子化学基础（HF、活性空间、分子几何）。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/embedding/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 38 / 295 — `manual.embedding.dmet_intro`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / embedding / dmet_intro` |
| slug | `dmet_intro` |
| title_zh / en | DMET 概览 / DMET overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/dmet.html |
| pillar / diataxis / class_leaf | P1 / concept / no |
| mirror_path | `/mirror/manual/embedding/dmet_intro/` |

- **L1 分区**: `manual` → **L2..n**: `embedding` → `dmet_intro`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 经典量子化学基础（HF、活性空间、分子几何）。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `projection_embedding` — Projection embedding（投影嵌入）· `partial`
- `nevpt2_ac0` — NEVPT2 / AC0 corrections（NEVPT2 / AC0 校正）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding.dmet`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/embedding/dmet_intro/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 39 / 295 — `manual.embedding.projection_embedding`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / embedding / projection_embedding` |
| slug | `projection_embedding` |
| title_zh / en | 投影嵌入 / Projection embedding |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/projection_embedding.html |
| pillar / diataxis / class_leaf | P1 / concept / no |
| mirror_path | `/mirror/manual/embedding/projection_embedding/` |

- **L1 分区**: `manual` → **L2..n**: `embedding` → `projection_embedding`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 经典量子化学基础（HF、活性空间、分子几何）。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `dmet_intro` — DMET overview（DMET 概览）· `partial`
- `nevpt2_ac0` — NEVPT2 / AC0 corrections（NEVPT2 / AC0 校正）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding.projection`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/embedding/projection_embedding/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 40 / 295 — `manual.embedding.nevpt2_ac0`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / embedding / nevpt2_ac0` |
| slug | `nevpt2_ac0` |
| title_zh / en | NEVPT2 / AC0 校正 / NEVPT2 / AC0 corrections |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/nevpt2.html |
| pillar / diataxis / class_leaf | P1 / concept / no |
| mirror_path | `/mirror/manual/embedding/nevpt2_ac0/` |

- **L1 分区**: `manual` → **L2..n**: `embedding` → `nevpt2_ac0`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 经典量子化学基础（HF、活性空间、分子几何）。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `dmet_intro` — DMET overview（DMET 概览）· `partial`
- `projection_embedding` — Projection embedding（投影嵌入）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/embedding/nevpt2_ac0/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 41 / 295 — `manual.noise_mitigation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / noise_mitigation` |
| slug | `noise_mitigation` |
| title_zh / en | 噪声缓解 / Noise mitigation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/errmit.html |
| pillar / diataxis / class_leaf | P3 / concept / no |
| mirror_path | `/mirror/manual/noise_mitigation/` |

- **L1 分区**: `manual` → **L2..n**: `noise_mitigation`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `howto` — Reference manual · How-to（参考手册 · 使用说明）· `shipped`
- `geometry` — Geometry（几何）· `partial`
- `express` — Express data sets（Express 数据集）· `partial`
- `symmetry` — Symmetry（对称性）· `placeholder`
- `spaces_operators` — Spaces, operators, states and mappings（空间 / 算符 / 状态 / 映射）· `partial`
- `ansatze` — Ansatze overview（Ansatze 概览）· `partial`
- `minimizers` — Minimizers（极小化器）· `partial`
- `computables` — Computables overview（Computables 概览）· `partial`
- `protocols` — Protocols overview (five stages)（Protocols 概览（五阶段））· `partial`
- `algorithms` — Algorithms overview（Algorithms 概览）· `partial`
- _… 另有 1 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.mitigation`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/noise_mitigation/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 42 / 295 — `manual.noise_mitigation.qermit`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / noise_mitigation / qermit` |
| slug | `qermit` |
| title_zh / en | Qermit MitRes / MitEx 集成 / Qermit MitRes / MitEx integration |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/errmit.html#using-qermit |
| pillar / diataxis / class_leaf | P3 / concept / no |
| mirror_path | `/mirror/manual/noise_mitigation/qermit/` |

- **L1 分区**: `manual` → **L2..n**: `noise_mitigation` → `qermit`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `pmsv_spam` — PMSV and SPAM（PMSV 与 SPAM）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.mitigation.qermit_analog`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/noise_mitigation/qermit/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 43 / 295 — `manual.noise_mitigation.pmsv_spam`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `manual / noise_mitigation / pmsv_spam` |
| slug | `pmsv_spam` |
| title_zh / en | PMSV 与 SPAM / PMSV and SPAM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/manual/errmit.html#using-inquanto-s-pmsv-and-spam |
| pillar / diataxis / class_leaf | P3 / concept / no |
| mirror_path | `/mirror/manual/noise_mitigation/pmsv_spam/` |

- **L1 分区**: `manual` → **L2..n**: `noise_mitigation` → `pmsv_spam`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `manual`
- **Diátaxis 标签（manifest）**: `concept` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。
- **典型入链**: introduction quickstart；tutorials 对应主题。

## 2. 同级兄弟（manifest 同父）

- `qermit` — Qermit MitRes / MitEx integration（Qermit MitRes / MitEx 集成）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.mitigation`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/manual/noise_mitigation/pmsv_spam/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 44 / 295 — `tutorials`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials` |
| slug | `tutorials` |
| title_zh / en | 教程 / Tutorials |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/tutorial_overview.html |
| pillar / diataxis / class_leaf | meta / tutorial / no |
| mirror_path | `/mirror/tutorials/` |

- **L1 分区**: `tutorials` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/`
- **四柱指南**: `/guide/` 总览 + `/product/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 45 / 295 — `tutorials.core`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / core` |
| slug | `core` |
| title_zh / en | 核心教程 / Core tutorials |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/tutorial_overview.html#core-tutorials |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/tutorials/core/` |

- **L1 分区**: `tutorials` → **L2..n**: `core`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends` — Backend tutorials（后端教程）· `partial`
- `case_study_fe4n2` — Fe4N2 case study（Fe4N2 案例研究）· `placeholder`
- `fragmentation` — Fragmentation tutorials（碎片化教程）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/core/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 46 / 295 — `tutorials.core.basic_vqe`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / core / basic_vqe` |
| slug | `basic_vqe` |
| title_zh / en | 基础 VQE / A basic VQE simulation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_VQE.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/tutorials/core/basic_vqe/` |

- **L1 分区**: `tutorials` → **L2..n**: `core` → `basic_vqe`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `extended_vqe` — Extended VQE（扩展 VQE）· `partial`
- `vqd` — Variational quantum deflation for excited states（激发态 VQD）· `partial`
- `nglview` — Visualization with NGLView (reference)（nglview 可视化）· `not-applicable`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.express`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/core/basic_vqe/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 47 / 295 — `tutorials.core.extended_vqe`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / core / extended_vqe` |
| slug | `extended_vqe` |
| title_zh / en | 扩展 VQE / Extended VQE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_VQE_extended.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/tutorials/core/extended_vqe/` |

- **L1 分区**: `tutorials` → **L2..n**: `core` → `extended_vqe`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `basic_vqe` — A basic VQE simulation（基础 VQE）· `shipped`
- `vqd` — Variational quantum deflation for excited states（激发态 VQD）· `partial`
- `nglview` — Visualization with NGLView (reference)（nglview 可视化）· `not-applicable`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/core/extended_vqe/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 48 / 295 — `tutorials.core.vqd`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / core / vqd` |
| slug | `vqd` |
| title_zh / en | 激发态 VQD / Variational quantum deflation for excited states |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_VQD.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/tutorials/core/vqd/` |

- **L1 分区**: `tutorials` → **L2..n**: `core` → `vqd`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `basic_vqe` — A basic VQE simulation（基础 VQE）· `shipped`
- `extended_vqe` — Extended VQE（扩展 VQE）· `partial`
- `nglview` — Visualization with NGLView (reference)（nglview 可视化）· `not-applicable`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.excited`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/core/vqd/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 49 / 295 — `tutorials.core.nglview`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / core / nglview` |
| slug | `nglview` |
| title_zh / en | nglview 可视化 / Visualization with NGLView (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_nglview.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/tutorials/core/nglview/` |

- **L1 分区**: `tutorials` → **L2..n**: `core` → `nglview`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `basic_vqe` — A basic VQE simulation（基础 VQE）· `shipped`
- `extended_vqe` — Extended VQE（扩展 VQE）· `partial`
- `vqd` — Variational quantum deflation for excited states（激发态 VQD）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 不打包闭源可视化扩展。
- **reason_en**: We do not bundle the closed-source visualization extension.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/core/nglview/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 50 / 295 — `tutorials.backends`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends` |
| slug | `backends` |
| title_zh / en | 后端教程 / Backend tutorials |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/tutorial_overview.html#backend-tutorials |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `core` — Core tutorials（核心教程）· `partial`
- `case_study_fe4n2` — Fe4N2 case study（Fe4N2 案例研究）· `placeholder`
- `fragmentation` — Fragmentation tutorials（碎片化教程）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 51 / 295 — `tutorials.backends.backends_setup`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / backends_setup` |
| slug | `backends_setup` |
| title_zh / en | 后端搭建 / Setting up and accessing backends |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_backends.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/backends_setup/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `backends_setup`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `async` — Running asynchronous experiments（异步实验）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.backends`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/backends_setup/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 52 / 295 — `tutorials.backends.nexus_intro`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / nexus_intro` |
| slug | `nexus_intro` |
| title_zh / en | Nexus 后端管理 / Accessing and managing backends with Nexus |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_nexus.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/nexus_intro/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `nexus_intro`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `async` — Running asynchronous experiments（异步实验）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.api`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 不实现 Nexus 真云；提供本地 SQLite 类比。
- **reason_en**: No real Nexus integration; we provide a local SQLite analog.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/nexus_intro/`
- **四柱指南**: `/guide/execution-and-analysis/`
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 53 / 295 — `tutorials.backends.helios_selene`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / helios_selene` |
| slug | `helios_selene` |
| title_zh / en | Helios / Selene 后端提交（参考教程） / Helios / Selene backend submission (reference tutorial) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_helios.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/helios_selene/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `helios_selene`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `async` — Running asynchronous experiments（异步实验）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 不接入 H 系硬件。
- **reason_en**: H-Series hardware not in scope.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/helios_selene/`
- **四柱指南**: `/guide/execution-and-analysis/`
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 54 / 295 — `tutorials.backends.aer_shots`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / aer_shots` |
| slug | `aer_shots` |
| title_zh / en | Aer 采样（shots） / Hamiltonian averaging with the Aer simulator (shots) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_qiskit_shots.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/aer_shots/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `aer_shots`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `async` — Running asynchronous experiments（异步实验）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.backends.qiskit_pauli_shots`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/aer_shots/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 55 / 295 — `tutorials.backends.circuit_compilation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / circuit_compilation` |
| slug | `circuit_compilation` |
| title_zh / en | 电路编译流水线 / Circuit compilation in protocols workflow |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_compilation.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/circuit_compilation/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `circuit_compilation`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `async` — Running asynchronous experiments（异步实验）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.backends.compile_passes`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/circuit_compilation/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 56 / 295 — `tutorials.backends.async`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / async` |
| slug | `async` |
| title_zh / en | 异步实验 / Running asynchronous experiments |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_async.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/async/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `async`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `qse_quantinuum` — QSE on hardware backends (reference tutorial)（QSE 硬件后端教程（参考））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.jobs.store`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/async/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 57 / 295 — `tutorials.backends.qse_quantinuum`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / backends / qse_quantinuum` |
| slug | `qse_quantinuum` |
| title_zh / en | QSE 硬件后端教程（参考） / QSE on hardware backends (reference tutorial) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_qse.html |
| pillar / diataxis / class_leaf | P3 / tutorial / no |
| mirror_path | `/mirror/tutorials/backends/qse_quantinuum/` |

- **L1 分区**: `tutorials` → **L2..n**: `backends` → `qse_quantinuum`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `backends_setup` — Setting up and accessing backends（后端搭建）· `shipped`
- `nexus_intro` — Accessing and managing backends with Nexus（Nexus 后端管理）· `not-applicable`
- `helios_selene` — Helios / Selene backend submission (reference tutorial)（Helios / Selene 后端提交（参考教程））· `not-applicable`
- `aer_shots` — Hamiltonian averaging with the Aer simulator (shots)（Aer 采样（shots））· `shipped`
- `circuit_compilation` — Circuit compilation in protocols workflow（电路编译流水线）· `partial`
- `async` — Running asynchronous experiments（异步实验）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/backends/qse_quantinuum/`
- **四柱指南**: `/guide/execution-and-analysis/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 58 / 295 — `tutorials.case_study_fe4n2`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / case_study_fe4n2` |
| slug | `case_study_fe4n2` |
| title_zh / en | Fe4N2 案例研究 / Fe4N2 case study |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/tutorial_overview.html#case-study-tutorials-fe4n2 |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/case_study_fe4n2/` |

- **L1 分区**: `tutorials` → **L2..n**: `case_study_fe4n2`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `core` — Core tutorials（核心教程）· `partial`
- `backends` — Backend tutorials（后端教程）· `partial`
- `fragmentation` — Fragmentation tutorials（碎片化教程）· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/case_study_fe4n2/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 59 / 295 — `tutorials.case_study_fe4n2.fe4n2_avas_casscf`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / case_study_fe4n2 / fe4n2_avas_casscf` |
| slug | `fe4n2_avas_casscf` |
| title_zh / en | Fe4N2：AVAS + CASSCF / Fe4N2 — AVAS + CASSCF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_1.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/case_study_fe4n2/fe4n2_avas_casscf/` |

- **L1 分区**: `tutorials` → **L2..n**: `case_study_fe4n2` → `fe4n2_avas_casscf`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `fe4n2_adapt` — Fe4N2 — ADAPT efficient circuits（Fe4N2：ADAPT 构造高效线路）· `placeholder`
- `fe4n2_hardware` — Fe4N2 — running on noisy hardware（Fe4N2：噪声硬件评估）· `not-applicable`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/case_study_fe4n2/fe4n2_avas_casscf/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 60 / 295 — `tutorials.case_study_fe4n2.fe4n2_adapt`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / case_study_fe4n2 / fe4n2_adapt` |
| slug | `fe4n2_adapt` |
| title_zh / en | Fe4N2：ADAPT 构造高效线路 / Fe4N2 — ADAPT efficient circuits |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_2.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/case_study_fe4n2/fe4n2_adapt/` |

- **L1 分区**: `tutorials` → **L2..n**: `case_study_fe4n2` → `fe4n2_adapt`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `fe4n2_avas_casscf` — Fe4N2 — AVAS + CASSCF（Fe4N2：AVAS + CASSCF）· `placeholder`
- `fe4n2_hardware` — Fe4N2 — running on noisy hardware（Fe4N2：噪声硬件评估）· `not-applicable`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/case_study_fe4n2/fe4n2_adapt/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 61 / 295 — `tutorials.case_study_fe4n2.fe4n2_hardware`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / case_study_fe4n2 / fe4n2_hardware` |
| slug | `fe4n2_hardware` |
| title_zh / en | Fe4N2：噪声硬件评估 / Fe4N2 — running on noisy hardware |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_3.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/case_study_fe4n2/fe4n2_hardware/` |

- **L1 分区**: `tutorials` → **L2..n**: `case_study_fe4n2` → `fe4n2_hardware`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `fe4n2_avas_casscf` — Fe4N2 — AVAS + CASSCF（Fe4N2：AVAS + CASSCF）· `placeholder`
- `fe4n2_adapt` — Fe4N2 — ADAPT efficient circuits（Fe4N2：ADAPT 构造高效线路）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/case_study_fe4n2/fe4n2_hardware/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 62 / 295 — `tutorials.fragmentation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / fragmentation` |
| slug | `fragmentation` |
| title_zh / en | 碎片化教程 / Fragmentation tutorials |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/tutorial_overview.html#fragmentation-tutorials |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/fragmentation/` |

- **L1 分区**: `tutorials` → **L2..n**: `fragmentation`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `core` — Core tutorials（核心教程）· `partial`
- `backends` — Backend tutorials（后端教程）· `partial`
- `case_study_fe4n2` — Fe4N2 case study（Fe4N2 案例研究）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/fragmentation/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 63 / 295 — `tutorials.fragmentation.dmet_basic`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / fragmentation / dmet_basic` |
| slug | `dmet_basic` |
| title_zh / en | 大体系 DMET 入门 / Tackling larger systems with fragmentation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_dmet.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/fragmentation/dmet_basic/` |

- **L1 分区**: `tutorials` → **L2..n**: `fragmentation` → `dmet_basic`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `projection_embedding` — Projection-based embedding（投影嵌入）· `partial`
- `nevpt2_ac0` — NEVPT2 + AC0 corrections（NEVPT2 + AC0 校正）· `placeholder`
- `wft_dft` — WFT-in-DFT + NEVPT2 or AC0（WFT-in-DFT + NEVPT2 / AC0）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding.dmet`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/fragmentation/dmet_basic/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 64 / 295 — `tutorials.fragmentation.projection_embedding`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / fragmentation / projection_embedding` |
| slug | `projection_embedding` |
| title_zh / en | 投影嵌入 / Projection-based embedding |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_projection.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/fragmentation/projection_embedding/` |

- **L1 分区**: `tutorials` → **L2..n**: `fragmentation` → `projection_embedding`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `dmet_basic` — Tackling larger systems with fragmentation（大体系 DMET 入门）· `partial`
- `nevpt2_ac0` — NEVPT2 + AC0 corrections（NEVPT2 + AC0 校正）· `placeholder`
- `wft_dft` — WFT-in-DFT + NEVPT2 or AC0（WFT-in-DFT + NEVPT2 / AC0）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding.projection`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/fragmentation/projection_embedding/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 65 / 295 — `tutorials.fragmentation.nevpt2_ac0`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / fragmentation / nevpt2_ac0` |
| slug | `nevpt2_ac0` |
| title_zh / en | NEVPT2 + AC0 校正 / NEVPT2 + AC0 corrections |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_nevpt2_AC0.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/fragmentation/nevpt2_ac0/` |

- **L1 分区**: `tutorials` → **L2..n**: `fragmentation` → `nevpt2_ac0`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `dmet_basic` — Tackling larger systems with fragmentation（大体系 DMET 入门）· `partial`
- `projection_embedding` — Projection-based embedding（投影嵌入）· `partial`
- `wft_dft` — WFT-in-DFT + NEVPT2 or AC0（WFT-in-DFT + NEVPT2 / AC0）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/fragmentation/nevpt2_ac0/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 66 / 295 — `tutorials.fragmentation.wft_dft`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `tutorials / fragmentation / wft_dft` |
| slug | `wft_dft` |
| title_zh / en | WFT-in-DFT + NEVPT2 / AC0 / WFT-in-DFT + NEVPT2 or AC0 |
| reference_doc_url | https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_wft_dft_2.html |
| pillar / diataxis / class_leaf | P1 / tutorial / no |
| mirror_path | `/mirror/tutorials/fragmentation/wft_dft/` |

- **L1 分区**: `tutorials` → **L2..n**: `fragmentation` → `wft_dft`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `tutorials`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。
- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。
- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。

## 2. 同级兄弟（manifest 同父）

- `dmet_basic` — Tackling larger systems with fragmentation（大体系 DMET 入门）· `partial`
- `projection_embedding` — Projection-based embedding（投影嵌入）· `partial`
- `nevpt2_ac0` — NEVPT2 + AC0 corrections（NEVPT2 + AC0 校正）· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/tutorials/fragmentation/wft_dft/`
- **四柱指南**: `/guide/chemistry-and-embedding/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 67 / 295 — `extensions`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions` |
| slug | `extensions` |
| title_zh / en | 扩展 / Extensions |
| reference_doc_url | https://docs.quantinuum.com/inquanto/extensions/extensions-overview.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/extensions/` |

- **L1 分区**: `extensions` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 68 / 295 — `extensions.inquanto_pyscf`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions / inquanto_pyscf` |
| slug | `inquanto_pyscf` |
| title_zh / en | PySCF 扩展（参考文档） / PySCF extension (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/extensions/inquanto-pyscf.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/extensions/inquanto_pyscf/` |

- **L1 分区**: `extensions` → **L2..n**: `inquanto_pyscf`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

- `inquanto_nexus` — Nexus integration (reference)（Nexus 集成（参考文档））· `not-applicable`
- `inquanto_nglview` — NGLView visualization (reference)（NGLView 可视化（参考文档））· `not-applicable`
- `inquanto_phayes` — Phayes extension (reference)（Phayes 扩展（参考文档））· `placeholder`
- `inquanto_cutensornet` — cuTensorNet extension (reference)（cuTensorNet 扩展（参考文档））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.drivers.pyscf_driver`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/inquanto_pyscf/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 69 / 295 — `extensions.inquanto_nexus`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions / inquanto_nexus` |
| slug | `inquanto_nexus` |
| title_zh / en | Nexus 集成（参考文档） / Nexus integration (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/extensions/inquanto-nexus.html |
| pillar / diataxis / class_leaf | P4 / reference / no |
| mirror_path | `/mirror/extensions/inquanto_nexus/` |

- **L1 分区**: `extensions` → **L2..n**: `inquanto_nexus`
- **Primary**: 平台与 DevOps（作业队列、API、可复现导出）
- **Secondary**: 合作方尽调 / 合规读者
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

- `inquanto_pyscf` — PySCF extension (reference)（PySCF 扩展（参考文档））· `partial`
- `inquanto_nglview` — NGLView visualization (reference)（NGLView 可视化（参考文档））· `not-applicable`
- `inquanto_phayes` — Phayes extension (reference)（Phayes 扩展（参考文档））· `placeholder`
- `inquanto_cutensornet` — cuTensorNet extension (reference)（cuTensorNet 扩展（参考文档））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.api`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 真云 / HQC / OAuth / 配额不在范围；提供本地 FastAPI 类比。
- **reason_en**: Real cloud / HQC / OAuth / quota not in scope; we provide a local FastAPI analog.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/inquanto_nexus/`
- **四柱指南**: `/guide/jobs-and-reproducibility/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。
- **P4**: `GET/POST /v1/runs`、`repro` 须有 **API 表或控制台等价说明**。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 70 / 295 — `extensions.inquanto_nglview`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions / inquanto_nglview` |
| slug | `inquanto_nglview` |
| title_zh / en | NGLView 可视化（参考文档） / NGLView visualization (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/extensions/inquanto-nglview.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/extensions/inquanto_nglview/` |

- **L1 分区**: `extensions` → **L2..n**: `inquanto_nglview`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

- `inquanto_pyscf` — PySCF extension (reference)（PySCF 扩展（参考文档））· `partial`
- `inquanto_nexus` — Nexus integration (reference)（Nexus 集成（参考文档））· `not-applicable`
- `inquanto_phayes` — Phayes extension (reference)（Phayes 扩展（参考文档））· `placeholder`
- `inquanto_cutensornet` — cuTensorNet extension (reference)（cuTensorNet 扩展（参考文档））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 我们不绑定闭源可视化包，留给上层应用自行接入 nglview/py3Dmol。
- **reason_en**: We do not bundle closed-source visualization; downstream apps may use nglview/py3Dmol directly.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/inquanto_nglview/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 71 / 295 — `extensions.inquanto_phayes`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions / inquanto_phayes` |
| slug | `inquanto_phayes` |
| title_zh / en | Phayes 扩展（参考文档） / Phayes extension (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/extensions/inquanto-phayes.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/extensions/inquanto_phayes/` |

- **L1 分区**: `extensions` → **L2..n**: `inquanto_phayes`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

- `inquanto_pyscf` — PySCF extension (reference)（PySCF 扩展（参考文档））· `partial`
- `inquanto_nexus` — Nexus integration (reference)（Nexus 集成（参考文档））· `not-applicable`
- `inquanto_nglview` — NGLView visualization (reference)（NGLView 可视化（参考文档））· `not-applicable`
- `inquanto_cutensornet` — cuTensorNet extension (reference)（cuTensorNet 扩展（参考文档））· `partial`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.qpe_qec_demo.bayesian_stub`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/inquanto_phayes/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 72 / 295 — `extensions.inquanto_cutensornet`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `extensions / inquanto_cutensornet` |
| slug | `inquanto_cutensornet` |
| title_zh / en | cuTensorNet 扩展（参考文档） / cuTensorNet extension (reference) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-cutensornet_api.html |
| pillar / diataxis / class_leaf | P3 / reference / no |
| mirror_path | `/mirror/extensions/inquanto_cutensornet/` |

- **L1 分区**: `extensions` → **L2..n**: `inquanto_cutensornet`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `extensions`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。
- **典型入链**: manual「驱动」叙事；quickstart。

## 2. 同级兄弟（manifest 同父）

- `inquanto_pyscf` — PySCF extension (reference)（PySCF 扩展（参考文档））· `partial`
- `inquanto_nexus` — Nexus integration (reference)（Nexus 集成（参考文档））· `not-applicable`
- `inquanto_nglview` — NGLView visualization (reference)（NGLView 可视化（参考文档））· `not-applicable`
- `inquanto_phayes` — Phayes extension (reference)（Phayes 扩展（参考文档））· `placeholder`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.tensornet`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/extensions/inquanto_cutensornet/`
- **四柱指南**: `/guide/execution-and-analysis/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 73 / 295 — `api`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api` |
| slug | `api` |
| title_zh / en | API 参考 / API reference |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/api/` |

- **L1 分区**: `api` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 74 / 295 — `api.api_intro_inquanto`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / api_intro_inquanto` |
| slug | `api_intro_inquanto` |
| title_zh / en | 参考文档 · API 总览 / Reference documentation · API overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto_api_intro.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/api/api_intro_inquanto/` |

- **L1 分区**: `api` → **L2..n**: `api_intro_inquanto`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/api_intro_inquanto/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 75 / 295 — `api.api_intro_extensions`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / api_intro_extensions` |
| slug | `api_intro_extensions` |
| title_zh / en | 参考文档 · 扩展 API 总览 / Reference documentation · Extensions API overview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto-ext_api_intro.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/api/api_intro_extensions/` |

- **L1 分区**: `api` → **L2..n**: `api_intro_extensions`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/api_intro_extensions/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 76 / 295 — `api.algorithms`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms` |
| slug | `algorithms` |
| title_zh / en | 参考 API · inquanto.algorithms / Reference API · inquanto.algorithms |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/algorithms/` |

- **L1 分区**: `api` → **L2..n**: `algorithms`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 77 / 295 — `api.algorithms.classes.AlgorithmVQE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmVQE` |
| slug | `AlgorithmVQE` |
| title_zh / en | AlgorithmVQE / AlgorithmVQE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmVQE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmVQE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmVQE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.vqe`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmVQE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 78 / 295 — `api.algorithms.classes.AlgorithmAdaptVQE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmAdaptVQE` |
| slug | `AlgorithmAdaptVQE` |
| title_zh / en | AlgorithmAdaptVQE / AlgorithmAdaptVQE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmAdaptVQE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmAdaptVQE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmAdaptVQE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.adapt`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmAdaptVQE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 79 / 295 — `api.algorithms.classes.AlgorithmFermionicAdaptVQE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmFermionicAdaptVQE` |
| slug | `AlgorithmFermionicAdaptVQE` |
| title_zh / en | AlgorithmFermionicAdaptVQE / AlgorithmFermionicAdaptVQE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmFermionicAdaptVQE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmFermionicAdaptVQE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmFermionicAdaptVQE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.adapt`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmFermionicAdaptVQE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 80 / 295 — `api.algorithms.classes.AlgorithmIQEB`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmIQEB` |
| slug | `AlgorithmIQEB` |
| title_zh / en | AlgorithmIQEB / AlgorithmIQEB |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmIQEB |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmIQEB/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmIQEB`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.iqeb`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmIQEB/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 81 / 295 — `api.algorithms.classes.AlgorithmVQD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmVQD` |
| slug | `AlgorithmVQD` |
| title_zh / en | AlgorithmVQD / AlgorithmVQD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmVQD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmVQD/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmVQD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.excited`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmVQD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 82 / 295 — `api.algorithms.classes.AlgorithmQSE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmQSE` |
| slug | `AlgorithmQSE` |
| title_zh / en | AlgorithmQSE / AlgorithmQSE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmQSE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmQSE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmQSE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.qse_transition`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmQSE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 83 / 295 — `api.algorithms.classes.AlgorithmSCEOM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmSCEOM` |
| slug | `AlgorithmSCEOM` |
| title_zh / en | AlgorithmSCEOM / AlgorithmSCEOM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmSCEOM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmSCEOM/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmSCEOM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.algorithms.sceom`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmSCEOM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 84 / 295 — `api.algorithms.classes.AlgorithmDeterministicQPE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmDeterministicQPE` |
| slug | `AlgorithmDeterministicQPE` |
| title_zh / en | AlgorithmDeterministicQPE / AlgorithmDeterministicQPE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmDeterministicQPE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmDeterministicQPE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmDeterministicQPE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmDeterministicQPE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 85 / 295 — `api.algorithms.classes.AlgorithmInfoTheoryQPE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmInfoTheoryQPE` |
| slug | `AlgorithmInfoTheoryQPE` |
| title_zh / en | AlgorithmInfoTheoryQPE / AlgorithmInfoTheoryQPE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmInfoTheoryQPE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmInfoTheoryQPE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmInfoTheoryQPE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmInfoTheoryQPE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 86 / 295 — `api.algorithms.classes.AlgorithmKitaevQPE`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmKitaevQPE` |
| slug | `AlgorithmKitaevQPE` |
| title_zh / en | AlgorithmKitaevQPE / AlgorithmKitaevQPE |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmKitaevQPE |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmKitaevQPE/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmKitaevQPE`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmVQS` — AlgorithmVQS（AlgorithmVQS）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmKitaevQPE/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 87 / 295 — `api.algorithms.classes.AlgorithmVQS`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmVQS` |
| slug | `AlgorithmVQS` |
| title_zh / en | AlgorithmVQS / AlgorithmVQS |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmVQS |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmVQS/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmVQS`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmVQS/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 88 / 295 — `api.algorithms.classes.AlgorithmMcLachlanRealTime`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmMcLachlanRealTime` |
| slug | `AlgorithmMcLachlanRealTime` |
| title_zh / en | AlgorithmMcLachlanRealTime / AlgorithmMcLachlanRealTime |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmMcLachlanRealTime |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmMcLachlanRealTime/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmMcLachlanRealTime`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmMcLachlanRealTime/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 89 / 295 — `api.algorithms.classes.AlgorithmMcLachlanImagTime`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / algorithms / classes / AlgorithmMcLachlanImagTime` |
| slug | `AlgorithmMcLachlanImagTime` |
| title_zh / en | AlgorithmMcLachlanImagTime / AlgorithmMcLachlanImagTime |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html#inquanto.algorithms.AlgorithmMcLachlanImagTime |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/algorithms/classes/AlgorithmMcLachlanImagTime/` |

- **L1 分区**: `api` → **L2..n**: `algorithms` → `classes` → `AlgorithmMcLachlanImagTime`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AlgorithmVQE` — AlgorithmVQE（AlgorithmVQE）· `shipped` · class-leaf
- `AlgorithmAdaptVQE` — AlgorithmAdaptVQE（AlgorithmAdaptVQE）· `partial` · class-leaf
- `AlgorithmFermionicAdaptVQE` — AlgorithmFermionicAdaptVQE（AlgorithmFermionicAdaptVQE）· `partial` · class-leaf
- `AlgorithmIQEB` — AlgorithmIQEB（AlgorithmIQEB）· `partial` · class-leaf
- `AlgorithmVQD` — AlgorithmVQD（AlgorithmVQD）· `partial` · class-leaf
- `AlgorithmQSE` — AlgorithmQSE（AlgorithmQSE）· `partial` · class-leaf
- `AlgorithmSCEOM` — AlgorithmSCEOM（AlgorithmSCEOM）· `partial` · class-leaf
- `AlgorithmDeterministicQPE` — AlgorithmDeterministicQPE（AlgorithmDeterministicQPE）· `placeholder` · class-leaf
- `AlgorithmInfoTheoryQPE` — AlgorithmInfoTheoryQPE（AlgorithmInfoTheoryQPE）· `placeholder` · class-leaf
- `AlgorithmKitaevQPE` — AlgorithmKitaevQPE（AlgorithmKitaevQPE）· `placeholder` · class-leaf
- _… 另有 2 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/algorithms/classes/AlgorithmMcLachlanImagTime/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 90 / 295 — `api.ansatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz` |
| slug | `ansatz` |
| title_zh / en | 参考 API · inquanto.ansatzes / Reference API · inquanto.ansatzes |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/ansatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.ansatze`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 91 / 295 — `api.ansatz.classes.GeneralAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / GeneralAnsatz` |
| slug | `GeneralAnsatz` |
| title_zh / en | GeneralAnsatz / GeneralAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.GeneralAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/GeneralAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `GeneralAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/GeneralAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 92 / 295 — `api.ansatz.classes.CircuitAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / CircuitAnsatz` |
| slug | `CircuitAnsatz` |
| title_zh / en | CircuitAnsatz / CircuitAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.CircuitAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/CircuitAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `CircuitAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/CircuitAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 93 / 295 — `api.ansatz.classes.ComposedAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / ComposedAnsatz` |
| slug | `ComposedAnsatz` |
| title_zh / en | ComposedAnsatz / ComposedAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.ComposedAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/ComposedAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `ComposedAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/ComposedAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 94 / 295 — `api.ansatz.classes.TrotterAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / TrotterAnsatz` |
| slug | `TrotterAnsatz` |
| title_zh / en | TrotterAnsatz / TrotterAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.TrotterAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/TrotterAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `TrotterAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/TrotterAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 95 / 295 — `api.ansatz.classes.FermionSpaceStateExp`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceStateExp` |
| slug | `FermionSpaceStateExp` |
| title_zh / en | FermionSpaceStateExp / FermionSpaceStateExp |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceStateExp |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceStateExp/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceStateExp`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceStateExp/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 96 / 295 — `api.ansatz.classes.FermionSpaceAnsatzUCCSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzUCCSD` |
| slug | `FermionSpaceAnsatzUCCSD` |
| title_zh / en | FermionSpaceAnsatzUCCSD / FermionSpaceAnsatzUCCSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzUCCSD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCSD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzUCCSD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCSD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 97 / 295 — `api.ansatz.classes.FermionSpaceAnsatzUCCD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzUCCD` |
| slug | `FermionSpaceAnsatzUCCD` |
| title_zh / en | FermionSpaceAnsatzUCCD / FermionSpaceAnsatzUCCD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzUCCD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzUCCD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 98 / 295 — `api.ansatz.classes.FermionSpaceStateExpChemicallyAware`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceStateExpChemicallyAware` |
| slug | `FermionSpaceStateExpChemicallyAware` |
| title_zh / en | FermionSpaceStateExpChemicallyAware / FermionSpaceStateExpChemicallyAware |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceStateExpChemicallyAware |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceStateExpChemicallyAware/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceStateExpChemicallyAware`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceStateExpChemicallyAware/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 99 / 295 — `api.ansatz.classes.FermionSpaceAnsatzChemicallyAwareUCCSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzChemicallyAwareUCCSD` |
| slug | `FermionSpaceAnsatzChemicallyAwareUCCSD` |
| title_zh / en | FermionSpaceAnsatzChemicallyAwareUCCSD / FermionSpaceAnsatzChemicallyAwareUCCSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzChemicallyAwareUCCSD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzChemicallyAwareUCCSD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzChemicallyAwareUCCSD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzChemicallyAwareUCCSD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 100 / 295 — `api.ansatz.classes.FermionSpaceAnsatzkUpCCGD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzkUpCCGD` |
| slug | `FermionSpaceAnsatzkUpCCGD` |
| title_zh / en | FermionSpaceAnsatzkUpCCGD / FermionSpaceAnsatzkUpCCGD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzkUpCCGD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzkUpCCGD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGSD` — FermionSpaceAnsatzkUpCCGSD（FermionSpaceAnsatzkUpCCGSD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 101 / 295 — `api.ansatz.classes.FermionSpaceAnsatzkUpCCGSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzkUpCCGSD` |
| slug | `FermionSpaceAnsatzkUpCCGSD` |
| title_zh / en | FermionSpaceAnsatzkUpCCGSD / FermionSpaceAnsatzkUpCCGSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzkUpCCGSD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGSD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzkUpCCGSD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGSD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 102 / 295 — `api.ansatz.classes.FermionSpaceAnsatzkUpCCGSDSinglet`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzkUpCCGSDSinglet` |
| slug | `FermionSpaceAnsatzkUpCCGSDSinglet` |
| title_zh / en | FermionSpaceAnsatzkUpCCGSDSinglet / FermionSpaceAnsatzkUpCCGSDSinglet |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzkUpCCGSDSinglet |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGSDSinglet/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzkUpCCGSDSinglet`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzkUpCCGSDSinglet/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 103 / 295 — `api.ansatz.classes.FermionSpaceAnsatzUCCGD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzUCCGD` |
| slug | `FermionSpaceAnsatzUCCGD` |
| title_zh / en | FermionSpaceAnsatzUCCGD / FermionSpaceAnsatzUCCGD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzUCCGD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCGD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzUCCGD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCGD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 104 / 295 — `api.ansatz.classes.FermionSpaceAnsatzUCCGSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzUCCGSD` |
| slug | `FermionSpaceAnsatzUCCGSD` |
| title_zh / en | FermionSpaceAnsatzUCCGSD / FermionSpaceAnsatzUCCGSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzUCCGSD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCGSD/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzUCCGSD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCGSD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 105 / 295 — `api.ansatz.classes.FermionSpaceAnsatzUCCSDSinglet`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzUCCSDSinglet` |
| slug | `FermionSpaceAnsatzUCCSDSinglet` |
| title_zh / en | FermionSpaceAnsatzUCCSDSinglet / FermionSpaceAnsatzUCCSDSinglet |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzUCCSDSinglet |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCSDSinglet/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzUCCSDSinglet`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzUCCSDSinglet/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 106 / 295 — `api.ansatz.classes.FermionSpaceAnsatzsUPS`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatzsUPS` |
| slug | `FermionSpaceAnsatzsUPS` |
| title_zh / en | FermionSpaceAnsatzsUPS / FermionSpaceAnsatzsUPS |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatzsUPS |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatzsUPS/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatzsUPS`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatzsUPS/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 107 / 295 — `api.ansatz.classes.FermionSpaceAnsatztUPS`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / FermionSpaceAnsatztUPS` |
| slug | `FermionSpaceAnsatztUPS` |
| title_zh / en | FermionSpaceAnsatztUPS / FermionSpaceAnsatztUPS |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.FermionSpaceAnsatztUPS |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/FermionSpaceAnsatztUPS/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `FermionSpaceAnsatztUPS`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/FermionSpaceAnsatztUPS/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 108 / 295 — `api.ansatz.classes.MultiConfigurationAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / MultiConfigurationAnsatz` |
| slug | `MultiConfigurationAnsatz` |
| title_zh / en | MultiConfigurationAnsatz / MultiConfigurationAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.MultiConfigurationAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/MultiConfigurationAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `MultiConfigurationAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/MultiConfigurationAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 109 / 295 — `api.ansatz.classes.MultiConfigurationState`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / MultiConfigurationState` |
| slug | `MultiConfigurationState` |
| title_zh / en | MultiConfigurationState / MultiConfigurationState |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.MultiConfigurationState |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/MultiConfigurationState/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `MultiConfigurationState`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/MultiConfigurationState/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 110 / 295 — `api.ansatz.classes.MultiConfigurationStateBox`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / MultiConfigurationStateBox` |
| slug | `MultiConfigurationStateBox` |
| title_zh / en | MultiConfigurationStateBox / MultiConfigurationStateBox |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.MultiConfigurationStateBox |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/MultiConfigurationStateBox/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `MultiConfigurationStateBox`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/MultiConfigurationStateBox/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 111 / 295 — `api.ansatz.classes.MultiConfigurationAnsatzSparse`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / MultiConfigurationAnsatzSparse` |
| slug | `MultiConfigurationAnsatzSparse` |
| title_zh / en | MultiConfigurationAnsatzSparse / MultiConfigurationAnsatzSparse |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.MultiConfigurationAnsatzSparse |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/MultiConfigurationAnsatzSparse/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `MultiConfigurationAnsatzSparse`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/MultiConfigurationAnsatzSparse/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 112 / 295 — `api.ansatz.classes.MultiConfigurationStateSparse`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / MultiConfigurationStateSparse` |
| slug | `MultiConfigurationStateSparse` |
| title_zh / en | MultiConfigurationStateSparse / MultiConfigurationStateSparse |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.MultiConfigurationStateSparse |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/MultiConfigurationStateSparse/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `MultiConfigurationStateSparse`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/MultiConfigurationStateSparse/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 113 / 295 — `api.ansatz.classes.RealGeneralizedBasisRotationAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / RealGeneralizedBasisRotationAnsatz` |
| slug | `RealGeneralizedBasisRotationAnsatz` |
| title_zh / en | RealGeneralizedBasisRotationAnsatz / RealGeneralizedBasisRotationAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.RealGeneralizedBasisRotationAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/RealGeneralizedBasisRotationAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `RealGeneralizedBasisRotationAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/RealGeneralizedBasisRotationAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 114 / 295 — `api.ansatz.classes.RealRestrictedBasisRotationAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / RealRestrictedBasisRotationAnsatz` |
| slug | `RealRestrictedBasisRotationAnsatz` |
| title_zh / en | RealRestrictedBasisRotationAnsatz / RealRestrictedBasisRotationAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.RealRestrictedBasisRotationAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/RealRestrictedBasisRotationAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `RealRestrictedBasisRotationAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/RealRestrictedBasisRotationAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 115 / 295 — `api.ansatz.classes.RealUnrestrictedBasisRotationAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / RealUnrestrictedBasisRotationAnsatz` |
| slug | `RealUnrestrictedBasisRotationAnsatz` |
| title_zh / en | RealUnrestrictedBasisRotationAnsatz / RealUnrestrictedBasisRotationAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.RealUnrestrictedBasisRotationAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/RealUnrestrictedBasisRotationAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `RealUnrestrictedBasisRotationAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/RealUnrestrictedBasisRotationAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 116 / 295 — `api.ansatz.classes.HamiltonianVariationalAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / HamiltonianVariationalAnsatz` |
| slug | `HamiltonianVariationalAnsatz` |
| title_zh / en | HamiltonianVariationalAnsatz / HamiltonianVariationalAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.HamiltonianVariationalAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/HamiltonianVariationalAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `HamiltonianVariationalAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/HamiltonianVariationalAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 117 / 295 — `api.ansatz.classes.LayeredAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / LayeredAnsatz` |
| slug | `LayeredAnsatz` |
| title_zh / en | LayeredAnsatz / LayeredAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.LayeredAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/LayeredAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `LayeredAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/LayeredAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 118 / 295 — `api.ansatz.classes.HardwareEfficientAnsatz`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / ansatz / classes / HardwareEfficientAnsatz` |
| slug | `HardwareEfficientAnsatz` |
| title_zh / en | HardwareEfficientAnsatz / HardwareEfficientAnsatz |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/ansatz.html#inquanto.ansatz.HardwareEfficientAnsatz |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/ansatz/classes/HardwareEfficientAnsatz/` |

- **L1 分区**: `api` → **L2..n**: `ansatz` → `classes` → `HardwareEfficientAnsatz`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `GeneralAnsatz` — GeneralAnsatz（GeneralAnsatz）· `partial` · class-leaf
- `CircuitAnsatz` — CircuitAnsatz（CircuitAnsatz）· `partial` · class-leaf
- `ComposedAnsatz` — ComposedAnsatz（ComposedAnsatz）· `placeholder` · class-leaf
- `TrotterAnsatz` — TrotterAnsatz（TrotterAnsatz）· `partial` · class-leaf
- `FermionSpaceStateExp` — FermionSpaceStateExp（FermionSpaceStateExp）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCSD` — FermionSpaceAnsatzUCCSD（FermionSpaceAnsatzUCCSD）· `partial` · class-leaf
- `FermionSpaceAnsatzUCCD` — FermionSpaceAnsatzUCCD（FermionSpaceAnsatzUCCD）· `placeholder` · class-leaf
- `FermionSpaceStateExpChemicallyAware` — FermionSpaceStateExpChemicallyAware（FermionSpaceStateExpChemicallyAware）· `placeholder` · class-leaf
- `FermionSpaceAnsatzChemicallyAwareUCCSD` — FermionSpaceAnsatzChemicallyAwareUCCSD（FermionSpaceAnsatzChemicallyAwareUCCSD）· `placeholder` · class-leaf
- `FermionSpaceAnsatzkUpCCGD` — FermionSpaceAnsatzkUpCCGD（FermionSpaceAnsatzkUpCCGD）· `placeholder` · class-leaf
- _… 另有 17 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.quantum.ansatze.hea`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/ansatz/classes/HardwareEfficientAnsatz/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 119 / 295 — `api.computables`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables` |
| slug | `computables` |
| title_zh / en | 参考 API · inquanto.computables / Reference API · inquanto.computables |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/computables/` |

- **L1 分区**: `api` → **L2..n**: `computables`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.computable`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 120 / 295 — `api.computables.classes.ExpectationValue`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValue` |
| slug | `ExpectationValue` |
| title_zh / en | ExpectationValue / ExpectationValue |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValue |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValue/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValue`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValue/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 121 / 295 — `api.computables.classes.ExpectationValueBraDerivative`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueBraDerivative` |
| slug | `ExpectationValueBraDerivative` |
| title_zh / en | ExpectationValueBraDerivative / ExpectationValueBraDerivative |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueBraDerivative |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueBraDerivative/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueBraDerivative`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueBraDerivative/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 122 / 295 — `api.computables.classes.ExpectationValueBraDerivativeImag`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueBraDerivativeImag` |
| slug | `ExpectationValueBraDerivativeImag` |
| title_zh / en | ExpectationValueBraDerivativeImag / ExpectationValueBraDerivativeImag |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueBraDerivativeImag |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueBraDerivativeImag/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueBraDerivativeImag`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueBraDerivativeImag/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 123 / 295 — `api.computables.classes.ExpectationValueBraDerivativeReal`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueBraDerivativeReal` |
| slug | `ExpectationValueBraDerivativeReal` |
| title_zh / en | ExpectationValueBraDerivativeReal / ExpectationValueBraDerivativeReal |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueBraDerivativeReal |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueBraDerivativeReal/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueBraDerivativeReal`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueBraDerivativeReal/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 124 / 295 — `api.computables.classes.ExpectationValueDerivative`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueDerivative` |
| slug | `ExpectationValueDerivative` |
| title_zh / en | ExpectationValueDerivative / ExpectationValueDerivative |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueDerivative |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueDerivative/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueDerivative`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueDerivative/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 125 / 295 — `api.computables.classes.ExpectationValueKetDerivative`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueKetDerivative` |
| slug | `ExpectationValueKetDerivative` |
| title_zh / en | ExpectationValueKetDerivative / ExpectationValueKetDerivative |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueKetDerivative |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueKetDerivative/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueKetDerivative`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueKetDerivative/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 126 / 295 — `api.computables.classes.ExpectationValueKetDerivativeImag`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueKetDerivativeImag` |
| slug | `ExpectationValueKetDerivativeImag` |
| title_zh / en | ExpectationValueKetDerivativeImag / ExpectationValueKetDerivativeImag |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueKetDerivativeImag |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueKetDerivativeImag/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueKetDerivativeImag`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueKetDerivativeImag/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 127 / 295 — `api.computables.classes.ExpectationValueKetDerivativeReal`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueKetDerivativeReal` |
| slug | `ExpectationValueKetDerivativeReal` |
| title_zh / en | ExpectationValueKetDerivativeReal / ExpectationValueKetDerivativeReal |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueKetDerivativeReal |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueKetDerivativeReal/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueKetDerivativeReal`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueKetDerivativeReal/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 128 / 295 — `api.computables.classes.ExpectationValueNonHermitian`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueNonHermitian` |
| slug | `ExpectationValueNonHermitian` |
| title_zh / en | ExpectationValueNonHermitian / ExpectationValueNonHermitian |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueNonHermitian |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueNonHermitian/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueNonHermitian`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueNonHermitian/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 129 / 295 — `api.computables.classes.MetricTensorImag`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / MetricTensorImag` |
| slug | `MetricTensorImag` |
| title_zh / en | MetricTensorImag / MetricTensorImag |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.MetricTensorImag |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/MetricTensorImag/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `MetricTensorImag`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorReal` — MetricTensorReal（MetricTensorReal）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/MetricTensorImag/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 130 / 295 — `api.computables.classes.MetricTensorReal`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / MetricTensorReal` |
| slug | `MetricTensorReal` |
| title_zh / en | MetricTensorReal / MetricTensorReal |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.MetricTensorReal |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/MetricTensorReal/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `MetricTensorReal`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/MetricTensorReal/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 131 / 295 — `api.computables.classes.Overlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / Overlap` |
| slug | `Overlap` |
| title_zh / en | Overlap / Overlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.Overlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/Overlap/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `Overlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/Overlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 132 / 295 — `api.computables.classes.OverlapImag`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / OverlapImag` |
| slug | `OverlapImag` |
| title_zh / en | OverlapImag / OverlapImag |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.OverlapImag |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/OverlapImag/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `OverlapImag`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/OverlapImag/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 133 / 295 — `api.computables.classes.OverlapReal`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / OverlapReal` |
| slug | `OverlapReal` |
| title_zh / en | OverlapReal / OverlapReal |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.OverlapReal |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/OverlapReal/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `OverlapReal`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/OverlapReal/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 134 / 295 — `api.computables.classes.OverlapSquared`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / OverlapSquared` |
| slug | `OverlapSquared` |
| title_zh / en | OverlapSquared / OverlapSquared |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.OverlapSquared |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/OverlapSquared/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `OverlapSquared`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/OverlapSquared/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 135 / 295 — `api.computables.classes.ComputableFunction`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableFunction` |
| slug | `ComputableFunction` |
| title_zh / en | ComputableFunction / ComputableFunction |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableFunction |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableFunction/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableFunction`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableFunction/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 136 / 295 — `api.computables.classes.ComputableInt`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableInt` |
| slug | `ComputableInt` |
| title_zh / en | ComputableInt / ComputableInt |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableInt |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableInt/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableInt`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableInt/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 137 / 295 — `api.computables.classes.ComputableList`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableList` |
| slug | `ComputableList` |
| title_zh / en | ComputableList / ComputableList |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableList |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableList/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableList`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableList/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 138 / 295 — `api.computables.classes.ComputableTuple`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableTuple` |
| slug | `ComputableTuple` |
| title_zh / en | ComputableTuple / ComputableTuple |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableTuple |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableTuple/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableTuple`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableTuple/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 139 / 295 — `api.computables.classes.ComputableNode`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableNode` |
| slug | `ComputableNode` |
| title_zh / en | ComputableNode / ComputableNode |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableNode |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableNode/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableNode`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableNode/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 140 / 295 — `api.computables.classes.ComputableSingleChild`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ComputableSingleChild` |
| slug | `ComputableSingleChild` |
| title_zh / en | ComputableSingleChild / ComputableSingleChild |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ComputableSingleChild |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ComputableSingleChild/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ComputableSingleChild`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ComputableSingleChild/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 141 / 295 — `api.computables.classes.Averageable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / Averageable` |
| slug | `Averageable` |
| title_zh / en | Averageable / Averageable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.Averageable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/Averageable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `Averageable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/Averageable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 142 / 295 — `api.computables.classes.Evaluatable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / Evaluatable` |
| slug | `Evaluatable` |
| title_zh / en | Evaluatable / Evaluatable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.Evaluatable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/Evaluatable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `Evaluatable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/Evaluatable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 143 / 295 — `api.computables.classes.CommutatorComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / CommutatorComputable` |
| slug | `CommutatorComputable` |
| title_zh / en | CommutatorComputable / CommutatorComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.CommutatorComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/CommutatorComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `CommutatorComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/CommutatorComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 144 / 295 — `api.computables.classes.ExpectationValueSumComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ExpectationValueSumComputable` |
| slug | `ExpectationValueSumComputable` |
| title_zh / en | ExpectationValueSumComputable / ExpectationValueSumComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueSumComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ExpectationValueSumComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ExpectationValueSumComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ExpectationValueSumComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 145 / 295 — `api.computables.classes.HoleGFComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / HoleGFComputable` |
| slug | `HoleGFComputable` |
| title_zh / en | HoleGFComputable / HoleGFComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.HoleGFComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/HoleGFComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `HoleGFComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/HoleGFComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 146 / 295 — `api.computables.classes.KrylovSubspace`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / KrylovSubspace` |
| slug | `KrylovSubspace` |
| title_zh / en | KrylovSubspace / KrylovSubspace |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.KrylovSubspace |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/KrylovSubspace/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `KrylovSubspace`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/KrylovSubspace/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 147 / 295 — `api.computables.classes.KrylovSubspaceComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / KrylovSubspaceComputable` |
| slug | `KrylovSubspaceComputable` |
| title_zh / en | KrylovSubspaceComputable / KrylovSubspaceComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.KrylovSubspaceComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/KrylovSubspaceComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `KrylovSubspaceComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/KrylovSubspaceComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 148 / 295 — `api.computables.classes.LanczosCoefficientsComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / LanczosCoefficientsComputable` |
| slug | `LanczosCoefficientsComputable` |
| title_zh / en | LanczosCoefficientsComputable / LanczosCoefficientsComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.LanczosCoefficientsComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/LanczosCoefficientsComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `LanczosCoefficientsComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/LanczosCoefficientsComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 149 / 295 — `api.computables.classes.LanczosMatrixComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / LanczosMatrixComputable` |
| slug | `LanczosMatrixComputable` |
| title_zh / en | LanczosMatrixComputable / LanczosMatrixComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.LanczosMatrixComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/LanczosMatrixComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `LanczosMatrixComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/LanczosMatrixComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 150 / 295 — `api.computables.classes.ManyBodyGFComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ManyBodyGFComputable` |
| slug | `ManyBodyGFComputable` |
| title_zh / en | ManyBodyGFComputable / ManyBodyGFComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ManyBodyGFComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ManyBodyGFComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ManyBodyGFComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ManyBodyGFComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 151 / 295 — `api.computables.classes.NonOrthogonalMatricesComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / NonOrthogonalMatricesComputable` |
| slug | `NonOrthogonalMatricesComputable` |
| title_zh / en | NonOrthogonalMatricesComputable / NonOrthogonalMatricesComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.NonOrthogonalMatricesComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/NonOrthogonalMatricesComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `NonOrthogonalMatricesComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/NonOrthogonalMatricesComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 152 / 295 — `api.computables.classes.OverlapMatrixComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / OverlapMatrixComputable` |
| slug | `OverlapMatrixComputable` |
| title_zh / en | OverlapMatrixComputable / OverlapMatrixComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.OverlapMatrixComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/OverlapMatrixComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `OverlapMatrixComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/OverlapMatrixComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 153 / 295 — `api.computables.classes.PDM1234RealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / PDM1234RealComputable` |
| slug | `PDM1234RealComputable` |
| title_zh / en | PDM1234RealComputable / PDM1234RealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.PDM1234RealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/PDM1234RealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `PDM1234RealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/PDM1234RealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 154 / 295 — `api.computables.classes.ParticleGFComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / ParticleGFComputable` |
| slug | `ParticleGFComputable` |
| title_zh / en | ParticleGFComputable / ParticleGFComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ParticleGFComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/ParticleGFComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `ParticleGFComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/ParticleGFComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 155 / 295 — `api.computables.classes.QCM4Computable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / QCM4Computable` |
| slug | `QCM4Computable` |
| title_zh / en | QCM4Computable / QCM4Computable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.QCM4Computable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/QCM4Computable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `QCM4Computable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/QCM4Computable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 156 / 295 — `api.computables.classes.QSEMatricesComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / QSEMatricesComputable` |
| slug | `QSEMatricesComputable` |
| title_zh / en | QSEMatricesComputable / QSEMatricesComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.QSEMatricesComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/QSEMatricesComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `QSEMatricesComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/QSEMatricesComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 157 / 295 — `api.computables.classes.RDM1234RealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / RDM1234RealComputable` |
| slug | `RDM1234RealComputable` |
| title_zh / en | RDM1234RealComputable / RDM1234RealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.RDM1234RealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/RDM1234RealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `RDM1234RealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/RDM1234RealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 158 / 295 — `api.computables.classes.RestrictedOneBodyRDMComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / RestrictedOneBodyRDMComputable` |
| slug | `RestrictedOneBodyRDMComputable` |
| title_zh / en | RestrictedOneBodyRDMComputable / RestrictedOneBodyRDMComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.RestrictedOneBodyRDMComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/RestrictedOneBodyRDMComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `RestrictedOneBodyRDMComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/RestrictedOneBodyRDMComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 159 / 295 — `api.computables.classes.RestrictedOneBodyRDMRealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / RestrictedOneBodyRDMRealComputable` |
| slug | `RestrictedOneBodyRDMRealComputable` |
| title_zh / en | RestrictedOneBodyRDMRealComputable / RestrictedOneBodyRDMRealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.RestrictedOneBodyRDMRealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/RestrictedOneBodyRDMRealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `RestrictedOneBodyRDMRealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/RestrictedOneBodyRDMRealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 160 / 295 — `api.computables.classes.SCEOMMatrixComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / SCEOMMatrixComputable` |
| slug | `SCEOMMatrixComputable` |
| title_zh / en | SCEOMMatrixComputable / SCEOMMatrixComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.SCEOMMatrixComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/SCEOMMatrixComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `SCEOMMatrixComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/SCEOMMatrixComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 161 / 295 — `api.computables.classes.SpinlessNBodyPDMArrayRealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / SpinlessNBodyPDMArrayRealComputable` |
| slug | `SpinlessNBodyPDMArrayRealComputable` |
| title_zh / en | SpinlessNBodyPDMArrayRealComputable / SpinlessNBodyPDMArrayRealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.SpinlessNBodyPDMArrayRealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/SpinlessNBodyPDMArrayRealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `SpinlessNBodyPDMArrayRealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/SpinlessNBodyPDMArrayRealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 162 / 295 — `api.computables.classes.SpinlessNBodyRDMArrayRealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / SpinlessNBodyRDMArrayRealComputable` |
| slug | `SpinlessNBodyRDMArrayRealComputable` |
| title_zh / en | SpinlessNBodyRDMArrayRealComputable / SpinlessNBodyRDMArrayRealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.SpinlessNBodyRDMArrayRealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/SpinlessNBodyRDMArrayRealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `SpinlessNBodyRDMArrayRealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/SpinlessNBodyRDMArrayRealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 163 / 295 — `api.computables.classes.UnrestrictedOneBodyRDMComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / UnrestrictedOneBodyRDMComputable` |
| slug | `UnrestrictedOneBodyRDMComputable` |
| title_zh / en | UnrestrictedOneBodyRDMComputable / UnrestrictedOneBodyRDMComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.UnrestrictedOneBodyRDMComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/UnrestrictedOneBodyRDMComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `UnrestrictedOneBodyRDMComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/UnrestrictedOneBodyRDMComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 164 / 295 — `api.computables.classes.UnrestrictedOneBodyRDMRealComputable`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / computables / classes / UnrestrictedOneBodyRDMRealComputable` |
| slug | `UnrestrictedOneBodyRDMRealComputable` |
| title_zh / en | UnrestrictedOneBodyRDMRealComputable / UnrestrictedOneBodyRDMRealComputable |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.UnrestrictedOneBodyRDMRealComputable |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/computables/classes/UnrestrictedOneBodyRDMRealComputable/` |

- **L1 分区**: `api` → **L2..n**: `computables` → `classes` → `UnrestrictedOneBodyRDMRealComputable`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ExpectationValue` — ExpectationValue（ExpectationValue）· `partial` · class-leaf
- `ExpectationValueBraDerivative` — ExpectationValueBraDerivative（ExpectationValueBraDerivative）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeImag` — ExpectationValueBraDerivativeImag（ExpectationValueBraDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueBraDerivativeReal` — ExpectationValueBraDerivativeReal（ExpectationValueBraDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueDerivative` — ExpectationValueDerivative（ExpectationValueDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivative` — ExpectationValueKetDerivative（ExpectationValueKetDerivative）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeImag` — ExpectationValueKetDerivativeImag（ExpectationValueKetDerivativeImag）· `placeholder` · class-leaf
- `ExpectationValueKetDerivativeReal` — ExpectationValueKetDerivativeReal（ExpectationValueKetDerivativeReal）· `placeholder` · class-leaf
- `ExpectationValueNonHermitian` — ExpectationValueNonHermitian（ExpectationValueNonHermitian）· `placeholder` · class-leaf
- `MetricTensorImag` — MetricTensorImag（MetricTensorImag）· `placeholder` · class-leaf
- _… 另有 34 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/computables/classes/UnrestrictedOneBodyRDMRealComputable/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 165 / 295 — `api.operators`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators` |
| slug | `operators` |
| title_zh / en | 参考 API · inquanto.operators / Reference API · inquanto.operators |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/operators/` |

- **L1 分区**: `api` → **L2..n**: `operators`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.hamiltonian`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 166 / 295 — `api.operators.classes.ChemistryRestrictedIntegralOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / ChemistryRestrictedIntegralOperator` |
| slug | `ChemistryRestrictedIntegralOperator` |
| title_zh / en | ChemistryRestrictedIntegralOperator / ChemistryRestrictedIntegralOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.ChemistryRestrictedIntegralOperator |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/ChemistryRestrictedIntegralOperator/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `ChemistryRestrictedIntegralOperator`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/ChemistryRestrictedIntegralOperator/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 167 / 295 — `api.operators.classes.ChemistryRestrictedIntegralOperatorCompact`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / ChemistryRestrictedIntegralOperatorCompact` |
| slug | `ChemistryRestrictedIntegralOperatorCompact` |
| title_zh / en | ChemistryRestrictedIntegralOperatorCompact / ChemistryRestrictedIntegralOperatorCompact |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.ChemistryRestrictedIntegralOperatorCompact |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/ChemistryRestrictedIntegralOperatorCompact/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `ChemistryRestrictedIntegralOperatorCompact`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/ChemistryRestrictedIntegralOperatorCompact/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 168 / 295 — `api.operators.classes.ChemistryUnrestrictedIntegralOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / ChemistryUnrestrictedIntegralOperator` |
| slug | `ChemistryUnrestrictedIntegralOperator` |
| title_zh / en | ChemistryUnrestrictedIntegralOperator / ChemistryUnrestrictedIntegralOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.ChemistryUnrestrictedIntegralOperator |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/ChemistryUnrestrictedIntegralOperator/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `ChemistryUnrestrictedIntegralOperator`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/ChemistryUnrestrictedIntegralOperator/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 169 / 295 — `api.operators.classes.ChemistryUnrestrictedIntegralOperatorCompact`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / ChemistryUnrestrictedIntegralOperatorCompact` |
| slug | `ChemistryUnrestrictedIntegralOperatorCompact` |
| title_zh / en | ChemistryUnrestrictedIntegralOperatorCompact / ChemistryUnrestrictedIntegralOperatorCompact |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.ChemistryUnrestrictedIntegralOperatorCompact |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/ChemistryUnrestrictedIntegralOperatorCompact/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `ChemistryUnrestrictedIntegralOperatorCompact`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/ChemistryUnrestrictedIntegralOperatorCompact/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 170 / 295 — `api.operators.classes.DoubleFactorizedTwoBodyIntegrals`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / DoubleFactorizedTwoBodyIntegrals` |
| slug | `DoubleFactorizedTwoBodyIntegrals` |
| title_zh / en | DoubleFactorizedTwoBodyIntegrals / DoubleFactorizedTwoBodyIntegrals |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.DoubleFactorizedTwoBodyIntegrals |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/DoubleFactorizedTwoBodyIntegrals/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `DoubleFactorizedTwoBodyIntegrals`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/DoubleFactorizedTwoBodyIntegrals/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 171 / 295 — `api.operators.classes.FCIDumpRestricted`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / FCIDumpRestricted` |
| slug | `FCIDumpRestricted` |
| title_zh / en | FCIDumpRestricted / FCIDumpRestricted |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.FCIDumpRestricted |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/FCIDumpRestricted/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `FCIDumpRestricted`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/FCIDumpRestricted/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 172 / 295 — `api.operators.classes.FCIDumpUnrestricted`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / FCIDumpUnrestricted` |
| slug | `FCIDumpUnrestricted` |
| title_zh / en | FCIDumpUnrestricted / FCIDumpUnrestricted |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.FCIDumpUnrestricted |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/FCIDumpUnrestricted/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `FCIDumpUnrestricted`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/FCIDumpUnrestricted/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 173 / 295 — `api.operators.classes.FermionOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / FermionOperator` |
| slug | `FermionOperator` |
| title_zh / en | FermionOperator / FermionOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.FermionOperator |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/FermionOperator/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `FermionOperator`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/FermionOperator/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 174 / 295 — `api.operators.classes.FermionOperatorList`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / FermionOperatorList` |
| slug | `FermionOperatorList` |
| title_zh / en | FermionOperatorList / FermionOperatorList |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.FermionOperatorList |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/FermionOperatorList/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `FermionOperatorList`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/FermionOperatorList/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 175 / 295 — `api.operators.classes.QubitOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / QubitOperator` |
| slug | `QubitOperator` |
| title_zh / en | QubitOperator / QubitOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.QubitOperator |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/QubitOperator/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `QubitOperator`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperatorList` — QubitOperatorList（QubitOperatorList）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/QubitOperator/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 176 / 295 — `api.operators.classes.QubitOperatorList`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / QubitOperatorList` |
| slug | `QubitOperatorList` |
| title_zh / en | QubitOperatorList / QubitOperatorList |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.QubitOperatorList |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/QubitOperatorList/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `QubitOperatorList`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/QubitOperatorList/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 177 / 295 — `api.operators.classes.QubitOperatorString`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / QubitOperatorString` |
| slug | `QubitOperatorString` |
| title_zh / en | QubitOperatorString / QubitOperatorString |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.QubitOperatorString |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/QubitOperatorString/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `QubitOperatorString`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/QubitOperatorString/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 178 / 295 — `api.operators.classes.OrbitalTransformer`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / OrbitalTransformer` |
| slug | `OrbitalTransformer` |
| title_zh / en | OrbitalTransformer / OrbitalTransformer |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.OrbitalTransformer |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/OrbitalTransformer/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `OrbitalTransformer`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/OrbitalTransformer/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 179 / 295 — `api.operators.classes.RestrictedDoubleFactorizedHamiltonian`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / RestrictedDoubleFactorizedHamiltonian` |
| slug | `RestrictedDoubleFactorizedHamiltonian` |
| title_zh / en | RestrictedDoubleFactorizedHamiltonian / RestrictedDoubleFactorizedHamiltonian |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.RestrictedDoubleFactorizedHamiltonian |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/RestrictedDoubleFactorizedHamiltonian/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `RestrictedDoubleFactorizedHamiltonian`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/RestrictedDoubleFactorizedHamiltonian/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 180 / 295 — `api.operators.classes.RestrictedOneBodyRDM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / RestrictedOneBodyRDM` |
| slug | `RestrictedOneBodyRDM` |
| title_zh / en | RestrictedOneBodyRDM / RestrictedOneBodyRDM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.RestrictedOneBodyRDM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/RestrictedOneBodyRDM/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `RestrictedOneBodyRDM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/RestrictedOneBodyRDM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 181 / 295 — `api.operators.classes.RestrictedTwoBodyRDM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / RestrictedTwoBodyRDM` |
| slug | `RestrictedTwoBodyRDM` |
| title_zh / en | RestrictedTwoBodyRDM / RestrictedTwoBodyRDM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.RestrictedTwoBodyRDM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/RestrictedTwoBodyRDM/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `RestrictedTwoBodyRDM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/RestrictedTwoBodyRDM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 182 / 295 — `api.operators.classes.UnrestrictedDoubleFactorizedHamiltonian`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / UnrestrictedDoubleFactorizedHamiltonian` |
| slug | `UnrestrictedDoubleFactorizedHamiltonian` |
| title_zh / en | UnrestrictedDoubleFactorizedHamiltonian / UnrestrictedDoubleFactorizedHamiltonian |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.UnrestrictedDoubleFactorizedHamiltonian |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/UnrestrictedDoubleFactorizedHamiltonian/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `UnrestrictedDoubleFactorizedHamiltonian`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/UnrestrictedDoubleFactorizedHamiltonian/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 183 / 295 — `api.operators.classes.UnrestrictedOneBodyRDM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / UnrestrictedOneBodyRDM` |
| slug | `UnrestrictedOneBodyRDM` |
| title_zh / en | UnrestrictedOneBodyRDM / UnrestrictedOneBodyRDM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.UnrestrictedOneBodyRDM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/UnrestrictedOneBodyRDM/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `UnrestrictedOneBodyRDM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/UnrestrictedOneBodyRDM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 184 / 295 — `api.operators.classes.UnrestrictedTwoBodyRDM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / UnrestrictedTwoBodyRDM` |
| slug | `UnrestrictedTwoBodyRDM` |
| title_zh / en | UnrestrictedTwoBodyRDM / UnrestrictedTwoBodyRDM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.UnrestrictedTwoBodyRDM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/UnrestrictedTwoBodyRDM/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `UnrestrictedTwoBodyRDM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/UnrestrictedTwoBodyRDM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 185 / 295 — `api.operators.classes.SymmetryOperatorFermionic`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / SymmetryOperatorFermionic` |
| slug | `SymmetryOperatorFermionic` |
| title_zh / en | SymmetryOperatorFermionic / SymmetryOperatorFermionic |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.SymmetryOperatorFermionic |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/SymmetryOperatorFermionic/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `SymmetryOperatorFermionic`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/SymmetryOperatorFermionic/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 186 / 295 — `api.operators.classes.SymmetryOperatorFermionicFactorized`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / SymmetryOperatorFermionicFactorized` |
| slug | `SymmetryOperatorFermionicFactorized` |
| title_zh / en | SymmetryOperatorFermionicFactorized / SymmetryOperatorFermionicFactorized |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.SymmetryOperatorFermionicFactorized |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/SymmetryOperatorFermionicFactorized/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `SymmetryOperatorFermionicFactorized`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/SymmetryOperatorFermionicFactorized/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 187 / 295 — `api.operators.classes.SymmetryOperatorPauli`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / SymmetryOperatorPauli` |
| slug | `SymmetryOperatorPauli` |
| title_zh / en | SymmetryOperatorPauli / SymmetryOperatorPauli |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.SymmetryOperatorPauli |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/SymmetryOperatorPauli/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `SymmetryOperatorPauli`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/SymmetryOperatorPauli/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 188 / 295 — `api.operators.classes.SymmetryOperatorPauliFactorized`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / SymmetryOperatorPauliFactorized` |
| slug | `SymmetryOperatorPauliFactorized` |
| title_zh / en | SymmetryOperatorPauliFactorized / SymmetryOperatorPauliFactorized |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.SymmetryOperatorPauliFactorized |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/SymmetryOperatorPauliFactorized/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `SymmetryOperatorPauliFactorized`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/SymmetryOperatorPauliFactorized/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 189 / 295 — `api.operators.classes.XDFCoreTensor`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / operators / classes / XDFCoreTensor` |
| slug | `XDFCoreTensor` |
| title_zh / en | XDFCoreTensor / XDFCoreTensor |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/operators.html#inquanto.operators.XDFCoreTensor |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/operators/classes/XDFCoreTensor/` |

- **L1 分区**: `api` → **L2..n**: `operators` → `classes` → `XDFCoreTensor`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `ChemistryRestrictedIntegralOperator` — ChemistryRestrictedIntegralOperator（ChemistryRestrictedIntegralOperator）· `partial` · class-leaf
- `ChemistryRestrictedIntegralOperatorCompact` — ChemistryRestrictedIntegralOperatorCompact（ChemistryRestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperator` — ChemistryUnrestrictedIntegralOperator（ChemistryUnrestrictedIntegralOperator）· `placeholder` · class-leaf
- `ChemistryUnrestrictedIntegralOperatorCompact` — ChemistryUnrestrictedIntegralOperatorCompact（ChemistryUnrestrictedIntegralOperatorCompact）· `placeholder` · class-leaf
- `DoubleFactorizedTwoBodyIntegrals` — DoubleFactorizedTwoBodyIntegrals（DoubleFactorizedTwoBodyIntegrals）· `placeholder` · class-leaf
- `FCIDumpRestricted` — FCIDumpRestricted（FCIDumpRestricted）· `placeholder` · class-leaf
- `FCIDumpUnrestricted` — FCIDumpUnrestricted（FCIDumpUnrestricted）· `placeholder` · class-leaf
- `FermionOperator` — FermionOperator（FermionOperator）· `shipped` · class-leaf
- `FermionOperatorList` — FermionOperatorList（FermionOperatorList）· `shipped` · class-leaf
- `QubitOperator` — QubitOperator（QubitOperator）· `shipped` · class-leaf
- _… 另有 13 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/operators/classes/XDFCoreTensor/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 190 / 295 — `api.spaces`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces` |
| slug | `spaces` |
| title_zh / en | 参考 API · inquanto.spaces / Reference API · inquanto.spaces |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/spaces/` |

- **L1 分区**: `api` → **L2..n**: `spaces`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 191 / 295 — `api.spaces.classes.FermionSpace`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces / classes / FermionSpace` |
| slug | `FermionSpace` |
| title_zh / en | FermionSpace / FermionSpace |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html#inquanto.spaces.FermionSpace |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/spaces/classes/FermionSpace/` |

- **L1 分区**: `api` → **L2..n**: `spaces` → `classes` → `FermionSpace`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionSpaceBrillouin` — FermionSpaceBrillouin（FermionSpaceBrillouin）· `placeholder` · class-leaf
- `FermionSpaceSupercell` — FermionSpaceSupercell（FermionSpaceSupercell）· `placeholder` · class-leaf
- `ParaFermionSpace` — ParaFermionSpace（ParaFermionSpace）· `placeholder` · class-leaf
- `QubitSpace` — QubitSpace（QubitSpace）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/classes/FermionSpace/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 192 / 295 — `api.spaces.classes.FermionSpaceBrillouin`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces / classes / FermionSpaceBrillouin` |
| slug | `FermionSpaceBrillouin` |
| title_zh / en | FermionSpaceBrillouin / FermionSpaceBrillouin |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html#inquanto.spaces.FermionSpaceBrillouin |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/spaces/classes/FermionSpaceBrillouin/` |

- **L1 分区**: `api` → **L2..n**: `spaces` → `classes` → `FermionSpaceBrillouin`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionSpace` — FermionSpace（FermionSpace）· `partial` · class-leaf
- `FermionSpaceSupercell` — FermionSpaceSupercell（FermionSpaceSupercell）· `placeholder` · class-leaf
- `ParaFermionSpace` — ParaFermionSpace（ParaFermionSpace）· `placeholder` · class-leaf
- `QubitSpace` — QubitSpace（QubitSpace）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/classes/FermionSpaceBrillouin/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 193 / 295 — `api.spaces.classes.FermionSpaceSupercell`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces / classes / FermionSpaceSupercell` |
| slug | `FermionSpaceSupercell` |
| title_zh / en | FermionSpaceSupercell / FermionSpaceSupercell |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html#inquanto.spaces.FermionSpaceSupercell |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/spaces/classes/FermionSpaceSupercell/` |

- **L1 分区**: `api` → **L2..n**: `spaces` → `classes` → `FermionSpaceSupercell`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionSpace` — FermionSpace（FermionSpace）· `partial` · class-leaf
- `FermionSpaceBrillouin` — FermionSpaceBrillouin（FermionSpaceBrillouin）· `placeholder` · class-leaf
- `ParaFermionSpace` — ParaFermionSpace（ParaFermionSpace）· `placeholder` · class-leaf
- `QubitSpace` — QubitSpace（QubitSpace）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/classes/FermionSpaceSupercell/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 194 / 295 — `api.spaces.classes.ParaFermionSpace`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces / classes / ParaFermionSpace` |
| slug | `ParaFermionSpace` |
| title_zh / en | ParaFermionSpace / ParaFermionSpace |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html#inquanto.spaces.ParaFermionSpace |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/spaces/classes/ParaFermionSpace/` |

- **L1 分区**: `api` → **L2..n**: `spaces` → `classes` → `ParaFermionSpace`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionSpace` — FermionSpace（FermionSpace）· `partial` · class-leaf
- `FermionSpaceBrillouin` — FermionSpaceBrillouin（FermionSpaceBrillouin）· `placeholder` · class-leaf
- `FermionSpaceSupercell` — FermionSpaceSupercell（FermionSpaceSupercell）· `placeholder` · class-leaf
- `QubitSpace` — QubitSpace（QubitSpace）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/classes/ParaFermionSpace/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 195 / 295 — `api.spaces.classes.QubitSpace`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / spaces / classes / QubitSpace` |
| slug | `QubitSpace` |
| title_zh / en | QubitSpace / QubitSpace |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/spaces.html#inquanto.spaces.QubitSpace |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/spaces/classes/QubitSpace/` |

- **L1 分区**: `api` → **L2..n**: `spaces` → `classes` → `QubitSpace`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionSpace` — FermionSpace（FermionSpace）· `partial` · class-leaf
- `FermionSpaceBrillouin` — FermionSpaceBrillouin（FermionSpaceBrillouin）· `placeholder` · class-leaf
- `FermionSpaceSupercell` — FermionSpaceSupercell（FermionSpaceSupercell）· `placeholder` · class-leaf
- `ParaFermionSpace` — ParaFermionSpace（ParaFermionSpace）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/spaces/classes/QubitSpace/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 196 / 295 — `api.states`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / states` |
| slug | `states` |
| title_zh / en | 参考 API · inquanto.states / Reference API · inquanto.states |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/states.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/states/` |

- **L1 分区**: `api` → **L2..n**: `states`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/states/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 197 / 295 — `api.states.classes.FermionState`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / states / classes / FermionState` |
| slug | `FermionState` |
| title_zh / en | FermionState / FermionState |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/states.html#inquanto.states.FermionState |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/states/classes/FermionState/` |

- **L1 分区**: `api` → **L2..n**: `states` → `classes` → `FermionState`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `QubitState` — QubitState（QubitState）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/states/classes/FermionState/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 198 / 295 — `api.states.classes.QubitState`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / states / classes / QubitState` |
| slug | `QubitState` |
| title_zh / en | QubitState / QubitState |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/states.html#inquanto.states.QubitState |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/states/classes/QubitState/` |

- **L1 分区**: `api` → **L2..n**: `states` → `classes` → `QubitState`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `FermionState` — FermionState（FermionState）· `partial` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/states/classes/QubitState/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 199 / 295 — `api.mappings`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / mappings` |
| slug | `mappings` |
| title_zh / en | 参考 API · inquanto.mappings / Reference API · inquanto.mappings |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/mappings.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/mappings/` |

- **L1 分区**: `api` → **L2..n**: `mappings`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/mappings/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 200 / 295 — `api.mappings.classes.QubitMappingJordanWigner`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / mappings / classes / QubitMappingJordanWigner` |
| slug | `QubitMappingJordanWigner` |
| title_zh / en | QubitMappingJordanWigner / QubitMappingJordanWigner |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/mappings.html#inquanto.mappings.QubitMappingJordanWigner |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/mappings/classes/QubitMappingJordanWigner/` |

- **L1 分区**: `api` → **L2..n**: `mappings` → `classes` → `QubitMappingJordanWigner`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `QubitMappingBravyiKitaev` — QubitMappingBravyiKitaev（QubitMappingBravyiKitaev）· `placeholder` · class-leaf
- `QubitMappingParity` — QubitMappingParity（QubitMappingParity）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/mappings/classes/QubitMappingJordanWigner/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 201 / 295 — `api.mappings.classes.QubitMappingBravyiKitaev`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / mappings / classes / QubitMappingBravyiKitaev` |
| slug | `QubitMappingBravyiKitaev` |
| title_zh / en | QubitMappingBravyiKitaev / QubitMappingBravyiKitaev |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/mappings.html#inquanto.mappings.QubitMappingBravyiKitaev |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/mappings/classes/QubitMappingBravyiKitaev/` |

- **L1 分区**: `api` → **L2..n**: `mappings` → `classes` → `QubitMappingBravyiKitaev`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `QubitMappingJordanWigner` — QubitMappingJordanWigner（QubitMappingJordanWigner）· `shipped` · class-leaf
- `QubitMappingParity` — QubitMappingParity（QubitMappingParity）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/mappings/classes/QubitMappingBravyiKitaev/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 202 / 295 — `api.mappings.classes.QubitMappingParity`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / mappings / classes / QubitMappingParity` |
| slug | `QubitMappingParity` |
| title_zh / en | QubitMappingParity / QubitMappingParity |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/mappings.html#inquanto.mappings.QubitMappingParity |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/mappings/classes/QubitMappingParity/` |

- **L1 分区**: `api` → **L2..n**: `mappings` → `classes` → `QubitMappingParity`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `QubitMappingJordanWigner` — QubitMappingJordanWigner（QubitMappingJordanWigner）· `shipped` · class-leaf
- `QubitMappingBravyiKitaev` — QubitMappingBravyiKitaev（QubitMappingBravyiKitaev）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/mappings/classes/QubitMappingParity/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 203 / 295 — `api.minimizers`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers` |
| slug | `minimizers` |
| title_zh / en | 参考 API · inquanto.minimizers / Reference API · inquanto.minimizers |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/minimizers/` |

- **L1 分区**: `api` → **L2..n**: `minimizers`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `symmetry` — Reference API · inquanto.symmetry（参考 API · inquanto.symmetry）· `placeholder`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 204 / 295 — `api.minimizers.classes.MinimizerScipy`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers / classes / MinimizerScipy` |
| slug | `MinimizerScipy` |
| title_zh / en | MinimizerScipy / MinimizerScipy |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html#inquanto.minimizers.MinimizerScipy |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/minimizers/classes/MinimizerScipy/` |

- **L1 分区**: `api` → **L2..n**: `minimizers` → `classes` → `MinimizerScipy`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `MinimizerNFT` — MinimizerNFT（MinimizerNFT）· `placeholder` · class-leaf
- `MinimizerRotosolve` — MinimizerRotosolve（MinimizerRotosolve）· `placeholder` · class-leaf
- `MinimizerSPSA` — MinimizerSPSA（MinimizerSPSA）· `placeholder` · class-leaf
- `MinimizerSGD` — MinimizerSGD（MinimizerSGD）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/classes/MinimizerScipy/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 205 / 295 — `api.minimizers.classes.MinimizerNFT`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers / classes / MinimizerNFT` |
| slug | `MinimizerNFT` |
| title_zh / en | MinimizerNFT / MinimizerNFT |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html#inquanto.minimizers.MinimizerNFT |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/minimizers/classes/MinimizerNFT/` |

- **L1 分区**: `api` → **L2..n**: `minimizers` → `classes` → `MinimizerNFT`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `MinimizerScipy` — MinimizerScipy（MinimizerScipy）· `shipped` · class-leaf
- `MinimizerRotosolve` — MinimizerRotosolve（MinimizerRotosolve）· `placeholder` · class-leaf
- `MinimizerSPSA` — MinimizerSPSA（MinimizerSPSA）· `placeholder` · class-leaf
- `MinimizerSGD` — MinimizerSGD（MinimizerSGD）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/classes/MinimizerNFT/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 206 / 295 — `api.minimizers.classes.MinimizerRotosolve`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers / classes / MinimizerRotosolve` |
| slug | `MinimizerRotosolve` |
| title_zh / en | MinimizerRotosolve / MinimizerRotosolve |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html#inquanto.minimizers.MinimizerRotosolve |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/minimizers/classes/MinimizerRotosolve/` |

- **L1 分区**: `api` → **L2..n**: `minimizers` → `classes` → `MinimizerRotosolve`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `MinimizerScipy` — MinimizerScipy（MinimizerScipy）· `shipped` · class-leaf
- `MinimizerNFT` — MinimizerNFT（MinimizerNFT）· `placeholder` · class-leaf
- `MinimizerSPSA` — MinimizerSPSA（MinimizerSPSA）· `placeholder` · class-leaf
- `MinimizerSGD` — MinimizerSGD（MinimizerSGD）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/classes/MinimizerRotosolve/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 207 / 295 — `api.minimizers.classes.MinimizerSPSA`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers / classes / MinimizerSPSA` |
| slug | `MinimizerSPSA` |
| title_zh / en | MinimizerSPSA / MinimizerSPSA |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html#inquanto.minimizers.MinimizerSPSA |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/minimizers/classes/MinimizerSPSA/` |

- **L1 分区**: `api` → **L2..n**: `minimizers` → `classes` → `MinimizerSPSA`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `MinimizerScipy` — MinimizerScipy（MinimizerScipy）· `shipped` · class-leaf
- `MinimizerNFT` — MinimizerNFT（MinimizerNFT）· `placeholder` · class-leaf
- `MinimizerRotosolve` — MinimizerRotosolve（MinimizerRotosolve）· `placeholder` · class-leaf
- `MinimizerSGD` — MinimizerSGD（MinimizerSGD）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/classes/MinimizerSPSA/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 208 / 295 — `api.minimizers.classes.MinimizerSGD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / minimizers / classes / MinimizerSGD` |
| slug | `MinimizerSGD` |
| title_zh / en | MinimizerSGD / MinimizerSGD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/minimizers.html#inquanto.minimizers.MinimizerSGD |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/minimizers/classes/MinimizerSGD/` |

- **L1 分区**: `api` → **L2..n**: `minimizers` → `classes` → `MinimizerSGD`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `MinimizerScipy` — MinimizerScipy（MinimizerScipy）· `shipped` · class-leaf
- `MinimizerNFT` — MinimizerNFT（MinimizerNFT）· `placeholder` · class-leaf
- `MinimizerRotosolve` — MinimizerRotosolve（MinimizerRotosolve）· `placeholder` · class-leaf
- `MinimizerSPSA` — MinimizerSPSA（MinimizerSPSA）· `placeholder` · class-leaf

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/minimizers/classes/MinimizerSGD/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 209 / 295 — `api.symmetry`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / symmetry` |
| slug | `symmetry` |
| title_zh / en | 参考 API · inquanto.symmetry / Reference API · inquanto.symmetry |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/symmetry.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/symmetry/` |

- **L1 分区**: `api` → **L2..n**: `symmetry`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/symmetry/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 210 / 295 — `api.core`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / core` |
| slug | `core` |
| title_zh / en | 参考 API · inquanto.core / Reference API · inquanto.core |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/core.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/api/core/` |

- **L1 分区**: `api` → **L2..n**: `core`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/core/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 211 / 295 — `api.embeddings`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / embeddings` |
| slug | `embeddings` |
| title_zh / en | 参考 API · inquanto.embeddings / Reference API · inquanto.embeddings |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/embeddings.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/api/embeddings/` |

- **L1 分区**: `api` → **L2..n**: `embeddings`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.embedding`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/embeddings/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 212 / 295 — `api.experiments`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / experiments` |
| slug | `experiments` |
| title_zh / en | 参考 API · inquanto.experiments / Reference API · inquanto.experiments |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/experiments.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/experiments/` |

- **L1 分区**: `api` → **L2..n**: `experiments`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **Manifest 摘要（zh）**: 与 Knowledge Articles 配套的演示型 API 子域。
- **Manifest 摘要（en）**: Demonstration-oriented API subtree paired with Knowledge Articles.
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/experiments/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 213 / 295 — `api.experiments.experiment_qec_qpe`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / experiments / experiment_qec_qpe` |
| slug | `experiment_qec_qpe` |
| title_zh / en | 量子纠错 QPE 演示 / Quantum error-corrected QPE demonstration |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/experiments/experiment_qec_qpe.html |
| pillar / diataxis / class_leaf | P2 / tutorial / no |
| mirror_path | `/mirror/api/experiments/experiment_qec_qpe/` |

- **L1 分区**: `api` → **L2..n**: `experiments` → `experiment_qec_qpe`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `tutorial` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

_（manifest 中此父节点下无其它兄弟项）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/experiments/experiment_qec_qpe/`
- **四柱指南**: `/guide/algorithms-and-protocols/`

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 214 / 295 — `api.express`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / express` |
| slug | `express` |
| title_zh / en | 参考 API · inquanto.express / Reference API · inquanto.express |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/express.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/express/` |

- **L1 分区**: `api` → **L2..n**: `express`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.express`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/express/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 215 / 295 — `api.geometries`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / geometries` |
| slug | `geometries` |
| title_zh / en | 参考 API · inquanto.geometries / Reference API · inquanto.geometries |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/geometry.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/api/geometries/` |

- **L1 分区**: `api` → **L2..n**: `geometries`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.molecule`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/geometries/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 216 / 295 — `api.protocols`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols` |
| slug | `protocols` |
| title_zh / en | 参考 API · inquanto.protocols / Reference API · inquanto.protocols |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/protocols/` |

- **L1 分区**: `api` → **L2..n**: `protocols`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 217 / 295 — `api.protocols.classes.PauliAveraging`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / PauliAveraging` |
| slug | `PauliAveraging` |
| title_zh / en | PauliAveraging / PauliAveraging |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.PauliAveraging |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/PauliAveraging/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `PauliAveraging`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.protocols.PauliAveragingProtocol`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/PauliAveraging/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 218 / 295 — `api.protocols.classes.HadamardTest`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / HadamardTest` |
| slug | `HadamardTest` |
| title_zh / en | HadamardTest / HadamardTest |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.HadamardTest |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/HadamardTest/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `HadamardTest`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/HadamardTest/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 219 / 295 — `api.protocols.classes.ComputeUncompute`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / ComputeUncompute` |
| slug | `ComputeUncompute` |
| title_zh / en | ComputeUncompute / ComputeUncompute |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.ComputeUncompute |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/ComputeUncompute/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `ComputeUncompute`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/ComputeUncompute/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 220 / 295 — `api.protocols.classes.DestructiveSwapTest`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / DestructiveSwapTest` |
| slug | `DestructiveSwapTest` |
| title_zh / en | DestructiveSwapTest / DestructiveSwapTest |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.DestructiveSwapTest |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/DestructiveSwapTest/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `DestructiveSwapTest`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/DestructiveSwapTest/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 221 / 295 — `api.protocols.classes.SwapTest`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / SwapTest` |
| slug | `SwapTest` |
| title_zh / en | SwapTest / SwapTest |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.SwapTest |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/SwapTest/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `SwapTest`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/SwapTest/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 222 / 295 — `api.protocols.classes.HadamardTestOverlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / HadamardTestOverlap` |
| slug | `HadamardTestOverlap` |
| title_zh / en | HadamardTestOverlap / HadamardTestOverlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.HadamardTestOverlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/HadamardTestOverlap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `HadamardTestOverlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/HadamardTestOverlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 223 / 295 — `api.protocols.classes.FactorizedOverlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / FactorizedOverlap` |
| slug | `FactorizedOverlap` |
| title_zh / en | FactorizedOverlap / FactorizedOverlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.FactorizedOverlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/FactorizedOverlap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `FactorizedOverlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/FactorizedOverlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 224 / 295 — `api.protocols.classes.SwapFactorizedOverlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / SwapFactorizedOverlap` |
| slug | `SwapFactorizedOverlap` |
| title_zh / en | SwapFactorizedOverlap / SwapFactorizedOverlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.SwapFactorizedOverlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/SwapFactorizedOverlap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `SwapFactorizedOverlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/SwapFactorizedOverlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 225 / 295 — `api.protocols.classes.ComputeUncomputeFactorizedOverlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / ComputeUncomputeFactorizedOverlap` |
| slug | `ComputeUncomputeFactorizedOverlap` |
| title_zh / en | ComputeUncomputeFactorizedOverlap / ComputeUncomputeFactorizedOverlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.ComputeUncomputeFactorizedOverlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/ComputeUncomputeFactorizedOverlap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `ComputeUncomputeFactorizedOverlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/ComputeUncomputeFactorizedOverlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 226 / 295 — `api.protocols.classes.SparseStatevectorProtocol`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / SparseStatevectorProtocol` |
| slug | `SparseStatevectorProtocol` |
| title_zh / en | SparseStatevectorProtocol / SparseStatevectorProtocol |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.SparseStatevectorProtocol |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/SparseStatevectorProtocol/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `SparseStatevectorProtocol`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `BackendStatevectorProtocol` — BackendStatevectorProtocol（BackendStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/SparseStatevectorProtocol/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 227 / 295 — `api.protocols.classes.BackendStatevectorProtocol`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / BackendStatevectorProtocol` |
| slug | `BackendStatevectorProtocol` |
| title_zh / en | BackendStatevectorProtocol / BackendStatevectorProtocol |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.BackendStatevectorProtocol |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/BackendStatevectorProtocol/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `BackendStatevectorProtocol`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/BackendStatevectorProtocol/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 228 / 295 — `api.protocols.classes.SymbolicProtocol`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / SymbolicProtocol` |
| slug | `SymbolicProtocol` |
| title_zh / en | SymbolicProtocol / SymbolicProtocol |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.SymbolicProtocol |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/SymbolicProtocol/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `SymbolicProtocol`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/SymbolicProtocol/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 229 / 295 — `api.protocols.classes.HadamardTestDerivativeOverlap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / HadamardTestDerivativeOverlap` |
| slug | `HadamardTestDerivativeOverlap` |
| title_zh / en | HadamardTestDerivativeOverlap / HadamardTestDerivativeOverlap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.HadamardTestDerivativeOverlap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/HadamardTestDerivativeOverlap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `HadamardTestDerivativeOverlap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/HadamardTestDerivativeOverlap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 230 / 295 — `api.protocols.classes.HadamardTestDerivative`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / HadamardTestDerivative` |
| slug | `HadamardTestDerivative` |
| title_zh / en | HadamardTestDerivative / HadamardTestDerivative |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.HadamardTestDerivative |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/HadamardTestDerivative/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `HadamardTestDerivative`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/HadamardTestDerivative/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 231 / 295 — `api.protocols.classes.CanonicalPhaseEstimation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / CanonicalPhaseEstimation` |
| slug | `CanonicalPhaseEstimation` |
| title_zh / en | CanonicalPhaseEstimation / CanonicalPhaseEstimation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.CanonicalPhaseEstimation |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/CanonicalPhaseEstimation/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `CanonicalPhaseEstimation`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/CanonicalPhaseEstimation/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 232 / 295 — `api.protocols.classes.IterativePhaseEstimation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / IterativePhaseEstimation` |
| slug | `IterativePhaseEstimation` |
| title_zh / en | IterativePhaseEstimation / IterativePhaseEstimation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.IterativePhaseEstimation |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/IterativePhaseEstimation/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `IterativePhaseEstimation`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/IterativePhaseEstimation/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 233 / 295 — `api.protocols.classes.IterativePhaseEstimationSingleCircuit`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / IterativePhaseEstimationSingleCircuit` |
| slug | `IterativePhaseEstimationSingleCircuit` |
| title_zh / en | IterativePhaseEstimationSingleCircuit / IterativePhaseEstimationSingleCircuit |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.IterativePhaseEstimationSingleCircuit |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/IterativePhaseEstimationSingleCircuit/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `IterativePhaseEstimationSingleCircuit`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/IterativePhaseEstimationSingleCircuit/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 234 / 295 — `api.protocols.classes.IterativePhaseEstimationQuantinuum`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / IterativePhaseEstimationQuantinuum` |
| slug | `IterativePhaseEstimationQuantinuum` |
| title_zh / en | IterativePhaseEstimationQuantinuum / IterativePhaseEstimationQuantinuum |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.IterativePhaseEstimationQuantinuum |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/IterativePhaseEstimationQuantinuum/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `IterativePhaseEstimationQuantinuum`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/IterativePhaseEstimationQuantinuum/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 235 / 295 — `api.protocols.classes.IterativePhaseEstimationStatevector`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / IterativePhaseEstimationStatevector` |
| slug | `IterativePhaseEstimationStatevector` |
| title_zh / en | IterativePhaseEstimationStatevector / IterativePhaseEstimationStatevector |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.IterativePhaseEstimationStatevector |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/IterativePhaseEstimationStatevector/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `IterativePhaseEstimationStatevector`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/IterativePhaseEstimationStatevector/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 236 / 295 — `api.protocols.classes.ProjectiveMeasurements`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / ProjectiveMeasurements` |
| slug | `ProjectiveMeasurements` |
| title_zh / en | ProjectiveMeasurements / ProjectiveMeasurements |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.ProjectiveMeasurements |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/ProjectiveMeasurements/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `ProjectiveMeasurements`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/ProjectiveMeasurements/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 237 / 295 — `api.protocols.classes.ProtocolList`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / ProtocolList` |
| slug | `ProtocolList` |
| title_zh / en | ProtocolList / ProtocolList |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.ProtocolList |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/ProtocolList/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `ProtocolList`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/ProtocolList/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 238 / 295 — `api.protocols.classes.PMSV`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / PMSV` |
| slug | `PMSV` |
| title_zh / en | PMSV / PMSV |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.PMSV |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/PMSV/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `PMSV`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.mitigation.pmsv`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/PMSV/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 239 / 295 — `api.protocols.classes.SPAM`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / SPAM` |
| slug | `SPAM` |
| title_zh / en | SPAM / SPAM |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.SPAM |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/SPAM/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `SPAM`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.mitigation.spam`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/SPAM/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 240 / 295 — `api.protocols.classes.CombinedMitigation`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / CombinedMitigation` |
| slug | `CombinedMitigation` |
| title_zh / en | CombinedMitigation / CombinedMitigation |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.CombinedMitigation |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/CombinedMitigation/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `CombinedMitigation`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/CombinedMitigation/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 241 / 295 — `api.protocols.classes.BackendResultBootstrap`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / BackendResultBootstrap` |
| slug | `BackendResultBootstrap` |
| title_zh / en | BackendResultBootstrap / BackendResultBootstrap |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.BackendResultBootstrap |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/BackendResultBootstrap/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `BackendResultBootstrap`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/BackendResultBootstrap/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 242 / 295 — `api.protocols.classes.BackendResultSplit`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / protocols / classes / BackendResultSplit` |
| slug | `BackendResultSplit` |
| title_zh / en | BackendResultSplit / BackendResultSplit |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html#inquanto.protocols.BackendResultSplit |
| pillar / diataxis / class_leaf | P2 / reference / yes |
| mirror_path | `/mirror/api/protocols/classes/BackendResultSplit/` |

- **L1 分区**: `api` → **L2..n**: `protocols` → `classes` → `BackendResultSplit`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `PauliAveraging` — PauliAveraging（PauliAveraging）· `shipped` · class-leaf
- `HadamardTest` — HadamardTest（HadamardTest）· `partial` · class-leaf
- `ComputeUncompute` — ComputeUncompute（ComputeUncompute）· `placeholder` · class-leaf
- `DestructiveSwapTest` — DestructiveSwapTest（DestructiveSwapTest）· `placeholder` · class-leaf
- `SwapTest` — SwapTest（SwapTest）· `placeholder` · class-leaf
- `HadamardTestOverlap` — HadamardTestOverlap（HadamardTestOverlap）· `placeholder` · class-leaf
- `FactorizedOverlap` — FactorizedOverlap（FactorizedOverlap）· `placeholder` · class-leaf
- `SwapFactorizedOverlap` — SwapFactorizedOverlap（SwapFactorizedOverlap）· `placeholder` · class-leaf
- `ComputeUncomputeFactorizedOverlap` — ComputeUncomputeFactorizedOverlap（ComputeUncomputeFactorizedOverlap）· `placeholder` · class-leaf
- `SparseStatevectorProtocol` — SparseStatevectorProtocol（SparseStatevectorProtocol）· `partial` · class-leaf
- _… 另有 15 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/protocols/classes/BackendResultSplit/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 243 / 295 — `api.extensions_pyscf`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf` |
| slug | `extensions_pyscf` |
| title_zh / en | 参考 API · inquanto.extensions.pyscf / Reference API · inquanto.extensions.pyscf |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/api/extensions_pyscf/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.chem.drivers.pyscf_driver`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 244 / 295 — `api.extensions_pyscf.classes.AVAS`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / AVAS` |
| slug | `AVAS` |
| title_zh / en | AVAS / AVAS |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.AVAS |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/AVAS/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `AVAS`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/AVAS/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 245 / 295 — `api.extensions_pyscf.classes.CASSCF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / CASSCF` |
| slug | `CASSCF` |
| title_zh / en | CASSCF / CASSCF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.CASSCF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/CASSCF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `CASSCF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/CASSCF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 246 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularRHF` |
| slug | `ChemistryDriverPySCFMolecularRHF` |
| title_zh / en | ChemistryDriverPySCFMolecularRHF / ChemistryDriverPySCFMolecularRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 247 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularROHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularROHF` |
| slug | `ChemistryDriverPySCFMolecularROHF` |
| title_zh / en | ChemistryDriverPySCFMolecularROHF / ChemistryDriverPySCFMolecularROHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularROHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularROHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularROHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularROHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 248 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularUHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularUHF` |
| slug | `ChemistryDriverPySCFMolecularUHF` |
| title_zh / en | ChemistryDriverPySCFMolecularUHF / ChemistryDriverPySCFMolecularUHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularUHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularUHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularUHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q3 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularUHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q3 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 249 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularRHFQMMMCOSMO`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularRHFQMMMCOSMO` |
| slug | `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` |
| title_zh / en | ChemistryDriverPySCFMolecularRHFQMMMCOSMO / ChemistryDriverPySCFMolecularRHFQMMMCOSMO |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularRHFQMMMCOSMO |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularRHFQMMMCOSMO/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularRHFQMMMCOSMO`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularRHFQMMMCOSMO/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 250 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularROHFQMMMCOSMO`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularROHFQMMMCOSMO` |
| slug | `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` |
| title_zh / en | ChemistryDriverPySCFMolecularROHFQMMMCOSMO / ChemistryDriverPySCFMolecularROHFQMMMCOSMO |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularROHFQMMMCOSMO |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularROHFQMMMCOSMO/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularROHFQMMMCOSMO`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularROHFQMMMCOSMO/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 251 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMolecularUHFQMMMCOSMO`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMolecularUHFQMMMCOSMO` |
| slug | `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` |
| title_zh / en | ChemistryDriverPySCFMolecularUHFQMMMCOSMO / ChemistryDriverPySCFMolecularUHFQMMMCOSMO |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMolecularUHFQMMMCOSMO |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularUHFQMMMCOSMO/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMolecularUHFQMMMCOSMO`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMolecularUHFQMMMCOSMO/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 252 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFGammaRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFGammaRHF` |
| slug | `ChemistryDriverPySCFGammaRHF` |
| title_zh / en | ChemistryDriverPySCFGammaRHF / ChemistryDriverPySCFGammaRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFGammaRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFGammaRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFGammaRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFGammaRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 253 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFGammaROHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFGammaROHF` |
| slug | `ChemistryDriverPySCFGammaROHF` |
| title_zh / en | ChemistryDriverPySCFGammaROHF / ChemistryDriverPySCFGammaROHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFGammaROHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFGammaROHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFGammaROHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMomentumRHF` — ChemistryDriverPySCFMomentumRHF（ChemistryDriverPySCFMomentumRHF）· `partial` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFGammaROHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 254 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMomentumRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMomentumRHF` |
| slug | `ChemistryDriverPySCFMomentumRHF` |
| title_zh / en | ChemistryDriverPySCFMomentumRHF / ChemistryDriverPySCFMomentumRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMomentumRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMomentumRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMomentumRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMomentumRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 255 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFMomentumROHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFMomentumROHF` |
| slug | `ChemistryDriverPySCFMomentumROHF` |
| title_zh / en | ChemistryDriverPySCFMomentumROHF / ChemistryDriverPySCFMomentumROHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFMomentumROHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMomentumROHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFMomentumROHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFMomentumROHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 256 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFEmbeddingRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFEmbeddingRHF` |
| slug | `ChemistryDriverPySCFEmbeddingRHF` |
| title_zh / en | ChemistryDriverPySCFEmbeddingRHF / ChemistryDriverPySCFEmbeddingRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFEmbeddingRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFEmbeddingRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 257 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFEmbeddingROHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFEmbeddingROHF` |
| slug | `ChemistryDriverPySCFEmbeddingROHF` |
| title_zh / en | ChemistryDriverPySCFEmbeddingROHF / ChemistryDriverPySCFEmbeddingROHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFEmbeddingROHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingROHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFEmbeddingROHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingROHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 258 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFEmbeddingROHF_UHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFEmbeddingROHF_UHF` |
| slug | `ChemistryDriverPySCFEmbeddingROHF_UHF` |
| title_zh / en | ChemistryDriverPySCFEmbeddingROHF_UHF / ChemistryDriverPySCFEmbeddingROHF_UHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFEmbeddingROHF_UHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingROHF_UHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFEmbeddingROHF_UHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingROHF_UHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 259 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFEmbeddingGammaRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFEmbeddingGammaRHF` |
| slug | `ChemistryDriverPySCFEmbeddingGammaRHF` |
| title_zh / en | ChemistryDriverPySCFEmbeddingGammaRHF / ChemistryDriverPySCFEmbeddingGammaRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFEmbeddingGammaRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingGammaRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFEmbeddingGammaRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingGammaRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 260 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFEmbeddingGammaROHF_UHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFEmbeddingGammaROHF_UHF` |
| slug | `ChemistryDriverPySCFEmbeddingGammaROHF_UHF` |
| title_zh / en | ChemistryDriverPySCFEmbeddingGammaROHF_UHF / ChemistryDriverPySCFEmbeddingGammaROHF_UHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFEmbeddingGammaROHF_UHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingGammaROHF_UHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFEmbeddingGammaROHF_UHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFEmbeddingGammaROHF_UHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 261 / 295 — `api.extensions_pyscf.classes.ChemistryDriverPySCFIntegrals`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ChemistryDriverPySCFIntegrals` |
| slug | `ChemistryDriverPySCFIntegrals` |
| title_zh / en | ChemistryDriverPySCFIntegrals / ChemistryDriverPySCFIntegrals |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ChemistryDriverPySCFIntegrals |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFIntegrals/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ChemistryDriverPySCFIntegrals`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ChemistryDriverPySCFIntegrals/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 262 / 295 — `api.extensions_pyscf.classes.DMETRHFFragmentPySCFActive`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / DMETRHFFragmentPySCFActive` |
| slug | `DMETRHFFragmentPySCFActive` |
| title_zh / en | DMETRHFFragmentPySCFActive / DMETRHFFragmentPySCFActive |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.DMETRHFFragmentPySCFActive |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFActive/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `DMETRHFFragmentPySCFActive`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFActive/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 263 / 295 — `api.extensions_pyscf.classes.DMETRHFFragmentPySCFCCSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / DMETRHFFragmentPySCFCCSD` |
| slug | `DMETRHFFragmentPySCFCCSD` |
| title_zh / en | DMETRHFFragmentPySCFCCSD / DMETRHFFragmentPySCFCCSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.DMETRHFFragmentPySCFCCSD |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFCCSD/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `DMETRHFFragmentPySCFCCSD`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFCCSD/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 264 / 295 — `api.extensions_pyscf.classes.DMETRHFFragmentPySCFFCI`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / DMETRHFFragmentPySCFFCI` |
| slug | `DMETRHFFragmentPySCFFCI` |
| title_zh / en | DMETRHFFragmentPySCFFCI / DMETRHFFragmentPySCFFCI |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.DMETRHFFragmentPySCFFCI |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFFCI/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `DMETRHFFragmentPySCFFCI`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFFCI/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 265 / 295 — `api.extensions_pyscf.classes.DMETRHFFragmentPySCFMP2`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / DMETRHFFragmentPySCFMP2` |
| slug | `DMETRHFFragmentPySCFMP2` |
| title_zh / en | DMETRHFFragmentPySCFMP2 / DMETRHFFragmentPySCFMP2 |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.DMETRHFFragmentPySCFMP2 |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFMP2/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `DMETRHFFragmentPySCFMP2`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: Q4 2026
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFMP2/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 Q4 2026 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 266 / 295 — `api.extensions_pyscf.classes.DMETRHFFragmentPySCFRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / DMETRHFFragmentPySCFRHF` |
| slug | `DMETRHFFragmentPySCFRHF` |
| title_zh / en | DMETRHFFragmentPySCFRHF / DMETRHFFragmentPySCFRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.DMETRHFFragmentPySCFRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `DMETRHFFragmentPySCFRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/DMETRHFFragmentPySCFRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 267 / 295 — `api.extensions_pyscf.classes.ImpurityDMETROHFFragmentPySCFActive`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ImpurityDMETROHFFragmentPySCFActive` |
| slug | `ImpurityDMETROHFFragmentPySCFActive` |
| title_zh / en | ImpurityDMETROHFFragmentPySCFActive / ImpurityDMETROHFFragmentPySCFActive |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ImpurityDMETROHFFragmentPySCFActive |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFActive/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ImpurityDMETROHFFragmentPySCFActive`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFActive/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 268 / 295 — `api.extensions_pyscf.classes.ImpurityDMETROHFFragmentPySCFCCSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ImpurityDMETROHFFragmentPySCFCCSD` |
| slug | `ImpurityDMETROHFFragmentPySCFCCSD` |
| title_zh / en | ImpurityDMETROHFFragmentPySCFCCSD / ImpurityDMETROHFFragmentPySCFCCSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ImpurityDMETROHFFragmentPySCFCCSD |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFCCSD/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ImpurityDMETROHFFragmentPySCFCCSD`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFCCSD/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 269 / 295 — `api.extensions_pyscf.classes.ImpurityDMETROHFFragmentPySCFFCI`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ImpurityDMETROHFFragmentPySCFFCI` |
| slug | `ImpurityDMETROHFFragmentPySCFFCI` |
| title_zh / en | ImpurityDMETROHFFragmentPySCFFCI / ImpurityDMETROHFFragmentPySCFFCI |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ImpurityDMETROHFFragmentPySCFFCI |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFFCI/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ImpurityDMETROHFFragmentPySCFFCI`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFFCI/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 270 / 295 — `api.extensions_pyscf.classes.ImpurityDMETROHFFragmentPySCFMP2`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ImpurityDMETROHFFragmentPySCFMP2` |
| slug | `ImpurityDMETROHFFragmentPySCFMP2` |
| title_zh / en | ImpurityDMETROHFFragmentPySCFMP2 / ImpurityDMETROHFFragmentPySCFMP2 |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ImpurityDMETROHFFragmentPySCFMP2 |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFMP2/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ImpurityDMETROHFFragmentPySCFMP2`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFMP2/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 271 / 295 — `api.extensions_pyscf.classes.ImpurityDMETROHFFragmentPySCFROHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / ImpurityDMETROHFFragmentPySCFROHF` |
| slug | `ImpurityDMETROHFFragmentPySCFROHF` |
| title_zh / en | ImpurityDMETROHFFragmentPySCFROHF / ImpurityDMETROHFFragmentPySCFROHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.ImpurityDMETROHFFragmentPySCFROHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFROHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `ImpurityDMETROHFFragmentPySCFROHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/ImpurityDMETROHFFragmentPySCFROHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 272 / 295 — `api.extensions_pyscf.classes.FromActiveOrbitals`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FromActiveOrbitals` |
| slug | `FromActiveOrbitals` |
| title_zh / en | FromActiveOrbitals / FromActiveOrbitals |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FromActiveOrbitals |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FromActiveOrbitals/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FromActiveOrbitals`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FromActiveOrbitals/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 273 / 295 — `api.extensions_pyscf.classes.FromActiveSpace`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FromActiveSpace` |
| slug | `FromActiveSpace` |
| title_zh / en | FromActiveSpace / FromActiveSpace |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FromActiveSpace |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FromActiveSpace/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FromActiveSpace`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FromActiveSpace/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 274 / 295 — `api.extensions_pyscf.classes.FrozenCore`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FrozenCore` |
| slug | `FrozenCore` |
| title_zh / en | FrozenCore / FrozenCore |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FrozenCore |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FrozenCore/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FrozenCore`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FrozenCore/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 275 / 295 — `api.extensions_pyscf.classes.FMO`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMO` |
| slug | `FMO` |
| title_zh / en | FMO / FMO |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMO |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMO/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMO`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMO/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 276 / 295 — `api.extensions_pyscf.classes.FMOFragment`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMOFragment` |
| slug | `FMOFragment` |
| title_zh / en | FMOFragment / FMOFragment |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMOFragment |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMOFragment/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMOFragment`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMOFragment/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 277 / 295 — `api.extensions_pyscf.classes.FMOFragmentPySCFActive`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMOFragmentPySCFActive` |
| slug | `FMOFragmentPySCFActive` |
| title_zh / en | FMOFragmentPySCFActive / FMOFragmentPySCFActive |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMOFragmentPySCFActive |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFActive/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMOFragmentPySCFActive`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFActive/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 278 / 295 — `api.extensions_pyscf.classes.FMOFragmentPySCFCCSD`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMOFragmentPySCFCCSD` |
| slug | `FMOFragmentPySCFCCSD` |
| title_zh / en | FMOFragmentPySCFCCSD / FMOFragmentPySCFCCSD |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMOFragmentPySCFCCSD |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFCCSD/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMOFragmentPySCFCCSD`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFCCSD/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 279 / 295 — `api.extensions_pyscf.classes.FMOFragmentPySCFMP2`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMOFragmentPySCFMP2` |
| slug | `FMOFragmentPySCFMP2` |
| title_zh / en | FMOFragmentPySCFMP2 / FMOFragmentPySCFMP2 |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMOFragmentPySCFMP2 |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFMP2/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMOFragmentPySCFMP2`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFMP2/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 280 / 295 — `api.extensions_pyscf.classes.FMOFragmentPySCFRHF`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / FMOFragmentPySCFRHF` |
| slug | `FMOFragmentPySCFRHF` |
| title_zh / en | FMOFragmentPySCFRHF / FMOFragmentPySCFRHF |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.FMOFragmentPySCFRHF |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFRHF/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `FMOFragmentPySCFRHF`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/FMOFragmentPySCFRHF/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 281 / 295 — `api.extensions_pyscf.classes.PySCFChemistryRestrictedIntegralOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / PySCFChemistryRestrictedIntegralOperator` |
| slug | `PySCFChemistryRestrictedIntegralOperator` |
| title_zh / en | PySCFChemistryRestrictedIntegralOperator / PySCFChemistryRestrictedIntegralOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.PySCFChemistryRestrictedIntegralOperator |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/PySCFChemistryRestrictedIntegralOperator/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `PySCFChemistryRestrictedIntegralOperator`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/PySCFChemistryRestrictedIntegralOperator/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 282 / 295 — `api.extensions_pyscf.classes.PySCFChemistryUnrestrictedIntegralOperator`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_pyscf / classes / PySCFChemistryUnrestrictedIntegralOperator` |
| slug | `PySCFChemistryUnrestrictedIntegralOperator` |
| title_zh / en | PySCFChemistryUnrestrictedIntegralOperator / PySCFChemistryUnrestrictedIntegralOperator |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.PySCFChemistryUnrestrictedIntegralOperator |
| pillar / diataxis / class_leaf | P1 / reference / yes |
| mirror_path | `/mirror/api/extensions_pyscf/classes/PySCFChemistryUnrestrictedIntegralOperator/` |

- **L1 分区**: `api` → **L2..n**: `extensions_pyscf` → `classes` → `PySCFChemistryUnrestrictedIntegralOperator`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `AVAS` — AVAS（AVAS）· `shipped` · class-leaf
- `CASSCF` — CASSCF（CASSCF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularRHF` — ChemistryDriverPySCFMolecularRHF（ChemistryDriverPySCFMolecularRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHF` — ChemistryDriverPySCFMolecularROHF（ChemistryDriverPySCFMolecularROHF）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularUHF` — ChemistryDriverPySCFMolecularUHF（ChemistryDriverPySCFMolecularUHF）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularRHFQMMMCOSMO` — ChemistryDriverPySCFMolecularRHFQMMMCOSMO（ChemistryDriverPySCFMolecularRHFQMMMCOSMO）· `partial` · class-leaf
- `ChemistryDriverPySCFMolecularROHFQMMMCOSMO` — ChemistryDriverPySCFMolecularROHFQMMMCOSMO（ChemistryDriverPySCFMolecularROHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFMolecularUHFQMMMCOSMO` — ChemistryDriverPySCFMolecularUHFQMMMCOSMO（ChemistryDriverPySCFMolecularUHFQMMMCOSMO）· `placeholder` · class-leaf
- `ChemistryDriverPySCFGammaRHF` — ChemistryDriverPySCFGammaRHF（ChemistryDriverPySCFGammaRHF）· `partial` · class-leaf
- `ChemistryDriverPySCFGammaROHF` — ChemistryDriverPySCFGammaROHF（ChemistryDriverPySCFGammaROHF）· `placeholder` · class-leaf
- _… 另有 28 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_pyscf/classes/PySCFChemistryUnrestrictedIntegralOperator/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] 里程碑 TBD 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 283 / 295 — `api.extensions_cutensornet`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_cutensornet` |
| slug | `extensions_cutensornet` |
| title_zh / en | 参考 API · inquanto.extensions.cutensornet / Reference API · inquanto.extensions.cutensornet |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-cutensornet_api.html |
| pillar / diataxis / class_leaf | P3 / reference / no |
| mirror_path | `/mirror/api/extensions_cutensornet/` |

- **L1 分区**: `api` → **L2..n**: `extensions_cutensornet`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.tensornet`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_cutensornet/`
- **四柱指南**: `/guide/execution-and-analysis/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 284 / 295 — `api.extensions_cutensornet.classes.CuTensorNetProtocol`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_cutensornet / classes / CuTensorNetProtocol` |
| slug | `CuTensorNetProtocol` |
| title_zh / en | CuTensorNetProtocol / CuTensorNetProtocol |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-cutensornet_api.html#inquanto.extensions.cutensornet.CuTensorNetProtocol |
| pillar / diataxis / class_leaf | P3 / reference / yes |
| mirror_path | `/mirror/api/extensions_cutensornet/classes/CuTensorNetProtocol/` |

- **L1 分区**: `api` → **L2..n**: `extensions_cutensornet` → `classes` → `CuTensorNetProtocol`
- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）
- **Secondary**: 资源估计与硬件集成者
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

_（manifest 中此父节点下无其它兄弟项）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块（manifest `qchem`）**:
  - `qchem_stack.tensornet.cutensornet_protocol_stub`
- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。

- **status（manifest）**: `partial`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_cutensornet/classes/CuTensorNetProtocol/`
- **四柱指南**: `/guide/execution-and-analysis/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。
- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。

- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。
- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 285 / 295 — `api.extensions_nexus`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_nexus` |
| slug | `extensions_nexus` |
| title_zh / en | 参考 API · inquanto.extensions.nexus / Reference API · inquanto.extensions.nexus |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-nexus_api.html |
| pillar / diataxis / class_leaf | P4 / reference / no |
| mirror_path | `/mirror/api/extensions_nexus/` |

- **L1 分区**: `api` → **L2..n**: `extensions_nexus`
- **Primary**: 平台与 DevOps（作业队列、API、可复现导出）
- **Secondary**: 合作方尽调 / 合规读者
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 真云不在范围；本地 FastAPI / SQLite 类比见 P4。
- **reason_en**: Real cloud out of scope; see local FastAPI / SQLite analog under P4.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_nexus/`
- **四柱指南**: `/guide/jobs-and-reproducibility/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。
- **P4**: `GET/POST /v1/runs`、`repro` 须有 **API 表或控制台等价说明**。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 286 / 295 — `api.extensions_phayes`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_phayes` |
| slug | `extensions_phayes` |
| title_zh / en | 参考 API · inquanto.extensions.phayes / Reference API · inquanto.extensions.phayes |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-phayes_api.html |
| pillar / diataxis / class_leaf | P2 / reference / no |
| mirror_path | `/mirror/api/extensions_phayes/` |

- **L1 分区**: `api` → **L2..n**: `extensions_phayes`
- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）
- **Secondary**: 应用数学家（优化器、激发态、QPE）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `placeholder`
- **milestone**: 2027
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_phayes/`
- **四柱指南**: `/guide/algorithms-and-protocols/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。

- [ ] 里程碑 2027 前：最小 API / YAML 样例落地。
- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 287 / 295 — `api.extensions_nglview`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `api / extensions_nglview` |
| slug | `extensions_nglview` |
| title_zh / en | 参考 API · inquanto.extensions.nglview / Reference API · inquanto.extensions.nglview |
| reference_doc_url | https://docs.quantinuum.com/inquanto/api/extensions/inquanto-nglview_api.html |
| pillar / diataxis / class_leaf | P1 / reference / no |
| mirror_path | `/mirror/api/extensions_nglview/` |

- **L1 分区**: `api` → **L2..n**: `extensions_nglview`
- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）
- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）
- **顶层分区（manifest）**: `api`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。
- Python 类型注解与包导入路径阅读经验。
- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。
- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。

## 2. 同级兄弟（manifest 同父）

- `api_intro_inquanto` — Reference documentation · API overview（参考文档 · API 总览）· `shipped`
- `api_intro_extensions` — Reference documentation · Extensions API overview（参考文档 · 扩展 API 总览）· `shipped`
- `algorithms` — Reference API · inquanto.algorithms（参考 API · inquanto.algorithms）· `partial`
- `ansatz` — Reference API · inquanto.ansatzes（参考 API · inquanto.ansatzes）· `partial`
- `computables` — Reference API · inquanto.computables（参考 API · inquanto.computables）· `partial`
- `operators` — Reference API · inquanto.operators（参考 API · inquanto.operators）· `partial`
- `spaces` — Reference API · inquanto.spaces（参考 API · inquanto.spaces）· `partial`
- `states` — Reference API · inquanto.states（参考 API · inquanto.states）· `partial`
- `mappings` — Reference API · inquanto.mappings（参考 API · inquanto.mappings）· `partial`
- `minimizers` — Reference API · inquanto.minimizers（参考 API · inquanto.minimizers）· `partial`
- _… 另有 11 个兄弟项（见 appendix-B TSV 同父路径）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/api/extensions_nglview/`
- **四柱指南**: `/guide/chemistry-and-embedding/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 288 / 295 — `misc`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc` |
| slug | `misc` |
| title_zh / en | 杂项 / Misc |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/ |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/` |

- **L1 分区**: `misc` → **L2..n**: _根_
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

_（根段无同级兄弟；见 manifest 顶层键）_

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 289 / 295 — `misc.release_notes`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / release_notes` |
| slug | `release_notes` |
| title_zh / en | 发行说明 / Release notes |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/changelog.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/release_notes/` |

- **L1 分区**: `misc` → **L2..n**: `release_notes`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `bibliography` — Bibliography（参考文献）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `license` — License / Changelog（许可与版本）· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/release_notes/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 290 / 295 — `misc.bibliography`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / bibliography` |
| slug | `bibliography` |
| title_zh / en | 参考文献 / Bibliography |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/bibliography.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/bibliography/` |

- **L1 分区**: `misc` → **L2..n**: `bibliography`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `license` — License / Changelog（许可与版本）· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/bibliography/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 291 / 295 — `misc.contact_docs`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / contact_docs` |
| slug | `contact_docs` |
| title_zh / en | 联系支持（文档内页） / Contact support (in-docs) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/contact.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/contact_docs/` |

- **L1 分区**: `misc` → **L2..n**: `contact_docs`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `bibliography` — Bibliography（参考文献）· `shipped`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `license` — License / Changelog（许可与版本）· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `not-applicable`
- **milestone**: —
- **reason_zh**: 厂商工单入口；我们站以 issue/discussion 替代。
- **reason_en**: Vendor ticket entry; we use issues/discussions instead.
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/contact_docs/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。
- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] `reason_*` 与法务/产品口径一致。
- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 292 / 295 — `misc.how_to_cite`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / how_to_cite` |
| slug | `how_to_cite` |
| title_zh / en | 文献引用说明（参考镜像） / Citing upstream documentation (mirror) |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/cite.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/how_to_cite/` |

- **L1 分区**: `misc` → **L2..n**: `how_to_cite`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `bibliography` — Bibliography（参考文献）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `license` — License / Changelog（许可与版本）· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/how_to_cite/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 293 / 295 — `misc.license`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / license` |
| slug | `license` |
| title_zh / en | 许可与版本 / License / Changelog |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/license.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/license/` |

- **L1 分区**: `misc` → **L2..n**: `license`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `bibliography` — Bibliography（参考文献）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/license/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 294 / 295 — `misc.opensource_attribution`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / opensource_attribution` |
| slug | `opensource_attribution` |
| title_zh / en | 开源组件归属 / Open-source attribution |
| reference_doc_url | https://docs.quantinuum.com/inquanto/misc/opensource.html |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/opensource_attribution/` |

- **L1 分区**: `misc` → **L2..n**: `opensource_attribution`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `bibliography` — Bibliography（参考文献）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `license` — License / Changelog（许可与版本）· `shipped`
- `contact` — Contact (corporate portal)（联系我们（官网门户））· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/opensource_attribution/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---

# 节点 295 / 295 — `misc.contact`

## 1. 标识、InQuanto IA 位置、读者与阅读路径

| 字段 | 值 |
| --- | --- |
| breadcrumb | `misc / contact` |
| slug | `contact` |
| title_zh / en | 联系我们（官网门户） / Contact (corporate portal) |
| reference_doc_url | https://www.quantinuum.com/contact/docs |
| pillar / diataxis / class_leaf | meta / reference / no |
| mirror_path | `/mirror/misc/contact/` |

- **L1 分区**: `misc` → **L2..n**: `contact`
- **Primary**: 信息架构与导航读者（总览、书目、许可）
- **Secondary**: 首次到访者（introduction）
- **顶层分区（manifest）**: `misc`
- **Diátaxis 标签（manifest）**: `reference` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。
- **节点类型**: **杂项或元信息** — 许可、联系、书目等。
- 依赖随分区变化；以 InQuanto 公开页前置说明为准。
- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。
- **典型出链**: 全站页脚 Support / Publications。
- **典型入链**: 根 hub。

## 2. 同级兄弟（manifest 同父）

- `release_notes` — Release notes（发行说明）· `shipped`
- `bibliography` — Bibliography（参考文献）· `shipped`
- `contact_docs` — Contact support (in-docs)（联系支持（文档内页））· `not-applicable`
- `how_to_cite` — Citing upstream documentation (mirror)（文献引用说明（参考镜像））· `shipped`
- `license` — License / Changelog（许可与版本）· `shipped`
- `opensource_attribution` — Open-source attribution（开源组件归属）· `shipped`

## 3. qchem_stack 映射、Parity、自有站 IA

- **已绑定模块**: _manifest 未填 `qchem`_。
- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。

- **status（manifest）**: `shipped`
- **milestone**: —
- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。

- **Mirror（审计）**: 必选 — `/mirror/misc/contact/`
- **四柱指南**: `/guide/` 总览 + `/product/`
- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。

### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）

- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。
- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。
- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。
- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 docs-site/docs/meta/ia-mapping.md 为真源。
- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。
- **CI**: 外链存活巡检；教程命令可选 smoke。

## 4. 风险与验收

- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。

- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。
- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。
- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。

## 5. 开放问题

- [ ] 公开页自 `source_pin_date` 以来是否结构重排？
- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？

---
