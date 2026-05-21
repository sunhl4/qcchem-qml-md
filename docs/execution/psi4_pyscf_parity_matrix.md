# Psi4 vs PySCF parity matrix (E2 reference)

Optional **E2** checks — not required for new driver admission. Thresholds are **soft**
(documented in test modules); record `psi4.__version__` / `pyscf.__version__` in `driver_meta` when debugging.

## H₂ sto-3g canonical active-space pack

| Test | Atol / metric | `implementation_id` (Psi4 CASCI path) |
|------|----------------|----------------------------------------|
| `tests/test_psi4_pyscf_h2_canonical_parity.py` | `constant` 5e-3; `h1` max abs 5e-2; `h2` max abs 8e-2 | `psi4_casci_hamiltonian_v1` or `psi4_mints_casci_effective_v1` (see `driver_meta.kernel_bindings`) |
| `tests/test_psi4_pyscf_alignment.py` | SCF energy, MO overlap, embedding smoke | `psi4_energy_scf_v1` vs `pyscf_native_v1` |

Run: `pytest -m psi4 tests/test_psi4_pyscf_h2_canonical_parity.py tests/test_psi4_pyscf_alignment.py`

## Audit-only cross-check

| Option | Behavior |
|--------|----------|
| `chemistry_extended.integral_crosscheck: pyscf_casci` | Writes `driver_meta.integral_crosscheck_casci_v1` (max abs h1/h2/constant); does **not** replace qubit H |

Default: `none` (no CI cost).
