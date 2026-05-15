---
title: Roadmap
description: P0–P2 engineering beats and milestones
---

# Roadmap

This page compresses the engineering narrative into **one navigable hub**. Authoritative detail stays in **[full plan (Chinese)](/concept/p2-detailed-plan)** and [English summary](/en/concept/p2-detailed-plan).

## Beat overview (conceptual)

Phase labels **P0 / P1 / P2** match that doc; they do **not** imply calendar quarters unless your programme pins them separately.

```mermaid
flowchart TB
  subgraph P0["P0 — Criteria & reproducibility closure"]
    a[parity_snapshot / repro]
    b[export_parity_criteria_table · CI]
  end
  subgraph Y1["Y1 Q3 (doc naming)"]
    l[L3 small-system numerical benchmarks]
  end
  subgraph P1["P1 — Embedding · excited states · mitigation reporting"]
    c[EmbeddingSpec / DMET hooks]
    d[Excited-state shot accounting consistency]
    e[PMSV report blocks]
  end
  subgraph P2["P2 — Long track & device sampling"]
    f[QPE / FT demos under same config tree]
    g[Qiskit histogram Pauli path]
  end
  P0 --> Y1
  P0 --> P1
  P1 --> P2
```

## Doc index (deep dives)

| Topic | Page |
|------|------|
| Roadmap P2 | [Full plan (ZH)](/concept/p2-detailed-plan) · [Summary (EN)](/en/concept/p2-detailed-plan) |
| Engineering architecture | [Architecture](/en/concept/engineering-architecture) |
| API and jobs | [HTTP API · SQLite jobs](/en/reference/http-api-sqlite-jobs) |

## Back to product & quickstart

- [Product features](/en/product/features) · [Positioning & roadmap](/en/product/) · [15-minute quickstart](/en/tutorial/quickstart) · [Guides overview](/en/guide/)
