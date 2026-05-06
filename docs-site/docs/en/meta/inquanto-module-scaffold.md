---
title: InQuanto module scaffold
description: Public-site top-level and Manual L1 branches ↔ mirror routes and qchem-stack docs — editable template, not vendor copy
---

# InQuanto public modules → site scaffold

This page is an **editable IA template**: it keeps Quantinuum **public** InQuanto **module names and URL patterns** (for comparison and future edits), points to this repo’s **generated mirror tree** (same shape as `docs-site/scripts/inquanto-tree.yaml`), and lists **qchem-stack implementation entrypoints** you can update as the product evolves.

- Public root: `https://docs.quantinuum.com/inquanto/` (external)  
- Machine source: `docs-site/scripts/inquanto-tree.yaml` (`site_meta.inquanto_version_seen`)  
- Regenerate mirror: `npm run scaffold:mirror`  

Mirror pages are mostly audit/placeholder prose; **product truth** remains [Product features](/en/product/features), [Guides](/en/guide/), and [Reference](/en/reference/cli-and-scripts).

---

## 1. Top-level modules (same tier as public nav)

| Public module | URL pattern | Mirror (ZH) | Mirror (EN) | Implementation docs (edit me) |
|---------------|-------------|-------------|---------------|----------------------------------|
| Introduction | `introduction/*.html` | [/mirror/introduction/](/mirror/introduction/) | [/en/mirror/introduction/](/en/mirror/introduction/) | [Quickstart](/en/tutorial/quickstart) · [Product features](/en/product/features) |
| Manual | `manual/**` | [/mirror/manual/](/mirror/manual/) | [/en/mirror/manual/](/en/mirror/manual/) | [Guides](/en/guide/) · [Principles & reading](/en/guide/principles-and-reading) |
| Tutorials | `tutorials/**` | [/mirror/tutorials/](/mirror/tutorials/) | [/en/mirror/tutorials/](/en/mirror/tutorials/) | [Tutorial hub](/en/tutorial/quickstart) |
| API reference | `api/inquanto/**` | [/mirror/api/](/mirror/api/) | [/en/mirror/api/](/en/mirror/api/) | [HTTP API](/en/reference/http-api-sqlite-jobs) · [CircuitIR / TKET](/en/reference/circuitir-tket-jobs) |
| Extensions | `extensions/**` | [/mirror/extensions/](/mirror/extensions/) | [/en/mirror/extensions/](/en/mirror/extensions/) | [Reference](/en/reference/cli-and-scripts) · `pyproject` extras in repo |
| Misc | `misc/**` | [/mirror/misc/](/mirror/misc/) | [/en/mirror/misc/](/en/mirror/misc/) | [Security & data](/en/meta/security-and-data) · [Site map](/en/meta/ia-mapping) |

---

## 2. Manual L1 branches (`manual.children` key order)

| Key | Public title (EN) | Mirror (ZH) | Suggested engineering links (edit me) |
|-----|-------------------|-------------|----------------------------------------|
| `howto` | How to use | [/mirror/manual/howto/](/mirror/manual/howto/) | [Quickstart](/en/tutorial/quickstart) · [Workflow & YAML](/en/tutorial/workflow-overview) |
| `geometry` | Geometry | [/mirror/manual/geometry/](/mirror/manual/geometry/) | [P1](/en/guide/chemistry-and-embedding/) |
| `express` | Express datasets | [/mirror/manual/express/](/mirror/manual/express/) | [Product features](/en/product/features) |
| `symmetry` | Symmetry | [/mirror/manual/symmetry/](/mirror/manual/symmetry/) | [P1](/en/guide/chemistry-and-embedding/) · [P2](/en/guide/algorithms-and-protocols/) |
| `spaces_operators` | Spaces / operators | [/mirror/manual/spaces_operators/](/mirror/manual/spaces_operators/) | [P2](/en/guide/algorithms-and-protocols/) · [CircuitIR](/en/reference/circuitir-tket-jobs) |
| `ansatze` | Ansatze | [/mirror/manual/ansatze/](/mirror/manual/ansatze/) | [P2](/en/guide/algorithms-and-protocols/) |
| `minimizers` | Minimizers | [/mirror/manual/minimizers/](/mirror/manual/minimizers/) | [P2](/en/guide/algorithms-and-protocols/) |
| `computables` | Computables | [/mirror/manual/computables/](/mirror/manual/computables/) | [P2](/en/guide/algorithms-and-protocols/) · [Concept](/en/concept/engineering-architecture) |
| `protocols` | Protocols (five-stage) | [/mirror/manual/protocols/](/mirror/manual/protocols/) | [P2](/en/guide/algorithms-and-protocols/) · [Mitigation mapping](/en/concept/mitigation-mapping) |
| `algorithms` | Algorithms | [/mirror/manual/algorithms/](/mirror/manual/algorithms/) | [P2](/en/guide/algorithms-and-protocols/) |
| `embedding` | Embedding & DMET | [/mirror/manual/embedding/](/mirror/manual/embedding/) | [P1](/en/guide/chemistry-and-embedding/) · [DMET · parity_snapshot](/en/reference/dmet-parity-snapshot) |
| `noise_mitigation` | Noise mitigation | [/mirror/manual/noise_mitigation/](/mirror/manual/noise_mitigation/) | [P3](/en/guide/execution-and-analysis/) · [Mitigation mapping](/en/concept/mitigation-mapping) |

---

## 3. Tutorial groups (manifest)

| Group | Mirror (ZH) | Suggested engineering links (edit me) |
|-------|-------------|----------------------------------------|
| `core` | Under [/mirror/tutorials/](/mirror/tutorials/) | [Quickstart](/en/tutorial/quickstart) |
| `backends` | backends subtree | [P3](/en/guide/execution-and-analysis/) · [Compare backends](/en/tutorial/switch-backend-compare) |
| `case_study_fe4n2` | case nodes | [H₂ family case](/en/tutorial/case-study-h2-family) (swap for Fe4N2 when you add pages) |
| `fragmentation` | fragmentation subtree | [P1](/en/guide/chemistry-and-embedding/) · DMET in Reference |

---

## 4. Maintenance rules

1. **Product changes**: edit the “Suggested engineering links” cells only; mirror URLs stay generator-owned.  
2. **Public tree changes**: edit `inquanto-tree.yaml`, run `npm run scaffold:mirror`, then **update this table** to match.  
3. **Optional codegen**: add `scripts/sync-inquanto-scaffold.mjs` later if you want the middle column auto-filled.

See also: [Site map](/en/meta/ia-mapping) · [Security & data](/en/meta/security-and-data).
