---
title: Compare backends with one YAML family
description: Change only the backend block to contrast statevector vs Qiskit shots paths
---

## Idea

Keep `molecule`, `scf`, `active_space`, and `quantum` fixed; edit **`backend`** (and backend-specific keys such as Qiskit **shots**) to isolate how the **execution surface** changes result shape (exact energies vs sampling, resource summary fields).

## Suggested triplets

1. **`configs/example_h2.yaml`** — baseline **statevector** (or default non-sampled path).  
2. **`configs/example_h2_qiskit_shots.yaml`** — **Qiskit shots / bitstrings** on the same chemistry narrative (`quantum` extra).  
3. **`configs/example_h2_sampled.yaml`** — **sampled Pauli protocol** vs baseline when relevant.

## Tips

- When merging edits, diff **`backend`** (and sampling-related `quantum` keys) first; avoid accidental `molecule` edits.  
- After runs, compare **`repro.pipeline_profile`** and any **resource summary** fields.  
- Install paths: [CLI & scripts](/en/reference/cli-and-scripts), [Quickstart](/en/tutorial/quickstart).

Allowed values remain authoritative in [Reference](/en/reference/http-api-sqlite-jobs) and Pydantic models.
