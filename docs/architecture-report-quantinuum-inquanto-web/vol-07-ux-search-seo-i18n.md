# Vol.07 UX、搜索、SEO 与多语言

**读者**：前端工程师、站点可靠性、国际化负责人。  
**对标**：InQuanto 公开站（Sphinx 类静态站）与 **本仓库 VitePress** 实现对照。

---

## 1. 推断的 InQuanto 文档站 UX 特征

| 特征 | 依据 | 用户影响 |
|------|------|----------|
| 固定顶栏 + 侧栏 TOC | 常见 Sphinx RTD 主题 | 长文导航清晰 |
| 版本在 `<title>` | 抓取样本 `InQuanto 5.2.3` | 书签与搜索引擎结果可区分版本 |
| 数学公式 | Protocols 页含 LaTeX | 需要 MathJax / KaTeX |
| 代码高亮 | quickstart / protocols 代码块 | Pygments 或等价 |
| 深色模式 | 未在样本中证实 | **推断** 可能随 Quantinuum 全域主题 |

---

## 2. 搜索（已证实存在行为）

公开站提供 **站内搜索**（具体引擎未证实 — 常见为浏览器内嵌或第三方索引）。**大 API 页** 依赖搜索 + 浏览器查找。

---

## 3. SEO 与可分享性（推断）

- **稳定 URL**：`.html` 路径即关键词。
- **外链**：Publications / TKET / Nexus 提高 **域权威** 与 **交叉引流**。
- **风险**：单页过大可能影响 **Core Web Vitals**（LCP）— **推断**。

---

## 4. 本仓库 VitePress 对照（工程事实）

| 能力 | VitePress `docs-site` | 备注 |
|------|-------------------------|------|
| Local Search | `themeConfig.search.provider: local` | 已启用 |
| Math | `markdown-it-mathjax3` | 已启用 |
| Mermaid | `vitepress-plugin-mermaid` | 已启用 |
| i18n | `locales` root `zh-CN` + `en` | EN parity 部分页仍 stub |
| 自定义组件 | `MirrorTree`、`PillarCard`、`StatusBadge` 等 | 优于 Sphinx 纯静态 |
| cleanUrls | `true` | URL 无 `.html` 后缀 — 与 InQuanto **不同**，需注意相对链接迁移 |

---

## 5. 可访问性（a11y）清单（建议）

- 为 `MirrorTree` 过滤按钮与 `details/summary` 树提供 **键盘可达**（浏览器默认 + 自定义样式勿破坏 focus ring）。
- 状态徽章 **颜色 + 文字** 双编码（已部分满足）。
- 大表与树提供 **横向滚动容器**（`custom.css` 已部分处理）。

---

## 6. 本卷结论

InQuanto 文档 UX **成熟但偏传统静态站**；VitePress + Vue 组件可在 **交互式目录、仪表盘、双语** 上超越。待办：**补齐 EN 深度页** 与 **站点地图 `sitemap`**（若对外 SEO 有要求）。

**下一卷**：[`vol-08-target-qchem-docs-and-cloud.md`](./vol-08-target-qchem-docs-and-cloud.md)。
