# DMET module map

Canonical DMET/self-consistency logic vs integration demos.

## Canonical (production-shaped)

| Module | Role |
|--------|------|
| [`src/qchem_stack/chem/embedding/dmet_self_consistent.py`](../../src/qchem_stack/chem/embedding/dmet_self_consistent.py) | PySCF density-feedback bath updates (H₂/H₄ demos) |
| [`src/qchem_stack/chem/embedding/dmet.py`](../../src/qchem_stack/chem/embedding/dmet.py) | DMET context / fragment solver hooks |
| [`src/qchem_stack/chem/embedding/schmidt_dmet_self_consistent.py`](../../src/qchem_stack/chem/embedding/schmidt_dmet_self_consistent.py) | Schmidt + DMET orchestration glue |

## Demo / toy (integrations)

| Module | Role |
|--------|------|
| [`src/qchem_stack/integrations/dmet_multifragment_toy.py`](../../src/qchem_stack/integrations/dmet_multifragment_toy.py) | Multi-fragment toy sweep |
| [`src/qchem_stack/integrations/dmet_self_consistent.py`](../../src/qchem_stack/integrations/dmet_self_consistent.py) | Thin re-export / parity bundle helper |

**Rule:** `chem/` must not import `integrations/` at module scope (see `tests/chem/test_dmet_import_boundaries.py`).

## Related configs

- `configs/example_h4_dmet_self_consistent.yaml`
- `configs/example_h4_schmidt_multifragment.yaml`
