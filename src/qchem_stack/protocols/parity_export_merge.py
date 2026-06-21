"""Parity export building blocks (split from parity_criteria_export)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
from qchem_stack.protocols.computable import computables_export_dict


def _truncate_pauli_support_for_export(out: dict[str, Any], *, max_pauli: int | None) -> None:
    if max_pauli is None or max_pauli < 0:
        return
    key = "hamiltonian_pauli_strings_mirror_protocol_counts"
    xs = out.get(key)
    if isinstance(xs, list) and len(xs) > max_pauli:
        out[key] = xs[:max_pauli]
        out["hamiltonian_pauli_strings_truncated"] = True
        out["hamiltonian_pauli_strings_omitted_count"] = len(xs) - max_pauli


def _merge_pipeline_results(
    out: dict[str, Any],
    *,
    config_path: Path,
    data: dict[str, Any],
) -> None:
    repro_raw = data.get("repro")
    repro: dict[str, Any] = repro_raw if isinstance(repro_raw, dict) else {}
    out["parity_snapshot_from_run"] = repro.get("parity_snapshot")
    rsum = repro.get("run_summary")
    out["run_summary_from_repro"] = rsum
    out["scf_energy_from_run"] = data.get("scf_energy")
    out["energy_after_variational_from_run"] = data.get("energy_after_variational")
    out["energy_pauli_protocol_from_run"] = data.get("energy_pauli_protocol")
    jr = data.get("job_result")
    if isinstance(jr, dict):
        out["job_async_expectation_from_run"] = jr.get("expectation")
        out["job_async_energy_stderr_from_run"] = jr.get("energy_stderr")
    rsg = data.get("resource_summary")
    out["resource_summary_from_run"] = rsg
    if isinstance(rsg, dict):
        out["sum_shots_total_with_excited_upper_bound_from_run"] = rsg.get(
            "sum_shots_total_with_excited_upper_bound"
        )
        out["excited_shots_upper_bound_from_run"] = rsg.get("excited_shots_upper_bound")
        out["excited_shot_accounting_from_run"] = rsg.get("excited_shot_accounting")
    out["protocol_expectation_source"] = None
    pc = data.get("protocol_counts")
    if isinstance(pc, dict):
        out["protocol_expectation_source"] = pc.get("expectation_source")
        out["protocol_energy_stderr_model"] = pc.get("energy_stderr_model")
        if isinstance(pc.get("pmsv_report"), dict):
            out["protocol_pmsv_report_from_run"] = pc.get("pmsv_report")
        hp = pc.get("hamiltonian_pauli_strings")
        if isinstance(hp, list):
            out["hamiltonian_pauli_strings_mirror_protocol_counts"] = list(hp)
        if pc.get("n_hamiltonian_pauli_terms") is not None:
            out["n_hamiltonian_pauli_terms_from_run"] = pc.get("n_hamiltonian_pauli_terms")
        if pc.get("pauli_group_ids") is not None:
            out["pauli_group_ids_from_run"] = pc.get("pauli_group_ids")
    hm = data.get("hamiltonian_meta")
    if isinstance(hm, dict) and hm.get("hamiltonian_fingerprint") is not None:
        out["hamiltonian_fingerprint_from_run"] = hm.get("hamiltonian_fingerprint")
    pqi = data.get("pre_quantum_input")
    if isinstance(pqi, dict):
        out["pre_quantum_input_from_run"] = {
            k: pqi[k]
            for k in (
                "schema",
                "source",
                "backend_tag",
                "integral_source",
                "fermion_to_qubit_map",
                "hamiltonian_fingerprint",
                "reference_energy_au",
                "scf_energy_au",
                "n_active_orbitals",
                "n_active_electrons",
                "hamiltonian_branch",
                "hamiltonian_fixed_before_variational",
                "post_variational_embedding_audit_only",
            )
            if k in pqi and pqi[k] is not None
        }
    pbc = data.get("pre_quantum_build_cache")
    if isinstance(pbc, dict):
        out["pre_quantum_build_cache_from_run"] = dict(pbc)
    cb = data.get("classical_benchmarks")
    if isinstance(cb, dict):
        out["classical_benchmarks_from_run"] = cb
    cbs = data.get("classical_benchmark_summary")
    if isinstance(cbs, dict):
        out["classical_benchmark_summary_from_run"] = cbs
    rcorr = data.get("rdm_correction")
    if isinstance(rcorr, dict):
        out["rdm_correction_from_run"] = rcorr
    rr_read = data.get("rdm_correction_readiness")
    if isinstance(rr_read, dict):
        out["rdm_correction_readiness_from_run"] = rr_read
    ecmp = data.get("energy_components")
    if isinstance(ecmp, dict):
        out["energy_components_from_run"] = ecmp
    out["excited_resource_summary_from_run"] = data.get("excited_resource_summary")
    if isinstance(rsum, dict):
        for key in (
            "n_pauli_terms",
            "n_pauli_groups",
            "n_circuits",
            "n_qubits",
            "energy_pauli_protocol",
            "async_job_id",
            "protocol_hash_prefix",
            "protocol_total_shots_budget",
            "protocol_n_measurement_circuits",
            "protocol_shots_per_circuit_effective",
            "protocol_energy_stderr",
            "job_async_expectation",
            "job_async_energy_stderr",
            "job_async_total_shots_budget",
            "vqd_n_states_yaml",
            "vqd_n_energies_recorded",
            "vqd_deflation_levels_completed",
            "vqd_channels_count",
            "vqd_shots_objective_yaml",
            "vqd_shots_overlap_yaml",
            "vqd_shots_weight_yaml",
            "qse_subspace_dim_yaml",
            "qse_max_basis_yaml",
            "qse_basis_dimension_K",
            "qse_n_excitation_energies",
            "qse_n_transition_tasks",
            "qse_total_shots_upper_bound",
            "sceom_subspace_dim_yaml",
            "sceom_n_energies_recorded",
            "sceom_active_generator_count",
            "sceom_matrix_construction",
            "dmet_embedding_active",
            "dmet_hamiltonian_source_yaml",
            "dmet_fragment_count",
            "decomposition_primary_fragment_id",
            "decomposition_fragment_count",
            "decomposition_total_pauli_terms",
            "mitigation_zne_mode_yaml",
            "mitigation_zne_scales_yaml",
            "dmet_uniform_multifragment_toy_yaml",
            "dmet_stub_one_shot_ledger_yaml",
            "dmet_fragment_solve_present",
            "dmet_fragment_solve_schema",
            "protocol_zne_mode",
            "variational_ansatz_yaml",
            "uccsd_n_parameters",
            "classical_benchmarks_present",
            "classical_benchmarks_schema",
            "classical_bench_hf_status",
            "classical_bench_hf_energy_au",
            "classical_bench_mp2_status",
            "classical_bench_mp2_energy_au",
            "classical_bench_ccsd_status",
            "classical_bench_ccsd_energy_au",
            "classical_bench_casci_status",
            "classical_bench_casci_energy_au",
            "classical_benchmark_summary_present",
            "classical_benchmark_summary_schema",
            "classical_benchmark_recommended_baseline_method",
            "classical_benchmark_recommended_baseline_energy_au",
            "classical_benchmark_best_method",
            "classical_benchmark_best_energy_au",
            "classical_benchmark_delta_best_vs_hf_au",
            "embedding_input_representation_yaml",
            "embedding_input_system_schema",
            "energy_components_present",
            "energy_components_schema",
            "energy_components_mean_field_total_au",
            "energy_components_nuclear_repulsion_au",
            "rdm_correction_present",
            "rdm_correction_schema",
            "rdm_correction_method",
            "rdm_correction_status",
            "rdm_correction_energy_au",
            "rdm_correction_readiness_present",
            "rdm_correction_readiness_schema",
            "rdm_correction_readiness_requested_method",
            "rdm_correction_readiness_rdm1_source",
            "rdm_correction_readiness_reference_wavefunction",
            "rdm_correction_readiness_kernel_class",
            "rdm_correction_readiness_nevpt2_pyscf_status",
            "pre_quantum_source",
            "pre_quantum_backend_tag",
            "pre_quantum_hamiltonian_branch",
            "hamiltonian_fingerprint",
            "hamiltonian_fixed_before_variational",
            "pre_quantum_pack_builds",
            "pre_quantum_pack_hits",
        ):
            if key in rsum and rsum[key] is not None:
                out[f"{key}_mirror_run_summary"] = rsum[key]
    out["computable_abstract"] = computables_export_dict(
        load_experiment_config(config_path),
        protocol_counts=pc if isinstance(pc, dict) else None,
    )
    ew = data.get("embedding_workflow")
    if isinstance(ew, dict):
        out["embedding_workflow_from_run"] = ew
    if isinstance(data.get("adapt_meta"), dict):
        out["adapt_meta_from_run"] = data["adapt_meta"]
    apool = data.get("adapt_pool")
    if isinstance(apool, list):
        out["adapt_pool_from_run"] = apool
    if isinstance(data.get("iqeb_meta"), dict):
        out["iqeb_meta_from_run"] = data["iqeb_meta"]
    isp = data.get("iqeb_selected_pauli_strings")
    if isinstance(isp, list):
        out["iqeb_selected_pauli_strings_from_run"] = isp
    qdt = data.get("qpe_demo_track")
    if isinstance(qdt, dict):
        out["qpe_demo_track_from_run"] = {
            "schema": qdt.get("schema"),
            "has_kitaev": qdt.get("kitaev_ground_energy_dense") is not None,
            "has_bayesian_stub": qdt.get("bayesian_phase_map_toy") is not None,
        }
    vtr = data.get("vqs_track")
    if isinstance(vtr, dict):
        out["vqs_track_from_run"] = {
            "schema": vtr.get("schema"),
            "has_energy_observable": bool(vtr.get("energy_observable")),
            "vqs_mode_from_run": vtr.get("vqs_mode"),
        }
    out["methods_resource_unified_v1"] = build_methods_resource_unified_v1(data)
    if isinstance(rsum, dict) and rsum.get("qpe_demo_track_ran"):
        out["qpe_demo_track_ran_from_run_summary"] = True
    if isinstance(rsum, dict) and rsum.get("vqs_track_ran"):
        out["vqs_track_ran_from_run_summary"] = True
    if isinstance(rsum, dict):
        if rsum.get("vqd_three_protocol_present") is not None:
            out["vqd_three_protocol_present_from_run_summary"] = rsum["vqd_three_protocol_present"]
        if rsum.get("qse_shot_mode") is not None:
            out["qse_shot_mode_from_run_summary"] = rsum["qse_shot_mode"]
        if rsum.get("sceom_shot_noise_model") is not None:
            out["sceom_shot_noise_model_from_run_summary"] = rsum["sceom_shot_noise_model"]
    psnap = repro.get("parity_snapshot")
    if isinstance(psnap, dict):
        for k in (
            "tensornet_engine_resolved",
            "tensornet_fallback_reason",
            "variational_ansatz",
            "uccsd_n_parameters",
        ):
            if psnap.get(k) is not None:
                out[f"{k}_from_parity_snapshot"] = psnap[k]
        ogr = psnap.get("open_gap_closure_reference")
        if isinstance(ogr, dict) and ogr.get("schema") is not None:
            out["open_gap_closure_reference_schema_from_run"] = ogr.get("schema")
        ph = psnap.get("pre_quantum_handoff_v1")
        if isinstance(ph, dict):
            out["pre_quantum_handoff_v1_from_parity_snapshot"] = dict(ph)
        pbc_snap = psnap.get("pre_quantum_build_cache_v1")
        if isinstance(pbc_snap, dict):
            out["pre_quantum_build_cache_v1_from_parity_snapshot"] = dict(pbc_snap)
    vqd_block = data.get("vqd")
    if isinstance(vqd_block, dict):
        vmeta = vqd_block.get("meta")
        if isinstance(vmeta, dict):
            ch = vmeta.get("vqd_channels")
            if isinstance(ch, list):
                out["vqd_three_protocol_present_from_run"] = any(
                    isinstance(c, dict) and "three_protocol" in c for c in ch
                )
    qse_block = data.get("qse")
    if isinstance(qse_block, dict):
        qm = qse_block.get("meta")
        if isinstance(qm, dict) and qm.get("qse_shot_mode") is not None:
            out["qse_shot_mode_from_run_meta"] = qm.get("qse_shot_mode")
    sceom_block = data.get("sceom")
    if isinstance(sceom_block, dict):
        sm = sceom_block.get("meta")
        if isinstance(sm, dict):
            out["sceom_shot_noise_model_from_run"] = sm.get("shot_noise_model")
            if sm.get("shots_per_matrix_element") is not None:
                out["sceom_shots_per_matrix_element_from_run"] = sm["shots_per_matrix_element"]
