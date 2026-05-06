---
title: Positioning & roadmap
description: Boundaries, roadmap, and internal engineering benchmark index (for planning; users start at Product features + Tutorial)
---

**Use the product** via: [Product features](/en/product/features) → [Tutorial](/en/tutorial/quickstart) → [Guides](/en/guide/) → [CLI & scripts](/en/reference/cli-and-scripts).

This page is for **scope, roadmap, and internal targets**: mapping to published InQuanto docs supports **engineering goals and acceptance**, not the primary user path.

## Product scope (summary)

Open orchestration: YAML, pluggable backends, strict repro. No claims of closed-wheel parity, real Nexus/HQC, or vendor hardware equivalence. Details: [competitive positioning](/en/concept/competitive-positioning), [engineering architecture](/en/concept/engineering-architecture).

## Roadmap

See **[Roadmap](/en/product/roadmap)**.

## Internal engineering: benchmark vs published InQuanto

Readable against the [public InQuanto hub](https://docs.quantinuum.com/inquanto/) **three pillars**; we add **P4 (jobs & reproducibility)**.

| InQuanto pillar | Engineering entries |
|-------------------|----------------------|
| Chemical Specification | [P1](/en/guide/chemistry-and-embedding/) · [DMET](/en/reference/dmet-parity-snapshot) · [Mirror Manual](/en/mirror/manual/) |
| Program Construction | [P2](/en/guide/algorithms-and-protocols/) · [CircuitIR](/en/reference/circuitir-tket-jobs) · [Mirror API](/en/mirror/api/algorithms/) |
| Execution and Analysis | [P3](/en/guide/execution-and-analysis/) · [P4](/en/guide/jobs-and-reproducibility/) · [Cloud](/en/cloud/) |

**Contracts & ledgers**: [parity matrix](/en/parity/public-matrix) · [Y1 ledger (ZH)](/parity/y1-alignment-ledger) · [/mirror/](/en/mirror/) · [Security & data](/en/meta/security-and-data). Machine backlog: `docs/inquanto-node-backlog.generated.json` (`npm run report:inquanto-backlog`).
