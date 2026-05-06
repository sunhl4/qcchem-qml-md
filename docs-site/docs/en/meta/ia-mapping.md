---
title: IA slug map
description: Four-pillar naming, URL slugs, and canonical mapping to repo Markdown
---

# Information architecture — pillars & slugs

**Finalized**: pillar slugs are ASCII and identical in both locales; Chinese nav labels live in `config.ts`. Extended mapping (Chinese): [`/meta/ia-mapping`](/meta/ia-mapping). Wireframes: [Home & guides wireframe](/en/meta/wireframe-home-and-guides). Stack: [SSG & search strategy](/en/meta/ssg-search-strategy). Diátaxis index: [Documentation types](/en/meta/diataxis-index).

## Four pillars

| ID | English label | URL slug | Site path |
|----|---------------|----------|-----------|
| P1 | Chemistry & embedding | `chemistry-and-embedding` | `/en/guide/chemistry-and-embedding/` |
| P2 | Algorithms & protocols | `algorithms-and-protocols` | `/en/guide/algorithms-and-protocols/` |
| P3 | Execution & analysis | `execution-and-analysis` | `/en/guide/execution-and-analysis/` |
| P4 | Jobs & reproducibility | `jobs-and-reproducibility` | `/en/guide/jobs-and-reproducibility/` |

**InQuanto hub mapping**: P1–P3 align with the public three-column hub; **P4** aggregates jobs, `repro`, and parity narratives that are scattered across Nexus + manuals on the vendor site.

## Diátaxis prefixes

| Type | Prefix |
|------|--------|
| Concept | `/en/concept/` |
| Tutorial | `/en/tutorial/` |
| Reference | `/en/reference/` |
| Parity | `/en/parity/` (partial EN; some rows link to authoritative ZH parity docs) |

## Machine-readable mirror

See `docs-site/scripts/inquanto-tree.yaml` and the [Mirror index](/en/mirror/). Module scaffold: [InQuanto module scaffold](/en/meta/inquanto-module-scaffold). Security: [Security & data](/en/meta/security-and-data).
