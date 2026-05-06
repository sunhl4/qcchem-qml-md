---
title: Three onboarding paths
description: Quickstart vs parity/L1 contract vs MD/ML — pick one or combine
---

Hub for **P2-W7** (two-month plan). Details live in each linked tutorial and in repo YAML.

## Path A — Run one quantum chemistry pipeline first

1. [Quickstart](/en/tutorial/quickstart)  
2. [Workflow & YAML](/en/tutorial/workflow-overview)  
3. Go deeper: [UCCSD Trotter + export](/en/tutorial/uccsd-trotter-export) or [H₂ case study](/en/tutorial/case-study-h2-family)

## Path B — Parity / L1 before changing code

1. [Public parity matrix](/en/parity/public-matrix)  
2. [L1 signoff](/en/parity/l1-signoff)  
3. [Gap plan](/parity/gap-implementation-plan) (ZH) and [P2 plan](/en/concept/p2-detailed-plan) (EN summary; full §6–§8 in repo `docs/P2_详细实施计划.md`)  
4. Repo root **`CONTRIBUTING.md`** (CI markers, parity export)

## Path C — MD/ML and `QMEFDataset`

1. [Principles & reading](/en/guide/principles-and-reading) (execution/mitigation sections as needed)  
2. `src/qchem_stack/md_bridge/` and **`docs/md_bridge_repro_freeze_list.md`**  
3. `pytest -m l1_md_ml`

**Maintenance**: Two-month calendar in repo `docs/P2_详细实施计划.md` §8.
