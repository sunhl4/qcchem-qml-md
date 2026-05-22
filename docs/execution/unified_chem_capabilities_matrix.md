# Unified Chemistry Capability Matrix

Pipeline branches gate on `SolverCapabilities` flags (not hard-coded `scf.driver` strings).

## Embedding / Hamiltonian gates

| Pipeline branch | Required capability flags |
|---|---|
| Global active-space qubit Hamiltonian | `supports_restricted_active_space_qubit_hamiltonian` |
| AVAS (`active_space.strategy=avas`) | `supports_avas_active_space_projection` |
| AO / Lowdin embedding input | `supports_embedding_input_ao_lowdin` |
| Projection fragment Mulliken | `supports_projection_fragment_mulliken_hamiltonian` |
| Schmidt atomic impurity | `supports_schmidt_atomic_hamiltonian` |
| CASSCF orbital audit / feed | `supports_casscf_orbital_audit` |
| RDM extraction | `supports_rdm_correction_hooks` |
| NEVPT2 CASCI correction | `supports_rdm_nevpt2_casci` |
| PBC k-mesh (`max(pbc_kpoint_mesh)>1`) | `supports_pbc_k_mesh` |

## Solver implementation snapshot

| backend_id | molecular_scf | pbc_k_mesh | restricted_active_space_qh | avas | projection_fragment_mulliken | schmidt_atomic | embedding_input_ao_lowdin | casscf_audit | rdm_hooks | rdm_nevpt2 | get_integrals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pyscf | true | true | true | true | true | true | true | true | true | true | true |
| psi4 | true | false | true | true | true | true | true | true | true | true | true |
| precomputed | true | false | false | false | false | false | false | false | false | false | false |

Precomputed uses ``PreQuantumPath.PRECOMPUTED_BUNDLE`` (``bundle.pre_quantum_input.qubit_hamiltonian``); live integral / embedding hooks are intentionally false.

Psi4 AVAS uses shared PySCF `mcscf.avas` projection on exported MO coefficients (`capability_notes` on `SolverCapabilities`). Psi4 PBC is Gamma-only (`supports_pbc_k_mesh=false`; use PySCF for `max(pbc_kpoint_mesh)>1`). Psi4 `ddcosmo` maps to PCM in Psi4 options.
