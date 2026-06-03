---
title: CASSCF audit workflow
description: Honest partial boundary for AVAS/CASSCF product UX vs open-stack hooks.
---

# CASSCF orbital audit (open-stack)

Vendor-platform-grade AVAS/CASSCF **product UX** remains `partial` in the parity matrix. This repo exposes **audit hooks** and optional single-pass CASSCF orbital optimization for integrals.

## Representative YAML

- `configs/example_h2_casscf_audit.yaml` — enables `casscf_orbital_optimization_audit` metadata
- `configs/example_h2_avas.yaml` — PySCF AVAS projection (requires capability gate)

## Run

```bash
pip install "qchem-stack[chem]"
qchem-run configs/example_h2_casscf_audit.yaml
```

Inspect `repro.run_summary` for `classical_active_space_caveat_v1` and driver meta from PySCF.

## Boundary

See [non-goals](/product/non-goals) — we do **not** claim closed-source default parity for full AVAS/CASSCF orchestration.
