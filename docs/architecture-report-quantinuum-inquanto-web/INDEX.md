# Quantinuum InQuanto 公开文档站 — 软件与网页架构报告（多卷 + 附录）

本目录为 **`qchem_qml_md` 仓库内** 的对标架构规格，用于指导后续「优于 InQuanto 公开站、适配模拟器云平台与量子化学流程」的自有文档站建设。**结构真源** 为 [`docs-site/scripts/mirror-doc-tree.yaml`](../docs-site/scripts/mirror-doc-tree.yaml)（与 `npm run check:mirror`、附录 A/B/C 同源）；manifest 与公开站对拍调整见下方变更记录，并需再跑 `scaffold:mirror` 与 `report:inquanto-appendix`。

**`docs/` 归类入口**（本目录属「生成物与尽调」）：[../与InQuanto能力差距与实施计划.md](../与InQuanto能力差距与实施计划.md)（附录 B–F 为台账/签字/P2 等）· [../竞争定位与路线图_对标Quantinuum产品与技术路线.md](../竞争定位与路线图_对标Quantinuum产品与技术路线.md)。

---

## 阅读顺序

| 顺序 | 文件 | 内容 |
|------|------|------|
| 1 | [vol-00-executive-summary.md](./vol-00-executive-summary.md) | 定位、顶层 IA、与 Nexus 边界 |
| 2 | [vol-01-hub-and-navigation.md](./vol-01-hub-and-navigation.md) | 枢纽三柱、导航、外链、角色分流 |
| 3 | [vol-02-manual-hierarchy.md](./vol-02-manual-hierarchy.md) | Manual 全分支、Protocols 五阶段、依赖 DAG |
| 4 | [vol-03-tutorials-and-case-studies.md](./vol-03-tutorials-and-case-studies.md) | 教程分区、案例研究、Nexus 类教程 |
| 5 | [vol-04-extensions-packaging.md](./vol-04-extensions-packaging.md) | 扩展包叙事与自建扩展建议 |
| 6 | [vol-05-api-reference-patterns.md](./vol-05-api-reference-patterns.md) | API 页模式、大页问题、类叶拆分 |
| 7 | [vol-06-content-types-and-diataxis.md](./vol-06-content-types-and-diataxis.md) | Diátaxis 映射与重复策略 |
| 8 | [vol-07-ux-search-seo-i18n.md](./vol-07-ux-search-seo-i18n.md) | UX、搜索、SEO、与 VitePress 对照 |
| 9 | [vol-08-target-qchem-docs-and-cloud.md](./vol-08-target-qchem-docs-and-cloud.md) | **目标态**：模拟器云 + 四柱 + `/cloud/` 建议 |
| 10 | [vol-09-api-modules-and-misc-supplement.md](./vol-09-api-modules-and-misc-supplement.md) | **补遗**：`api/*` 模块族与 `misc/` 的 manifest 聚合索引 |
| 11 | [vol-10-official-sidebar-vs-manifest.md](./vol-10-official-sidebar-vs-manifest.md) | **对拍**：Furo `search.html` 侧栏 ↔ manifest 边界与双轨说明 |
| 12 | [vol-11-node-backlog-and-waves.md](./vol-11-node-backlog-and-waves.md) | **执行法**：附录 C vs 机读 JSON backlog、Wave、差异化字段 |
| 13 | [appendix-A-full-node-list.generated.md](./appendix-A-full-node-list.generated.md) | **机器生成**：全节点紧凑审计块（~9.7k 行，随节点数变） |
| 14 | [appendix-C-deep-node-architecture.generated.md](./appendix-C-deep-node-architecture.generated.md) | **机器生成**：每节点 **~74 行** 架构拆解（兄弟节点、parity、云检查单等；**~2.17 万行**） |
| 15 | [appendix-B-url-inventory.generated.tsv](./appendix-B-url-inventory.generated.tsv) | TSV：可导入表格工具筛选 |
| — | [`../inquanto-node-backlog.generated.json`](../inquanto-node-backlog.generated.json) | **295 节点机读 backlog**（`npm run report:inquanto-backlog`） |
| — | [`../inquanto-node-backlog.schema.json`](../inquanto-node-backlog.schema.json) | backlog JSON Schema |
| — | [`../inquanto-node-backlog.generated.md`](../inquanto-node-backlog.generated.md) | backlog 紧凑索引表 |

