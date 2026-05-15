---
title: UCCSD Trotter layers and export
description: H₂ with JW + quantum.uccsd_trotter_steps and parity export smoke
---

This tutorial covers one **packaged** path: first-order **Trotter-layer** closed-shell UCCSD (`UCCSDTrotterVQE`) versus dense cluster exponentials (`UCCSDVQE`), plus a **config-only** `export_parity_criteria_table` check.

## Prerequisites

- Full pipeline: PySCF installed.
- Export only: no PySCF required.

## Pipeline (PySCF)

From the repository root (adjust `PYTHONPATH=src` if needed):

```bash
python -c "from pathlib import Path; from qchem_stack.config import load_experiment_config; from qchem_stack.orchestration.pipeline import run_pipeline_sync; p=Path('configs/example_h2_uccsd_trotter.yaml'); cfg=load_experiment_config(p); out=run_pipeline_sync(cfg, cfg_path=p); print(out['vqe_meta'].get('uccsd_trotter_steps'), out['repro']['parity_snapshot'].get('uccsd_trotter_steps'))"
```

## Export

```bash
python scripts/export_parity_criteria_table.py configs/example_h2_uccsd_trotter.yaml
```

## Caveat

**Bravyi–Kitaev / SCBK**: this UCCSD Trotter ansatz is **JW-only**; use HEA for BK/SCBK-transformed Hamiltonians. See the [parity matrix](/product/roadmap) §2.

## See also

- [Workflow & YAML](/en/tutorial/workflow-overview)
- [Ten repro keys](/en/tutorial/read-repro-keys)
