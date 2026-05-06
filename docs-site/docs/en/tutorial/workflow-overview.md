---
title: Workflow & YAML overview
description: How an experiment is structured in YAML; how it maps to the four pillars
---

After you can run the [quickstart](/en/tutorial/quickstart), this page explains **how a task is shaped in YAML** so you can edit examples or author your own `experiment` file.

The one-page Mermaid overview lives under [Product features](/en/product/features) (“One-page diagram”).

## Logical pipeline order

Typical flow vs pillars:

1. **Molecule / classical chemistry** → [P1 Chemistry & embedding](/en/guide/chemistry-and-embedding/)  
2. **Quantum subproblem** (active space, mapping, algorithm names) → P1 / [P2 Algorithms & protocols](/en/guide/algorithms-and-protocols/)  
3. **Protocol stages** (variational, Pauli protocol, excited paths) → P2  
4. **Backend & sampling** → [P3 Execution & analysis](/en/guide/execution-and-analysis/)  
5. **Jobs, API, repro** (if async or HTTP) → [P4 Jobs & reproducibility](/en/guide/jobs-and-reproducibility/)  

Start from `configs/example_h2.yaml`, then open the pillar sections you care about.

## Blocks you usually touch first

| Block (conceptual) | Role |
|--------------------|------|
| Molecule / cell metadata | System, charge, etc. |
| Classical / driver | PySCF (or other) driver and SCF options |
| Quantum / active space | Active orbitals, electrons, mapping |
| Quantum / algorithm | VQE, ADAPT, excited-state switches and hyperparameters |
| Backend | `statevector`, `qiskit`, shots-related fields |
| Jobs / API (optional) | SQLite / HTTP demo-related fields |

Exact keys follow packaged `configs/*.yaml` and the Pydantic config models in source; each pillar guide expands by topic.

## Relation to “Product features”

- [Product features](/en/product/features): **layers** (what / how / deep dive).  
- This page: **order and structure** of YAML vs pillars.  
- Commands: [CLI & scripts](/en/reference/cli-and-scripts).  

## Next

- [Guides overview](/en/guide/) → P1–P4  
- [UCCSD Trotter + export](/en/tutorial/uccsd-trotter-export)  
- [ZNE × Qiskit repro](/en/tutorial/zne-qiskit-repro)  
- [Projection embedding deep dive](/en/tutorial/projection-embedding-deep-dive)  
- [Principles & reading](/en/guide/principles-and-reading)  
