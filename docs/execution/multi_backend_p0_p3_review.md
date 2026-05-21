# Multi-backend P0–P3 implementation review

**Date:** 2026-05-20  
**Scope:** Plan *Multi-backend P0-P3* (architecture observability, low integration cost, capabilities, delivery).

## Completed

### P0 — Observability
- `append_kernel_bindings` / binding factories in `chem/integration/driver_meta.py` (dedupe by `kernel_id`).
- Production `kernel_bindings`: PySCF/Psi4 SCF, AVAS, CASCI (post-pack), NEVPT2 merge in `stage_execution`.
- `run_integration_checklist` validates `upstream_classical_software_tag` + `mean_field_scf` when `--run-scf`.
- AVAS validator renamed to `validate_avas_strategy_requires_labels_and_capability` (deprecated alias kept).
- Philosophy / registry / active-space docs updated; C2 marked done.

### P1 — Integration cost
- `chem/integration/presets.py` (`capabilities_driver_scf_only`, `capabilities_with_delegated_cas_path`).
- `chem/kernels/dispatch.py` (mean-field binding helpers, `run_avas`, `run_nevpt2_casci`).
- Facade `ensure_mean_field_binding` after bridge headers.
- `docs/execution/external_driver_ao_basis_view.md`.
- Template solver uses SCF-only preset.

### P2 — Capabilities & science options
- `SolverCapabilities.supports_pbc_k_mesh` + load-time validation.
- `chemistry_extended.integral_crosscheck` + `chem/integration/crosscheck.py` (audit-only).
- `capability_notes` on capabilities (Psi4 delegation documented).
- Unified capability matrix updated.

### P3 — Delivery
- `scripts/integration_checklist.py`.
- `pre_quantum_input` / `repro` export `classical_kernel_bindings` and `classical_epistemic_bound`.
- `configs/example_custom_driver_template.yaml`.
- `docs/execution/psi4_pyscf_parity_matrix.md`.
- Learning roadmap link to philosophy + AO guide.

## Tests

- `pytest -m "not psi4"`: **618 passed** (after golden fixture update).
- New: `test_integration_philosophy`, `test_pbc_kmesh_validation`, `test_integral_crosscheck`.
- `pytest -m psi4`: run in Psi4 micromamba env when validating E2 parity.

## Known residuals / backlog

| Item | Notes |
|------|--------|
| Schmidt DMET density feedback | `run_schmidt_density_feedback_cycles` still requires PySCF MF internally; `test_schmidt_path_allows_psi4_when_capability_enabled` fails when Psi4 is installed (capability vs implementation gap). |
| Central L3 scheduler | `kernels/dispatch` is thin; full catalog dispatch remains future work. |
| ORCA / Gaussian spike | Not in scope. |
| `registered_solvers_detail` | Does not yet embed `capability_notes`; use `solver_capability_notes_for_config(cfg)` or live `create_solver(cfg).capabilities`. |

## Cache / meta

`RunBuildCache` checksum excludes `kernel_bindings` and `integral_crosscheck_casci_v1` so audit metadata does not invalidate integral pack cache.
