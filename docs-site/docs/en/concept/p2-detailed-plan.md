---
title: P2 implementation plan
description: Research depth, large systems, pre-productization — WBS, milestones, gates, and explicit non-goals (roadmap P2)
---

# P2 implementation plan

The **authoritative full text** is maintained on the Chinese page: **[`/concept/p2-detailed-plan`](/concept/p2-detailed-plan)** (WBS tables, milestone cadence, and gate checklist).

## InQuanto-PySCF × Tangelo master implementation entry

A new repository master document has been added: `docs/实施总计划_InQuanto_PySCF_Tangelo.md`.
Use it as the single implementation entry for this topic, including:

- public-evidence breakdown of InQuanto `inquanto-pyscf` API capabilities
- Tangelo source-level patterns (`IntegralSolver` abstraction, solver selection, `SecondQuantizedMolecule`)
- gap matrix against current `qchem_stack` modules
- dual-track execution plan (12-week schedule + task-level implementation checklist)

Recommended reading order:

1. this page (P2 roadmap framing and boundaries)
2. `docs/实施总计划_InQuanto_PySCF_Tangelo.md` (detailed implementation)
3. [Gap implementation plan](/product/roadmap) (ledger and appendix anchors)

## Scope (roadmap P2 vs shipped “mainline structure” batch)

- **Roadmap P2** here means the competitive-doc phase **research depth & large-system work**, not the gap-doc §3 batch already shipped (QPE track on pipeline, `computable` thin layer, TKET CI)—that batch is labeled **“mainline structure enhancement (delivered)”** on [Gap implementation plan](/product/roadmap).

## P1 demo track vs P2 depth (QPE / export)

- **P1**: `qpe_demo_track`, `methods_resource_unified_v1`, optional TKET probe (`configs/example_h2_qpe_track_parity_integrations.yaml`).  
- **P2**: export top-level **`resource_estimation_preview_v1`** when `parity_integrations.resource_estimation_preview: true` (see repo `src/qchem_stack/integrations/resource_estimation_preview.py` and `qpe_qec_demo/README.md`). No cloud pricing or vendor L0 resource claims.

## Explicit non-goals

- Real Quantinuum Nexus / `qnexus` / HQC / OAuth / quotas / contractual SLA.
- Calibration, native gate-set superiority, or topology-level compilation promises for named hardware.
- Closed-wheel InQuanto, commercial Qermit, or `inquanto-cutensornet` binary **numerical or API** L0 parity.
- Marketing claims on accuracy or resources without public evidence or machine-readable keys.

## WBS IDs (summary)

| ID | Work package |
|----|----------------|
| **P2-W1** | QPE/FT × resources × compiler narrative（minimal closure: `configs/example_h2_qpe_track_parity_integrations.yaml` + `test_methods_resource_unified_qpe_plus_tket_probe_schema`, needs PySCF + pytket） |
| **P2-W2** | Decomposition: DMET / ONIOM / QM-MM |
| **P2-W3** | Classical: CASSCF / AVAS paths |
| **P2-W4** | Advanced mitigation blocks |
| **P2-W5** | Mapping / ansatz registry depth |
| **P2-W6** | MD/ML productization |
| **P2-W7** | Tutorials & examples |

**Exit gates** (each milestone): full `pytest`, `scripts/check_parity_export_sample.py`, parity matrix ↔ `inquanto_gap_categories`, cross-links between repo `docs/` and `docs-site`, and public-doc pinning per L1 signoff / ledger.

**Post-P1 execution order** (W1→W7 + B→J item 21): see canonical `docs/与InQuanto能力差距与实施计划.md`（附录 A） **§6** (not duplicated here).

For maintenance roles see repo `CONTRIBUTING.md`（维护角色）. Canonical markdown mirror: `qchem_qml_md/docs/与InQuanto能力差距与实施计划.md（附录 A）`.
Execution evidence pages are archived in repo `docs/execution/` (including Day12 and milestone closeouts at Day25/45/65/80/90).

<a id="adr-p2-w2-decomposition-scope"></a>
<a id="p2-w3-avas-casscf-boundary"></a>
<a id="p2-w5-algorithm-registry-alignment"></a>

## Appendix §9–§11 (ADR · W3 · W5)

The **full** ADR (P2-W2 decomposition scope), P2-W3 (AVAS / CASSCF boundary tables), and P2-W5 (registry tables) live only in the repo markdown **`docs/与InQuanto能力差距与实施计划.md`（附录 A）** sections **§9–§11**, co-maintained with the [public parity matrix](/product/roadmap). This English page keeps the **same anchor ids** for `fix-internal-links` compatibility; read the Chinese `/concept/p2-detailed-plan` §8 for the same pointer.
