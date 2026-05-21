# External driver: `AOBasisView` checklist

New `scf.driver` adapters must expose atomic-orbital quantities through
`src/qchem_stack/chem/bridges/ao_basis_view.py` so L3 kernels (AVAS shadow MO,
integral cross-checks) can run without vendor-specific code in orchestration.

## Required methods

| Method | Purpose |
|--------|---------|
| `nao()` | Number of atomic orbitals |
| `aoslice_by_atom()` | Per-atom AO slices (for Mulliken / embedding) |
| `overlap_ao()` | AO overlap matrix |
| `hcore_ao()` | Core Hamiltonian in AO basis |
| `fock_ao()` | Fock matrix in AO basis (for MO energies after transforms) |
| `mo_coeff_ao()` | MO coefficients `(nao, nmo)` in AO basis |

Optional but useful: `nmo()`, `function_to_center()` (Psi4 Mulliken paths).

## Reference implementations

| Backend | Module |
|---------|--------|
| PySCF | `PySCFAOBasisView` in `ao_basis_view.py` |
| Psi4 | `Psi4AOBasisView` + `psi4_reference_api.py` (`psi4_nao`, `psi4_hcore_ao`, `psi4_set_ca`, …) |

Factory: `ao_basis_view_from_reference(reference)` picks the view from `reference.backend_tag()`.

## Integration steps

1. After SCF, wrap your wavefunction in a `AOBasisView` subclass.
2. Build `ClassicalMeanFieldReference` with `merge_integration_driver_meta` / `kernel_bindings`.
3. Run `python scripts/integration_checklist.py --driver <id> --config <yaml> --run-scf`.

See also [multi_backend_integration_philosophy.md](multi_backend_integration_philosophy.md) §5 path A.