---

## 证据等级与钉扎

- **机器真源**：`mirror-doc-tree.yaml` 内 `site_meta`（`source_pin_date`、`upstream_doc_version_seen`、`source_root`）。
- **已证实**：本报告 Vol.00–01、Protocols、Quick-start、Extensions overview 等 **直接抓取** 的公开 HTML 事实。
- **推断**：Sphinx 技术栈、全站壳层与 Nexus 单点登录、移动端深色模式等 — 已在各卷标注。
- **勿过度声称**：未读过的单页、未公开的构建流水线细节 — 不写入「已证实」。

---

## 附录再生成与行数

在仓库 `docs-site/` 下执行：

```bash
npm run report:inquanto-appendix
npm run report:inquanto-backlog
npm run check:node-backlog
```

默认输出到本目录。最近一次生成统计：**295 个节点**（与 `check:mirror` 与 **node backlog** 一致）。

| 附录 | 行数（约） | 说明 |
|------|------------|------|
| appendix-A | ~9 750 | 元数据表 + 短审计提示 |
| appendix-C | ~21 670 | **每节点完整拆解**（规则模板 + manifest 字段 + 同父兄弟索引；非空话堆砌） |
| appendix-B | 296 行 TSV | 含表头一行 |

**一致性校验**：附录条目数应等于 `npm run check:mirror` 所报 mirror entries 数（当前为 **295**）。再生附录：`cd docs-site && npm run report:inquanto-appendix`。

---

## 与现有 `docs-site` 工程对照（Handoff）

| 报告概念 | 当前实现路径 |
|-----------|--------------|
| 三柱 / 四柱产品叙事 | [`docs/index.md`](../docs-site/docs/index.md)、[`docs/product/`](../docs-site/docs/product/) |
| 公开树审计 | [`docs/mirror/`](../docs-site/docs/mirror/)、`MirrorTree.vue`、`mirror-doc-tree.yaml` |
| 四柱任务指南 | [`docs/guide/`](../docs-site/docs/guide/) |
| Parity / 契约 | [`docs/parity/`](../docs-site/docs/parity/) |
| 模拟器云（占位） | [`docs/cloud/`](../docs-site/docs/cloud/) |
| 站点配置 | [`docs/.vitepress/config.ts`](../docs-site/docs/.vitepress/config.ts) |
| IA  slug 映射 | [`docs-site/docs/meta/ia-mapping.md`](../docs-site/docs/meta/ia-mapping.md)（站内 `/meta/ia-mapping`） |

**后续建议**：按 [vol-08](./vol-08-target-qchem-docs-and-cloud.md) 扩展 `/cloud/` 正文（已建最小占位）；补齐 EN parity 深度页；以本报告结论**收敛**首页 / 产品 / 导航文案，而非把附录全文搬进 VitePress。

---

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-04-29 | 首版：Vol.00–08 + 附录脚本与生成物 |
| 2026-04-29 | 增补 Vol.09；附录 C 压至 ~2.07 万行/282 节点；附录 A 保持 ~9.3k 行 |
| 2026-04-30 | 对齐 Furo 侧栏：补 introduction / misc / API intro、experiments、geometries；**embeddings.html** 修正；Vol.10 对拍；节点 **295** |
| 2026-04-30 | Vol.11 + `inquanto-node-backlog` JSON/Schema；`lib/inquanto-manifest-flatten.mjs` 共享；`/cloud/` 占位 |
