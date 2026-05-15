# Second quantization cheat sheet: Fock occupations & fermionic Hamiltonian

Tutorial and debug dumps often print a **reference determinant (occupations)** plus a **fermionic Hamiltonian as strings of ladders**. This note breaks those tables into small, navigable chunks and points to `qchem_stack` contracts (`RestrictedActiveSpaceQuantumProblem`, ``integral_convention``).

Sections mirror the Chinese guide:

1. **Spin-orbital labels** — spatial index × (α/β); `Fi^` creates, `Fi` annihilates on spin orbital `i` (ordering is convention-specific).
2. **Fock / occupation blocks** — 0/1 occupancies per spin orbital; closed-shell \(\mathrm{H}_2\)/STO-3G is the canonical 4-spin-orbital, 2-electron example.
3. **Hamiltonian table** — expansion of \(h_0 + \sum h_{pq} a^\dagger_p a_q + \tfrac12 \sum g_{pqrs} a^\dagger_p a^\dagger_q a_s a_r\); mind whether the \(\tfrac12\) is folded into printed coefficients.
4. **Terms** — constant (often nuclear repulsion + offsets); diagonal `Fp^ Fp` as number operators / one-body diagonal; generic four-index strings map to chemist ERIs **only after** verifying the toolkit’s indexing (OpenFermion / Tangelo-aligned reorder lives in ``qchem_stack.chem.integral_convention``).

**Workflow link:** :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_restricted_active_space_quantum_problem` yields ``interaction_operator``, ``fermion_space``, ``hartree_fock_state_jw``, ``qubit_hamiltonian``.

Zh version: [/guide/chemistry-and-embedding/second-quantization-fock-hamiltonian-readout](/guide/chemistry-and-embedding/second-quantization-fock-hamiltonian-readout).
