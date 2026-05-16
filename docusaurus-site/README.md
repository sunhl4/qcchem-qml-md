# qchem-stack Docusaurus Site

This site is the **primary** user-facing documentation surface for `qchem_qml_md` (guides, tutorials, parity, reference). Long-form engineering appendices and deep technical contracts often remain in repository-root **`docs/*.md`**; the parity **matrix** is kept in sync with [`docs/public_parity_matrix.md`](../docs/public_parity_matrix.md) (update both when the matrix changes).

## Installation

`npm install`

## Local Development

```bash
cd docusaurus-site
npm install   # first time only
npm start
```

默认开发服务器：**`http://localhost:3000/`**。parity / workflow-preview 稳定 import 说明页：**`/reference/parity-contract-import-paths`**。

## Build

`npm run build`

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Content Scope

- Product capabilities
- Guides (three-pillar architecture)
- Tutorials and workflow examples
- CLI/API references
- Cloud/job orchestration notes
- Product roadmap and acceptance pages
