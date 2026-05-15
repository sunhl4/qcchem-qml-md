---
title: SSG 与搜索策略
description: 静态文档框架选型结论、侧边栏与本地搜索的实现方式
---

# 静态站生成与搜索（定稿）

## 1. 框架选型

| 选项 | 结论 |
|------|------|
| VitePress | **已采用**。与 Vue 生态、Markdown 一阶支持、`theme/` 自定义与 `layout-bottom` 等槽位契合当前工程。 |
| Docusaurus / Starlight | 未选：迁移成本高；当前内容已在 VitePress 侧栏与镜像脚手架中稳定运行。 |

**信源**：仓库内 Markdown（`docs-site/docs/**`）为主；`qchem_qml_md/docs/**` 母稿经映射表迁入（见 [IA slug 映射](/meta/ia-mapping)）。

## 2. 侧边栏策略

| 区域 | 策略 |
|------|------|
| 产品 / 指南 / 教程 / Concept / Reference / Parity / Cloud / Meta | **手工维护**于 `docs/.vitepress/config.ts` 的 `themeConfig.locales.*.themeConfig.sidebar`，保证顺序与对外叙事一致。 |
| `/mirror/**`、`/en/mirror/**` | **`sidebar-mirror.json`** 由 `npm run scaffold:mirror` 从 `scripts/mirror-doc-tree.yaml` 生成，避免 295+ 节点手改。 |

## 3. 搜索策略

| 能力 | 实现 |
|------|------|
| 当前 | **VitePress Local Search**（`themeConfig.search.provider: "local"`），随构建索引全站 Markdown。 |
| 体量增长 | 可选 **Algolia DocSearch**：见 `docs-site/README.md`；需在 `config.ts` 配置 `themeConfig.search` 与爬虫。 |
| 镜像子域拆分 | 若将 `/mirror` 独立子域部署，可单独构建镜像项目以控制索引体积与抓取预算。 |

## 4. 构建与 CI

- `npm run docs:build`：先 `sync:configs-table`，再 `vitepress build`。
- `npm run verify:inquanto`：manifest 与文件系统一致后再扩大镜像树。

更多部署选项见仓库 `docs-site/README.md` 的 Mirror size 表。
