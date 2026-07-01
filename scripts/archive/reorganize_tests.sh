#!/usr/bin/env bash
# One-time move of flat tests/test_*.py into layer subdirectories.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/tests"

mkdir -p api chem quantum repro protocols integrations

move_glob() {
  local dest="$1"
  shift
  for pat in "$@"; do
    for f in $pat; do
      [[ -e "$f" ]] || continue
      git mv "$f" "$dest/" 2>/dev/null || mv "$f" "$dest/"
    done
  done
}

move_glob api test_api_*.py
move_glob md_bridge test_md_bridge*.py
move_glob chem test_pyscf*.py test_psi4*.py test_solver*.py test_dmet*.py test_embedding*.py test_canonical*.py test_classical*.py test_active_space*.py test_avas*.py test_molecular*.py test_molecule*.py test_geometry*.py test_hamiltonian*.py test_integral*.py test_fermion*.py test_reference*.py test_lowdin*.py test_mo_transform*.py test_precomputed*.py test_pre_quantum*.py test_restricted*.py test_spatial*.py test_oniom*.py test_ao_basis*.py test_bridges*.py test_create_solver*.py test_mock_external*.py test_cross_solver*.py test_inquanto*.py test_decomposition*.py test_plugin_registration*.py test_energy_components*.py
move_glob quantum test_*vqe*.py test_*adapt*.py test_*qse*.py test_*vqd*.py test_*iqeb*.py test_*sceom*.py test_*ucc*.py test_*qcc*.py test_h4_sto3g*.py test_lih_vqe*.py test_statevector*.py test_executor*.py test_pauli*.py test_qiskit*.py test_qulacs*.py test_algorithm*.py test_computable*.py test_property*.py test_gap_closure*.py test_l1_phase*.py test_qpe*.py test_zne*.py test_spam*.py test_mitigation*.py test_classical_shadows*.py test_tensornet*.py test_toy_dmrg*.py test_ucc_reference*.py test_uqc*.py test_scbk*.py
move_glob repro test_repro*.py test_export*.py test_observability*.py test_run_context*.py test_resource_summary*.py test_methods_resource*.py test_pec_literature*.py test_benchmark_dashboard*.py test_l3_*.py test_smoke_pipeline*.py test_check_parity*.py test_partial_l1*.py test_workflow_preview*.py test_workflow_coordinator*.py test_cli*.py test_secure_serialization*.py test_deprecation*.py test_sdk*.py test_build_prequantum*.py test_build_pre_quantum*.py test_validate_pre_quantum*.py test_pipeline*.py test_phase_bc*.py test_p4_*.py test_pbc_*.py test_backend*.py test_integration_philosophy*.py test_integrations*.py test_tier2*.py test_examples*.py test_gap_closure*.py test_computable*.py test_contracts*.py test_problem_bundle*.py test_protocol*.py
move_glob orchestration test_scf_stage*.py test_run_build_cache*.py 2>/dev/null || true

# Remaining flat tests -> integrations (glue/smoke) unless already in subdir
for f in test_*.py; do
  [[ -e "$f" ]] || continue
  git mv "$f" integrations/ 2>/dev/null || mv "$f" integrations/
done

echo "test reorg done"
