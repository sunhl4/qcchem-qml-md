# qchem-stack documentation site

[VitePress](https://vitepress.dev/) site for the **qchem-stack product**: **`/product/`** (value proposition), **`/product/roadmap`** (engineering beats + Parity doc index), pillar guides (`/guide/`), concepts, reference, parity — plus optional **`/mirror/`** public-doc benchmark map aligned with Quantinuum’s [published InQuanto doc tree](https://docs.quantinuum.com/inquanto/) for audits (**not** a clone of closed-source InQuanto).

**设计与对标关系（模板语义）**：本站与 InQuanto **公开文档站**可视为沿用**同一类文档产品模板**——顶栏模块（Introduction / Manual / Tutorials / API / Extensions / Misc）、首页三柱叙事、浅色文档阅读节奏等与公开站**对齐**；**差异**在于正文与功能边界（qchem-stack 自管栈、`repro`/SQLite、无 Nexus 绑定等）以及**实现载体**（本站为 VitePress + 自有主题/CSS，非对方源码或设计资产）。便于你对照改文案、删减模块而不改整体层级。

**仓库文档入口**：根目录 [`README.md`](../README.md)、[`CONTRIBUTING.md`](../CONTRIBUTING.md)；对标三母稿与附录在 [`../docs/`](../docs/)（与 [`与InQuanto能力差距与实施计划.md`](../docs/与InQuanto能力差距与实施计划.md) 等）。

**InQuanto 文档站架构报告（多卷 + 附录 A/B/C + 295 节点机读 backlog）**：母稿在仓库 [`../docs/architecture-report-quantinuum-inquanto-web/`](../docs/architecture-report-quantinuum-inquanto-web/INDEX.md)，用于指导本站信息架构与门禁，**不**作为 VitePress 内嵌长文。机读 backlog：**`../docs/inquanto-node-backlog.generated.json`**。再生：`npm run report:inquanto-appendix`；`npm run report:inquanto-backlog`；门禁：`npm run verify:inquanto`。

**公开站模块 ↔ 本站「复现骨架」母版**（便于按模块改工程文档链接，非转载对方正文）：[`docs/meta/inquanto-module-scaffold.md`](docs/meta/inquanto-module-scaffold.md)（英文：[`docs/en/meta/inquanto-module-scaffold.md`](docs/en/meta/inquanto-module-scaffold.md)）。Manifest 变更后除 `scaffold:mirror` 外，请同步更新该 Markdown 表中的「工程侧」列（或后续改为脚本生成）。

**IA 定稿与线框（四柱 + Diátaxis）**：[`docs/meta/ia-mapping.md`](docs/meta/ia-mapping.md) · [`docs/meta/wireframe-home-and-guides.md`](docs/meta/wireframe-home-and-guides.md) · [`docs/meta/ssg-search-strategy.md`](docs/meta/ssg-search-strategy.md) · [`docs/meta/diataxis-index.md`](docs/meta/diataxis-index.md)（英文在 `docs/en/meta/` 同名路径）。

Bilingual: Chinese is primary at `/`, English is at `/en/`. Built-in **local** search (index grows with mirror pages; for very large public trees consider [Algolia DocSearch](https://docsearch.algolia.com/) and set `themeConfig.search` + crawler config in `.vitepress/config.ts`). Mermaid diagrams render natively via [`vitepress-plugin-mermaid`](https://emersonbottero.github.io/vitepress-plugin-mermaid/) (`mermaid.theme` in `config.ts` is set for the current light doc pages).

### Mirror size & deployment options

| Strategy | When to use |
|----------|----------------|
| **Single site** (current) | One VitePress app ships `/`, `/en/`, and `/mirror/**`; simplest ops. |
| **Mirror on a subdomain** | Split a second VitePress project that only builds `mirror/` + `en/mirror/` to keep the product docs slim and isolate crawl budget. |
| **On-demand scaffold** | Point `scripts/scaffold-mirror.mjs` at a filtered manifest or subtree while iterating; expand to full tree before release. |

`npm run verify:inquanto` should stay green before you widen the manifest. Regenerate mirror pages after manifest edits: `npm run scaffold:mirror`.

### Appearance

The site defaults to **`appearance: "light"`** to match the public InQuanto documentation rhythm (light surfaces + purple links). To force dark only, set `appearance: "force-dark"` in `docs/.vitepress/config.ts` and retune `theme/custom.css` tokens.

### GitHub `socialLinks` / `editLink`

When you publish a **public** GitHub repo, add `themeConfig.socialLinks` and per-locale `editLink.pattern` in `config.ts` pointing at the real org/repo (remove the placeholder-era omission).

### Generated `configs/` index

`npm run docs:build` runs `sync:configs-table` first. After adding or renaming files under `../configs/*.yaml`, commit the updated `docs/product/configs-packaged-list.md` and `docs/en/product/configs-packaged-list.md`, or CI will fail on `npm run check:configs-table`.

### Custom components (auto-registered)

| Component | Where it's used |
|---|---|
| `<StatusBadge :status="..." />` | every mirror page header & status legend |
| `<PillarCard ... />` | home page pillar tiles |
| `<MirrorTree locale="zh" />` | `/mirror/` index — full tree with status dashboard, pillar × status matrix, search & filters |
| `<MirrorBranch :prefix='[...]' :grouped='true' />` | injected by scaffold into every section / sub-section landing page |
| `<PillarMirror pillar="P1" locale="zh" />` | each `/guide/<pillar>/` page — auto-listed mirror nodes for that pillar |
| `<Breadcrumbs />`, `<LangSwitch />` | injected via theme slots |

## Commands

```bash
cd docs-site
npm install
npm run docs:dev          # opens http://localhost:5173/ in the default browser
npm run sync:configs-table # refresh packaged YAML index pages (also run by docs:build)
npm run check:configs-table # fail if index != git HEAD (for CI)
npm run docs:build        # sync configs index, then build → docs/.vitepress/dist
npm run docs:preview      # preview production build

npm run scaffold:mirror   # regenerate /mirror/** + /en/mirror/** + sidebar JSON
npm run check:mirror      # validate manifest vs filesystem
npm run fix-links         # one-shot rewrite of legacy .md links (skips /mirror & /en)
```

VitePress **does not** embed a preview panel inside the IDE. View it in a **regular web browser** (or in Cursor / VS Code: Command Palette → "Simple Browser: Show" → paste the URL).

## How the mirror is generated

```
scripts/inquanto-tree.yaml   ← single source of truth
       │
       │  npm run scaffold:mirror
       ▼
docs/mirror/**, docs/en/mirror/**           (placeholder pages, idempotent)
docs/.vitepress/sidebar-mirror.json         (consumed by config.ts)
docs/.vitepress/mirror-data.json            (consumed by <MirrorTree>)
```

To register a newly-discovered InQuanto leaf or change its status, **edit `scripts/inquanto-tree.yaml` only** and rerun `npm run scaffold:mirror`. Existing pages are not overwritten when they contain `<!-- generated:keep -->`.

## IA reference

- [`docs/meta/ia-mapping.md`](docs/meta/ia-mapping.md) — pillar slugs and source-file map (single canonical copy).
- [`docs/design/wireframe-home-guides.md`](docs/design/wireframe-home-guides.md) — block-level wireframe of the home and guides hubs.

## Syncing from repo `docs/`

Canonical narrative Markdown still lives in [`../docs/`](../docs/). When syncing copies into `docs/concept/`, `docs/parity/`, `docs/reference/`:

```bash
npm run fix-links
```

This rewrites `.md` cross-links to site routes; `/mirror` and `/en` trees are skipped (they are generator output).
