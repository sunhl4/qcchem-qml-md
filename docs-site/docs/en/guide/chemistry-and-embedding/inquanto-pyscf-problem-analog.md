# InQuanto-PySCF analog: quantum-problem tuple & AO view

This page maps the common Quantinuum tutorial narrative—**PySCF driver → Hamiltonian / Fock space / HF reference → variational quantum algorithms**—to `qchem_stack`. Names differ from InQuanto-PySCF, but the engineering coverage below is explicit.

## 1. MO active space → OpenFermion (`get_system`-style)

InQuanto returns an integral operator, `FockSpace`, HF reference, …

`qchem_stack`:

- :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_restricted_active_space_quantum_problem`
- :class:`~qchem_stack.chem.molecular_problem.RestrictedActiveSpaceQuantumProblem` carries:
  - **`compact_mo_operator`** — :class:`~qchem_stack.chem.restricted_integral_operator.RestrictedActiveSpaceIntegralOperatorCompact`: retains PySCF CASCI ``get_h2eff`` storage (compact **or** dense), expands via ``dense_h2_chemist_spatial()`` / ``to_interaction_operator()`` on demand, and exposes **`df_mo_integrals()` / `df()`** (pandas) for notebook-style tables (tutorial ``df()`` parity).
  - **`interaction_operator`** — :class:`openfermion.InteractionOperator`
  - **`fermion_space`** — :class:`~qchem_stack.chem.fermion.FermionSpace`
  - **`hartree_fock_state_jw`** — OpenFermion **Jordan–Wigner** HF amplitudes
  - **`qubit_hamiltonian`** — :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`

CASCI raw hook: :func:`~qchem_stack.chem.drivers.pyscf_driver.active_space_casci_raw_blocks`; OpenFermion ordering follows the Tangelo-aligned reorder in :mod:`qchem_stack.chem.integral_convention`.

## 2. Symmetry + compact MO ERIs (`get_system(symmetry=…)` narrative)

InQuanto ships compact symmetry-backed integral containers.

`qchem_stack`:

- **Symmetry**: `chemistry_extended.pyscf_symmetry` → ``pyscf.gto.M(..., symmetry=...)`` for classical acceleration.
- **Compact holder**: `RestrictedActiveSpaceIntegralOperatorCompact` stores the raw ``get_h2eff`` buffer (see ``eri_raw_ndim`` / ``eri_raw_n_elements`` in ``symmetry_meta``) and only runs ``ao2mo.restore`` when expanding to `(na, na, na, na)`.
- **Quantum mapping (Jordan–Wigner)** Two optional layers: (1) default ``InteractionOperator`` + OpenFermion’s specialized JW; set ``active_space.jordan_wigner_coeff_atol`` (positive) to drop negligible Pauli shells on that path. (2) Avoid allocating a dense `(2×ncas)⁴` spin ERI tensor *for the JW step*: ``active_space.prefer_restricted_spatial_fermion_for_jordan_wigner: true`` with ``fermion_qubit_mapping: jordan_wigner`` builds a spatial-MO ``FermionOperator`` then JW. **Canonical entry point**: ``molecular_hamiltonian_from_classical_reference`` (unified interface). ``PySCFDriver.get_restricted_active_space_quantum_problem`` remains available. ``interaction_operator`` is still materialized for API parity / notebook exports. With :meth:`~qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.from_config`, omitting the corresponding kwargs on ``get_restricted_active_space_quantum_problem`` inherits those YAML fields from ``cfg.active_space``.
- **Scope**: compact storage stays about **deferred ``ao2mo.restore``** and **tabular introspection**; very large systems still want DF / tensor-network backends beyond these JW optimizations.

### 2.1 AVAS / CASSCF hooks (PySCF pipeline stage)

- **`active_space.strategy=avas`** requires **`scf.driver=pyscf`** and non-empty **`chemistry_extended.avas_ao_labels`**; wraps PySCF **`mcscf.avas.AVAS`**, writes **`qchem_active_space_resolution_v1`**, and refreshes YAML active-space sizing in-process. Example **`configs/example_h2_avas.yaml`**.
- **`chemistry_extended.casscf_orbital_optimization_for_integrals`** shares a single **`mcscf.CASSCF`** call with **`casscf_orbital_optimization_audit`**; when enabled, optimized MO coefficients feed the CASCI-style active extract.
- **Not** claiming InQuanto proprietary **driver-default** AVAS/CASSCF packaging—see [public matrix §3](/parity/public-matrix) / [§10 boundary](/parity/gap-implementation-plan#p2-w3-avas-casscf-boundary).

### 2.2 Geometry, RI/DF, frozen orbitals, MO hook, one-electron API (PySCF-first)

> Note: PySCF is the default adapter example in this repository, not a hardwired exclusive backend; the canonical entry stays `create_solver` + `SolverCapabilities`.

- **`molecule.ecp`**, **`molecule.zmatrix`**: mutually exclusive with Cartesian **`coordinates`**; built through PySCF **`gto.M`**.
- **`scf.density_fit`** / **`scf.density_fit_auxbasis`**: recorded in **`driver_meta`** (`scf_density_fit*`).
- **Frozen orbitals**: non-empty **`active_space.frozen_orbitals`** → **`driver_meta.active_space_frozen_orbitals`** → CASCI **`frozen`** (must satisfy PySCF constraints).
- **Post-SCF MO hook**: **`chemistry_extended.mo_coeff_transform_hook`** (`identity`, `reverse_mo_columns`, or ``module:function``); audit **`mo_coeff_transform_hook_v1`**.
- **One-electron operators**: `PySCFDriver.compute_one_electron_operator_fermion` / `compute_one_electron_operator_pauli` (`kin|nuc|hcore|ovlp|r|rr|dm`). **Not** a drop-in replacement for proprietary `compute_one_electron_operator`.
- **Restricted quantum-problem path**: still assumes a **closed-shell RHF** mean field; non-RHF choices fail fast.
- **Psi4**: registered; **`compute_mean_field`** can return **RHF total energy** when Psi4 is installed (energy-only MF); **`supports_restricted_active_space_qubit_hamiltonian=False`**.

## 3. AO + PySCF `mf` (`get_system_ao`)

InQuanto wraps the PySCF SCF object for AO-centric workflows.

`qchem_stack`:

- :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_system_ao` → :class:`~qchem_stack.chem.drivers.pyscf_driver.PySCFAOSystem`
- **Summary table**: :meth:`~qchem_stack.chem.drivers.pyscf_driver.PySCFAOSystem.ao_driver_summary_df` (`nao_nr`, electrons, `groupname`, …).

## 4. Geometry units (Å vs Bohr)

Use **`coordinates` + `coordinate_unit`** (default **angstrom**), or legacy **`coordinates_bohr`** (Bohr when `coordinate_unit` is omitted). See `MoleculeSpec`.

## 5. Runnable example

```bash
python examples/example_inquanto_style_quantum_problem.py
```

Source file: `examples/example_inquanto_style_quantum_problem.py`.

## See also

- Active space / frozen / AVAS / CAS (**Chinese deep-dive**): [`docs/活性空间指定与AVAS_理论实践与开源对照.md`](../../../../docs/活性空间指定与AVAS_理论实践与开源对照.md)
- [Second quantization cheat sheet (Fock + fermionic Hamiltonian)](./second-quantization-fock-hamiltonian-readout.md)
- [P1 Chemistry & embedding](./index.md)
- [Public parity matrix §3](/en/parity/public-matrix)
