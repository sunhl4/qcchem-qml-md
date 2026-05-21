# Integrations layer index

The `qchem_stack.integrations` package holds **extension and parity-reference** code that sits
above orchestration. It is **not** imported by `chem`, `quantum`, or `protocols` (orchestration
may import integrations for optional sidecars and previews).

Use this index to tell **product paths** (stable imports, HTTP/meta surfaces, CI smoke) from
**research / analog stubs** (benchmarks, vendor-shaped reports, toy loops).

## Product paths (stable for integrators)

| Module | Role | Typical entry |
|--------|------|----------------|
| `workflow_preview.py` | YAML-only workflow checklist + `computable_graph_v2` | `workflow_preview_payload`, HTTP `POST /v1/meta/workflow-preview` |
| `workflow_preview_graph.py` | Graph builder helpers for preview | Used by `workflow_preview` |
| `methods_resource_unified.py` | Methods-style resource export bundle | Pipeline / export scripts |
| `resource_estimation_preview.py` | Shot/circuit preview without chemistry | Meta APIs, export scripts |
| `cross_solver_parity.py` | HF energy cross-check reports | Tests, parity scripts |
| `open_driver_surface.py` | Registered classical driver catalog | Capability / parity exports |
| `rdm_corrections.py` | RDM correction hooks wired from orchestration | SCF stage when YAML enables |
| `rdm_corrections_types.py` | Typed shapes for RDM sidecars | `rdm_corrections` |

These modules are covered by contract tests (`tests/test_workflow_preview_contract.py`,
`tests/test_methods_resource_unified_export.py`, etc.) and documented in
[`CONTRIBUTING.md`](../../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports).

## Research / analog / toy paths

| Module | Role | Epistemic note |
|--------|------|----------------|
| `dmet_self_consistent.py` | DMET self-consistency loop + one-shot driver | Open architecture; not full literature DMET |
| `schmidt_dmet_self_consistent.py` | Schmidt ↔ DMET density feedback | Production-shaped; see embedding YAML |
| `dmet_multifragment_toy.py` | Uniform multifragment toy sweep | **Toy** — smoke only |
| `gap_closure_bundle.py` | Gap-closure reference bundle | Parity / Methods narrative |
| `l3_algorithm_benchmark.py` | Deep numerical benchmark gate | Optional `pytest -m l3` |
| `l3_statistics_reference.py` | Bootstrap stats stub for L3 | Research reference |
| `qermit_reference.py` | Qermit-style capability matrix | **Analog** — not commercial Qermit runtime |
| `tensornet_closure.py` | Tensor-network closure strategy doc blob | Stub / research |
| `tket_fullchain.py` | TKET compile stats bridge | Optional `pip install .[pytket]` |
| `nexus_optional.py` | qnexus installation probe | Optional `pip install .[nexus]` |
| `ucc_reference.py` | UCCSD pool / regrouping reference | Algorithm parity, not runtime default |

## Package `__init__` exports

`integrations/__init__.py` re-exports a **small stable subset** (DMET loop, TKET bridge,
Qermit matrix, UCC reference, nexus probe). Everything else is imported by explicit submodule path.

## Dependency rule

```
integrations  →  orchestration, protocols, chem, quantum, jobs  (may)
orchestration →  integrations  (optional sidecars only)
chem/quantum  →  integrations  (must NOT)
```

When adding a new file here, classify it in this README and add a focused test under `tests/`.
