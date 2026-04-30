# Vol.10 官方侧栏真源 ↔ manifest 闭合集

**读者**：架构师、负责 mirror / parity 的工程 owner。  
**目的**：把「**全站每一个 Sphinx 导航项**」与「**`inquanto-tree.yaml` 扁平节点（= `check:mirror` 条目）**」的关系写清楚，避免附录行数被误读为「已枚举互联网上全部 HTML」。

---

## 1. 官方 IA 的「机器可读真源」是什么

InQuanto 文档由 **Sphinx + Furo** 发布。根营销页 [`https://docs.quantinuum.com/inquanto/`](https://docs.quantinuum.com/inquanto/) 只展示三柱叙事；**完整树**出现在全站 [`search.html`](https://docs.quantinuum.com/inquanto/search.html) 的侧栏（与每页左侧导航同源）。  
**工作约定**：以 **search 页侧栏** 作为「官方公开导航闭包」的 **人类可读真源**；manifest 以 **刻意子集 + 类叶展开** 对齐 **我们产品要对标的 URL**，并允许额外钉扎（如双 contact 入口）。

---

## 2. 2026-04-30 批次已纳入 manifest 的侧栏项（此前缺口）

| 官方侧栏 / URL 形态 | manifest 位置 |
|---------------------|----------------|
| Introduction → What is InQuanto | `introduction.overview` → `introduction/overview.html` |
| Installation / System requirements / Troubleshooting | `introduction.installation` 及子节点 |
| API Reference → InQuanto / Extensions **总览** | `api.api_intro_inquanto`、`api.api_intro_extensions` |
| `inquanto.embeddings`（`embeddings.html`） | `api.embeddings`（**已替换**错误的 `embedding.html`） |
| `inquanto.geometries` | `api.geometries` |
| `inquanto.experiments` + QEC QPE 子页 | `api.experiments` 与 `experiment_qec_qpe` |
| Support → Release notes / Contact (in-docs) / How to cite / Open-source | `misc.release_notes`、`misc.contact_docs`、`misc.how_to_cite`、`misc.opensource_attribution` |

**仍建议人工季度核对**：Sphinx `objects.inv`、`genindex.html`（若启用）、以及 **未进侧栏** 的孤立页面 — 这些 **不保证** 被 manifest 覆盖。

---

## 3. 刻意保留的「双轨」与 n/a

| 现象 | 说明 |
|------|------|
| `misc.contact` vs `misc.contact_docs` | 前者为 **官网门户外链**；后者为 **文档站内 `misc/contact.html`**。我们 mirror 对后者标 **`not-applicable`**，避免假装承接厂商工单。 |
| 节点数 **295**（相对此前 282）主要来自 **新增整页节点**；既有类叶集合未删改 | 节点总数随 manifest 变化；`npm run check:mirror` 与附录 B/C **同一扁平规则**。 |

---

## 4. 与本报告其他卷的衔接

- **Vol.09**：在 manifest 语义下归纳 `api/*` / `misc/*` 模块职责。  
- **附录 B**：全节点 TSV，可筛选 `introduction/`、`misc/`、`api/inquanto_api_intro` 等新行。  
- **Vol.05**：`api/index.html` **404** 仍成立；API 入口为 **模块 HTML** 与 **intro 页**，而非单层 `api/` 目录索引。

---

## 5. 本卷结论

**「细致」= manifest 与官方侧栏 **可对拍** + 附录对 **每个 manifest 节点** 同构拆解**；不等于 **未声明地承诺** 已爬完 Quantinuum 上所有可能 URL。Vol.10 把该边界 **显式化**，便于审计与对外沟通。

**返回**：[`INDEX.md`](./INDEX.md) · 补遗 [`vol-09-api-modules-and-misc-supplement.md`](./vol-09-api-modules-and-misc-supplement.md) · backlog 执行法 [`vol-11-node-backlog-and-waves.md`](./vol-11-node-backlog-and-waves.md)。
