# qchem-stack documentation site

[VitePress](https://vitepress.dev/) site for the **qchem-stack product**: **`/product/`** (value proposition), **`/product/roadmap`** (engineering beats + Parity doc index), pillar guides (`/guide/`), concepts, reference, parity — plus optional **`/mirror/`** public-doc benchmark map aligned with Quantinuum’s [published InQuanto doc tree](https://docs.quantinuum.com/inquanto/) for audits (**not** a clone of closed-source InQuanto).

**InQuanto 文档站架构报告（多卷 + 附录 A/B/C + 295 节点机读 backlog）**：母稿在仓库 [`../docs/architecture-report-quantinuum-inquanto-web/`](../docs/architecture-report-quantinuum-inquanto-web/INDEX.md)，用于指导本站信息架构与门禁，**不**作为 VitePress 内嵌长文。机读 backlog：**`../docs/inquanto-node-backlog.generated.json`**。再生：`npm run report:inquanto-appendix`；`npm run report:inquanto-backlog`；门禁：`npm run verify:inquanto`。

Bilingual: Chinese is primary at `/`, English is at `/en/`. Built-in local search. Mermaid diagrams render natively in any markdown via [`vitepress-plugin-mermaid`](https://emersonbottero.github.io/vitepress-plugin-mermaid/).

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
npm run docs:build        # output: docs/.vitepress/dist
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

- [`docs/meta/ia-mapping.md`](docs/meta/ia-mapping.md) — pillar slugs and source-file map.
- [`../IA_MAPPING.md`](../IA_MAPPING.md) — same content at the package root.
- [`docs/design/wireframe-home-guides.md`](docs/design/wireframe-home-guides.md) — block-level wireframe of the home and guides hubs.

## Syncing from repo `docs/`

Canonical narrative Markdown still lives in [`../docs/`](../docs/). When syncing copies into `docs/concept/`, `docs/parity/`, `docs/reference/`:

```bash
npm run fix-links
```

This rewrites `.md` cross-links to site routes; `/mirror` and `/en` trees are skipped (they are generator output).
