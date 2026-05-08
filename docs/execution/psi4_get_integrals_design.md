# Psi4 `get_integrals` Design Draft (v1)

## Goal

Define a backend-neutral shape for future `Psi4IntegralSolver.get_integrals` so orchestration can consume a `ClassicalMeanFieldReference` without importing Psi4 objects.

## Proposed return schema

```text
{
  "schema": "classical_get_integrals_v1",
  "backend_id": "psi4",
  "basis": "...",
  "n_spatial_orbitals": <int>,
  "h1_spatial": <ndarray/list>,
  "h2_spatial_chemist": <ndarray/list>,
  "electron_count": <int>,
  "nuclear_repulsion_au": <float>,
  "meta": {
    "integral_convention": "chemist_spatial",
    "ordering": "p_i p_j | p_k p_l",
    "source": "psi4_mints_or_post_scf"
  }
}
```

## Ordering contract

- Two-electron block uses **chemist spatial** order `(p, q, r, s)`.
- Downstream conversion to OpenFermion continues to use existing `qchem_stack.chem.integral_convention` utilities.
- Any backend-native packed/triangular ERI must be expanded before returning.

## Capability gate

- `SolverCapabilities.supports_get_integrals=False` until this shape is implemented.
- `NotImplementedError` is valid and expected before implementation.
