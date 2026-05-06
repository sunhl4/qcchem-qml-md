---
title: Roadmap
description: P0–P2 engineering beats, Y1 Q3 L3 benchmarks, and parity doc index
---

# Roadmap

This page compresses the engineering narrative into **one navigable hub**. Authoritative detail stays in [Competitive positioning](/concept/competitive-positioning) (§5 — Chinese-primary); contract matrices and sign-offs live under Parity. **Roadmap P2 WBS**: **[full plan (Chinese)](/concept/p2-detailed-plan)** · [English summary](/en/concept/p2-detailed-plan) · canonical repo file `qchem_qml_md/docs/P2_详细实施计划.md`.

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

## Y1 Q3: L3 benchmark suite

Goal: **repeatable numerical thresholds** for public alignment without claiming equivalence to closed-source defaults (excluding cloud/hardware). Order: benchmark 1 (H₂ sto-3g + VQE+Pauli) → benchmark 2 (sampled / shots) → optional benchmark 3 (Schmidt single round).

See **[L3 benchmark roadmap](/parity/l3-benchmark-roadmap)** (Chinese-primary).

## Doc index (deep dives)

| Topic | Page |
|------|------|
| Gap list & implementation order | [Gap implementation plan](/parity/gap-implementation-plan) (Chinese-primary) |
| Roadmap P2 | [Full plan (ZH)](/concept/p2-detailed-plan) · [Summary (EN)](/en/concept/p2-detailed-plan); canonical `qchem_qml_md/docs/P2_详细实施计划.md` |
| Contract matrix | [Public parity matrix](/en/parity/public-matrix) · [full matrix (ZH)](/parity/public-matrix) |
| L1 / Y1 pinning | [L1 sign-off](/en/parity/l1-signoff) · [Y1 alignment ledger](/parity/y1-alignment-ledger) |
| Open-stack memory | [Open-stack memory](/parity/open-stack-memory) |
| Backlog vs schedule | [Backlog to schedule](/parity/backlog-to-schedule) |

## Back to product & quickstart

- [Product features](/en/product/features) · [Positioning & roadmap](/en/product/) · [15-minute quickstart](/en/tutorial/quickstart) · [Guides overview](/en/guide/)
