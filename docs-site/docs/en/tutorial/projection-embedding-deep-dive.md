---
title: Projection embedding — trace keys and Mulliken Hamiltonians
description: What changes when embedding.mode=projection and projection_quantum_hamiltonian varies
---

Optional **deep dive** for the projection embedding path: which Hamiltonian is used variationally and where the audit keys land.

## Two `projection_quantum_hamiltonian` modes

| Value | Variational `QubitHamiltonian` | Example YAML |
|-------|-------------------------------|--------------|
| `global_active_space` (default) | Same global active space + fermion→qubit mapping; embedding adds **trace metadata** | `configs/example_h2_projection_trace.yaml` |
| `fragment_mulliken_mo` | Active orbitals from **fragment Mulliken weights** on RHF MOs, then CASCI active integrals + mapping (**not** full many-body projection product parity) | `configs/example_h4_projection_mulliken.yaml` |

Read any **`epistemic_bound`** text in snapshots for open-stack honesty vs closed-source defaults.

## Repro keys to diff

- **`repro.embedding_config`**
- **`repro.parity_snapshot`** projection trace keys (names vary slightly by path)
- Top-level **`embedding_workflow`** after a pipeline run

Reference table: [DMET / parity_snapshot](/en/reference/dmet-parity-snapshot) (authoritative long-form remains under repo `docs/`).

## Smoke

```bash
python scripts/smoke_pipeline.py --projection-trace
```

## See also

- [Workflow & YAML](/en/tutorial/workflow-overview)
- [Parity matrix](/parity/public-matrix) §3
