# `qchem_stack.chem`

Classical chemistry → pre-quantum interchange (`ExperimentConfig` → `PreQuantumInput` / `QubitHamiltonian`).

**模块技术参考手册：** [docs/说明_chem模块技术参考手册.md](../../../docs/说明_chem模块技术参考手册.md)

**代码与架构风格标准（必读）：** [docs/chem_模块风格约定.md](../../../docs/chem_模块风格约定.md)

**多后端与能力位：** [docs/说明_经典化学后端驱动_registry与能力位.md](../../../docs/说明_经典化学后端驱动_registry与能力位.md)

**统一接口理念：** [docs/统一经典化学接口_ChemIntegralSolver与下游无关性.md](../../../docs/统一经典化学接口_ChemIntegralSolver与下游无关性.md)

## Layout

| Area | Modules | Notes |
|------|---------|-------|
| Solver registry | `solvers/` | `create_solver`, `ChemIntegralSolver`, `SolverCapabilities` |
| Bridge interchange | `bridges/` | `ClassicalMeanFieldReference`, `reference_factory`, `facade` |
| Pre-quantum assembly | `pre_quantum_build.py`, `pre_quantum_*` | `build_pre_quantum_input` |
| Restricted RAS problem | `molecular_problem.py`, `molecular_problem_build.py` | PySCF `get_system` analog |
| Hamiltonian | `hamiltonian*.py` | JW/BK/SCBK → `QubitHamiltonian` |
| Integrals | `integrals/` | PySCF/Psi4 active-space export, one-body, Löwdin |
| Active space hooks | `active_space/` | Backend plugin hooks (AVAS, MO transform) |
| Embedding | `embedding/` | Schmidt, DMET, projection |
| Systems (views) | `system.py`, `systems/` | `MolecularSystem` vs backend-specific AO/Löwdin views |
| Integration | `integration/` | `meta_schema` (kernel bindings), capability presets, checklist |
| Kernels (L3) | `kernels/` | Shared algorithm dispatch (NEVPT2, AVAS delegate) |
| Classical benchmarks | `classical_benchmarks/` | HF/MP2/CCSD/CASCI dispatch |
| Legacy driver types | `drivers/pyscf_driver_types.py` | **Deprecated** — `drivers/` exports only `PySCFRHFResult` (the eager RHF result type); `PySCFDriver` was removed in v0.6.0 → use `chem.solvers` |

`ChemIntegralSolver` and `SolverCapabilities` are imported from `qchem_stack.chem.solvers` (not top-level `chem.__all__`) to avoid eagerly loading the full solver stack during test collection.

## Build chain (canonical)

```text
ExperimentConfig
  → create_solver(cfg)                    # scf.driver registry
  → classical_mean_field_reference_from_config(cfg)
  → build_pre_quantum_input(cfg, reference)   # embedding branch dispatch
  → PreQuantumInput (QubitHamiltonian + fermion_space + meta)

Restricted active-space tuple (optional shortcut):
  → restricted_active_space_quantum_problem_from_config(cfg)
  → RestrictedActiveSpaceQuantumProblem
```

PySCF-only convenience (tests, legacy scripts):

```text
  → pyscf_rhf_result_from_config(cfg)
  → pyscf_ao_system_from_config(cfg) / pyscf_lowdin_system_from_rhf(rhf)
```

## Conventions (summary)

Full rules: [chem_模块风格约定.md](../../../docs/chem_模块风格约定.md).

- **Orchestration must not `import pyscf`** for routing; use `create_solver` + `SolverCapabilities`.
- **Downstream consumes** `ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack`, not raw MF objects.
- **Backend-specific hooks** live under `active_space/` and `integrals/`; register via hook/exporter registries.
- **New public names** belong in submodule `__all__` first, then re-export from `qchem_stack.chem` when stable.
- **`PySCFRHFResult`** (legacy RHF result type) remains in `drivers/` for migration; `PySCFDriver` was removed in v0.6.0 — use `create_solver` + `ChemIntegralSolver`. AO views import from `systems/`, not `drivers/`.

## Public import surface

```python
import qchem_stack.chem as chem

solver = chem.create_solver(cfg)
ref = chem.classical_mean_field_reference_from_config(cfg)
pre_q = chem.build_pre_quantum_input(cfg, ref)
prob = chem.restricted_active_space_quantum_problem_from_config(cfg)
checklist = chem.run_integration_checklist(solver)
caps = chem.capabilities_pyscf_production()
```

Heavy symbols are lazy-loaded from `chem/__init__.py` to avoid circular imports during test collection.
