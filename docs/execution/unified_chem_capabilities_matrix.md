# Unified Chemistry Capability Matrix

This matrix documents which `SolverCapabilities` flags gate each orchestration path.
The pipeline must use capability checks instead of backend string branching whenever possible.

## Embedding / Hamiltonian gates

| Pipeline branch | Required capability flags | Current callsite |
|---|---|---|
| Global active-space qubit Hamiltonian (`embedding.mode=none` baseline path) | `supports_restricted_active_space_qubit_hamiltonian` | `src/qchem_stack/orchestration/pipeline.py` (`_hamiltonian_with_schmidt_context`) |
| AVAS active-space projection (`active_space.strategy=avas`) | `supports_avas_active_space_projection` | `src/qchem_stack/orchestration/pipeline.py` (`_refine_mean_field_for_active_space`) |
| AO / Lowdin embedding input payload | `supports_embedding_input_ao_lowdin` | `src/qchem_stack/orchestration/pipeline.py` (`_embedding_input_system_payload`) |
| Projection fragment Mulliken Hamiltonian (`projection_quantum_hamiltonian=fragment_mulliken_mo`) | `supports_projection_fragment_mulliken_hamiltonian` | `src/qchem_stack/orchestration/pipeline.py` (`_hamiltonian_with_schmidt_context`) |
| Schmidt atomic impurity Hamiltonian (`dmet_hamiltonian_source=schmidt_atomic_production`) | `supports_schmidt_atomic_hamiltonian` | `src/qchem_stack/orchestration/pipeline.py` (`_schmidt_hamiltonian_and_context`) |
| CASSCF orbital audit / feed hooks | `supports_casscf_orbital_audit` | `src/qchem_stack/orchestration/pipeline.py` (`_refine_mean_field_for_active_space`) |
| RDM extraction correction hooks | `supports_rdm_correction_hooks` | `src/qchem_stack/orchestration/pipeline.py` (`run_pipeline_sync`) |
| NEVPT2 CASCI correction | `supports_rdm_nevpt2_casci` | `src/qchem_stack/orchestration/pipeline.py` (`run_pipeline_sync`) |

## Solver implementation snapshot

| backend_id | molecular_scf | restricted_active_space_qh | avas | projection_fragment_mulliken | schmidt_atomic | embedding_input_ao_lowdin | casscf_audit | rdm_hooks | rdm_nevpt2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pyscf | true | true | true | true | true | true | true | true | true |
| psi4 | true | false | false | false | false | false | false | false | false |

## DMET / Schmidt precise branch notes

- `embedding.mode=dmet` + `dmet_hamiltonian_source=whole_active_system` still uses the global active-space Hamiltonian gate, therefore requires `supports_restricted_active_space_qubit_hamiltonian`.
- `embedding.mode=dmet` + `dmet_hamiltonian_source=schmidt_atomic_production` is explicitly a Schmidt path and requires `supports_schmidt_atomic_hamiltonian`.
- `embedding.mode=plugin` is backend-agnostic at the Hamiltonian construction layer and does not consume backend MO/AO hooks directly.
