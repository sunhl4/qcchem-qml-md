---
title: ZNE × Qiskit Pauli and repro keys
description: What parity_snapshot.zne_qiskit_unification_v1 records (open stack, not commercial Qermit)
---

When **`mitigation.zne_enabled`** and the **Qiskit Pauli protocol** path are both on, the pipeline adds **`parity_snapshot.zne_qiskit_unification_v1`** with:

- YAML `mitigation_zne_mode`
- protocol summary fields (when present)
- a fixed **`epistemic_bound`** string describing open-stack limitations vs vendor MitRes/MitEx

Example YAML: **`configs/example_h2_zne_circuit_fold.yaml`**.

Narrative mapping: repo `docs/mitigation_PMSV_ZNE_Qermit_mapping.md` (mirrored as [mitigation mapping](/concept/mitigation-mapping) when available).

See also: [parity matrix](/parity/public-matrix), [Ten repro keys](/en/tutorial/read-repro-keys).
