# Unified Adapter I/O Contract for Multiple Chemistry Backends

Goal: let users keep one `ExperimentConfig`/YAML surface while switching classical chemistry engines (PySCF, Psi4, more later), without changing downstream quantum workflow code.

## Unified Input (user-facing)

- Users provide standard `molecule`, `scf`, `active_space`, and `embedding` config blocks.
- Each backend adapter translates this canonical config to backend-native inputs.
- Adapters are registered through `qchem_stack.chem.solvers.registry` and implement `ChemIntegralSolver`.

## Unified Output (engineering-facing)

Current normalized output layers:

- `MolecularMeanFieldResult` for SCF results.
- `MeanFieldLike` for bridge-safe mean-field handles.
- `CanonicalActiveSpaceIntegralPack` for active-space integrals before Hamiltonian build.
- `QubitHamiltonian` as the common quantum Hamiltonian output.

Once data are wrapped as `MolecularMeanFieldResult` / `ClassicalMeanFieldReference`, downstream orchestration should stay backend-agnostic and branch only on `SolverCapabilities`.

## Minimal Adapter Contract (MVP)

A new backend should:

1. Implement the `ChemIntegralSolver` protocol (`set_physical_data`, `compute_mean_field`, etc.).
2. Declare `SolverCapabilities` correctly, especially `supports_restricted_active_space_qubit_hamiltonian`.
3. If active-space Hamiltonian path is not implemented yet, set capability to `False` explicitly.
4. If implemented, provide integrals compatible with `CanonicalActiveSpaceIntegralPack` semantics.

Optional hooks are also explicit capability flags:

- `supports_projection_fragment_mulliken_hamiltonian`
- `supports_schmidt_atomic_hamiltonian`
- `supports_embedding_input_ao_lowdin`
- `supports_casscf_orbital_audit`
- `supports_avas_active_space_projection` (PySCF example: `active_space.strategy=avas`)
- `supports_rdm_correction_hooks`
- `supports_rdm_nevpt2_casci`
- `supports_get_integrals`

## Current Status

- PySCF:
  - unified mean-field bridge, `CanonicalActiveSpaceIntegralPack`, and the default active-space Hamiltonian path.
  - **Geometry**: `molecule.ecp`, `molecule.zmatrix` (mutually exclusive with Cartesian `coordinates`; built via PySCF `gto.M`).
  - **RI/DF**: `scf.density_fit`, `scf.density_fit_auxbasis` (`driver_meta`: `scf_density_fit`, `scf_density_fit_auxbasis`).
  - **Frozen orbitals**: non-empty `active_space.frozen_orbitals` → `driver_meta.active_space_frozen_orbitals` → CASCI **`frozen`** (must satisfy PySCF constraints).
  - **Orbital hook**: `chemistry_extended.mo_coeff_transform_hook` (audit **`mo_coeff_transform_hook_v1`**).
  - **One-electron operators**: `PySCFDriver.compute_one_electron_operator_fermion` / `compute_one_electron_operator_pauli` (`kin|nuc|hcore|ovlp|r|rr|dm`).
  - restricted quantum-problem tuples still assume a **closed-shell RHF** mean field.
- Psi4:
  - registered with **`supports_molecular_scf=True`**; when Psi4 is installed, **`compute_mean_field`** can return **RHF total energy** (energy-only `MolecularMeanFieldResult`, **no** `CanonicalActiveSpaceIntegralPack` / default Hamiltonian pipeline).
  - `supports_restricted_active_space_qubit_hamiltonian=False`; missing Psi4 surfaces a clear **import** failure from `compute_mean_field`.
- Pipeline:
  - gates by capabilities (no hardcoded `scf.driver=="pyscf"`),
  - keeps `embedding.mode=plugin` usable independently.

## Suggested Onboarding Sequence for New Backends

1. Implement `compute_mean_field` and return normalized SCF output first.
2. Add active-space integral export compatible with canonical pack.
3. Flip capability from `False` to `True`.
4. Add backend conformance tests and pipeline smoke tests.

## Quickstart

- [Backend adapter quickstart (template + check)](/en/guide/chemistry-and-embedding/backend-adapter-quickstart)

## Migration snippet (post-cutover)

Compatibility wrappers are removed. Use backend-agnostic entry points directly.

```python
# recommended (backend-agnostic)
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference

ref = ClassicalMeanFieldReference(
    mf=rhf.mf,
    e_tot=float(rhf.e_tot),
    mo_energy=rhf.mo_energy,
    molecular_system=rhf.molecular_system,
    driver_meta=dict(rhf.driver_meta),
)
qh = molecular_hamiltonian_from_classical_reference(
    ref,
    n_active_orbitals=2,
    n_active_electrons=2,
)
```

## Suggested Regression Matrix

- `tests/test_backend_capability_conformance.py`: capability baseline and contract gates.
- `tests/test_pipeline_backend_gate.py`: canonical-pack / projection / schmidt gate behavior.

## Completion Board and Compatibility Sunset

### Current completion state

- Core interchanges are pinned: `MolecularMeanFieldResult`, `ClassicalMeanFieldReference`, `CanonicalActiveSpaceIntegralPack`.
- Pipeline routing is capability-gated (not backend-brand checks on `scf.driver`).
- Hamiltonian helpers expose unified `*_from_classical_reference` entry points; compatibility wrappers are removed.

### Exit criteria for this migration direction

Treat this migration as complete and move to the next priorities once:

1. At least one non-PySCF backend (including mock/stub) passes adapter-contract + pipeline-gate regressions;
2. Unified-entry examples in docs are at least as many as compatibility-path examples;
3. New feature PRs no longer add backend-brand checks in orchestration/algorithm paths (adapter boundary excluded).
