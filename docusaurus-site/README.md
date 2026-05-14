# qchem-stack Docusaurus Site

This site is the **primary** user-facing documentation surface for `qchem_qml_md` (guides, tutorials, parity, reference). Long-form engineering appendices and deep technical contracts often remain in repository-root **`docs/*.md`**; the parity **matrix** is kept in sync with [`docs/inquanto_public_parity_matrix.md`](../docs/inquanto_public_parity_matrix.md) (update both when the matrix changes). A VitePress tree under `docs-site/` is retained for legacy workflows and some npm automation.

## Installation

`npm install`

## Local Development

`npm start`

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

`npm run build`

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Content Scope

- Product capabilities
- Guides (three-pillar architecture)
- Tutorials and workflow examples
- CLI/API references
- Cloud/job orchestration notes
- InQuanto benchmark-oriented parity pages
