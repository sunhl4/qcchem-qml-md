"""Run summary attachment for pipeline repro."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.config.embedding_enums import DmetHamiltonianSource, EmbeddingMode
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels
from qchem_stack.config.embedding_specs import EmbeddingDmet, EmbeddingPlugin
from qchem_stack.config.quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    excited_qse_after_variational,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
    pauli_protocol_enabled,
)
from qchem_stack.contracts.schema_ids import (
    PIPELINE_PROFILE_V1,
    SCHMIDT_PER_FRAGMENT_VQE_V1,
)
from qchem_stack.orchestration.repro_summary_classical import classical_benchmark_summary
from qchem_stack.orchestration.repro_summary_quantum_tracks import (
    apply_quantum_and_demo_run_summary_fields,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig

__all__ = ["attach_run_summary", "classical_benchmark_summary"]


def attach_run_summary(out: dict[str, Any], cfg: ExperimentConfig) -> None:
    """Merge machine-readable stage list and resource hints into ``out['repro']``."""
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    q = cfg.quantum
    stages: list[str] = ["scf"]
    if cfg.embedding.mode == EmbeddingMode.PROJECTION:
        stages.append("projection_embedding_trace")
    if cfg.embedding.mode == EmbeddingMode.PLUGIN:
        stages.append("decomposition_plugin")
    if isinstance(cfg.embedding, EmbeddingDmet):
        schmidt = cfg.embedding.dmet.schmidt
        if cfg.embedding.dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
            if int(schmidt.dmet_max_cycles) > 1:
                stages.append("schmidt_dmet_density_feedback")
            elif schmidt.multi_fragment_atom_groups:
                stages.append("schmidt_embedding_multifragment_sweep")
            else:
                stages.append("schmidt_embedding_single_shot")
    stages.append("variational")
    spfv_out = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_out, dict) and spfv_out.get("schema") == SCHMIDT_PER_FRAGMENT_VQE_V1:
        stages.append("schmidt_per_fragment_vqe")
    if excited_vqd_after_variational(cfg) and "vqd" in out:
        stages.append("vqd")
    if excited_qse_after_variational(cfg) and "qse" in out:
        stages.append("qse")
    if excited_sceom_after_variational(cfg) and "sceom" in out:
        stages.append("sceom")
    if pauli_protocol_enabled(cfg) and "energy_pauli_protocol" in out:
        stages.append("pauli_averaging_protocol")
    sm: dict[str, Any] = {
        "stages_completed": stages,
        "quantum_algorithm": q.algorithm,
        "quantum_algorithm_yaml": q.algorithm,
        "classical_backend_id": str(cfg.scf.driver),
        "variational_ansatz_yaml": q.variational.ansatz,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(cfg),
        "energy_after_variational": out.get("energy_after_variational"),
        "mitigation_zne_mode_yaml": cfg.mitigation.zne.mode,
        "mitigation_zne_scales_yaml": [float(x) for x in cfg.mitigation.zne.scales],
        "spam_calibration_enabled_yaml": cfg.mitigation.stubs.spam_calibration,
        "classical_shadows_stub_enabled_yaml": cfg.mitigation.stubs.classical_shadows,
        "classical_shadows_budget_pairs_yaml": int(
            cfg.mitigation.stubs.classical_shadows_budget_pairs
        ),
        "embedding_input_representation_yaml": cfg.embedding.embedding_input_representation,
        "classical_benchmark_backend_yaml": cfg.chemistry_extended.benchmarks.backend,
    }
    if q.algorithm_factory:
        sm["quantum_algorithm_factory_yaml"] = q.algorithm_factory
    eis = out.get("embedding_input_system")
    if isinstance(eis, dict) and eis.get("schema") is not None:
        sm["embedding_input_system_schema"] = eis["schema"]
    ec = out.get("energy_components")
    if isinstance(ec, dict):
        sm["energy_components_present"] = True
        if ec.get("schema") is not None:
            sm["energy_components_schema"] = ec["schema"]
        if ec.get("mean_field_total_au") is not None:
            sm["energy_components_mean_field_total_au"] = float(ec["mean_field_total_au"])
        if ec.get("nuclear_repulsion_au") is not None:
            sm["energy_components_nuclear_repulsion_au"] = float(ec["nuclear_repulsion_au"])
    vm_rs = out.get("vqe_meta")
    if isinstance(vm_rs, dict) and vm_rs.get("uccsd_n_parameters") is not None:
        sm["uccsd_n_parameters"] = int(vm_rs["uccsd_n_parameters"])
    emb = cfg.embedding
    if isinstance(emb, EmbeddingDmet):
        dmet = emb.dmet
        sm["dmet_embedding_active"] = True
        sm["dmet_hamiltonian_source_yaml"] = dmet.hamiltonian_source
        frag_labels = nonempty_fragment_labels(emb)
        sm["dmet_fragment_count"] = len(frag_labels)
        sm["dmet_uniform_multifragment_toy_yaml"] = bool(dmet.uniform_multifragment_toy)
        sm["dmet_stub_one_shot_ledger_yaml"] = bool(
            cfg.parity_integrations.dmet_stub_one_shot_ledger
        )
    elif isinstance(emb, EmbeddingPlugin):
        sm["decomposition_plugin_yaml"] = emb.plugin.name
        wf = out.get("embedding_workflow")
        if isinstance(wf, dict):
            if wf.get("decomposition_primary_fragment_id") is not None:
                sm["decomposition_primary_fragment_id"] = wf["decomposition_primary_fragment_id"]
            if wf.get("decomposition_fragment_count") is not None:
                sm["decomposition_fragment_count"] = int(wf["decomposition_fragment_count"])
            if wf.get("decomposition_total_pauli_terms") is not None:
                sm["decomposition_total_pauli_terms"] = int(wf["decomposition_total_pauli_terms"])
    dfs_ledger = out.get("dmet_fragment_solve")
    if isinstance(dfs_ledger, dict):
        sm["dmet_fragment_solve_present"] = True
        if dfs_ledger.get("schema") is not None:
            sm["dmet_fragment_solve_schema"] = dfs_ledger["schema"]
    if isinstance(cfg.embedding, EmbeddingDmet):
        if cfg.embedding.dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
            sm["schmidt_dmet_max_cycles_yaml"] = int(cfg.embedding.dmet.schmidt.dmet_max_cycles)
        hm = out.get("hamiltonian_meta")
        if isinstance(hm, dict):
            aud = hm.get("schmidt_production_audit")
            if isinstance(aud, dict):
                dmet_sc = aud.get("schmidt_dmet_self_consistency")
                if isinstance(dmet_sc, dict):
                    ce = dmet_sc.get("cycles_executed")
                    if ce is None:
                        ce = dmet_sc.get("outer_cycles_executed")
                    if ce is not None:
                        sm["schmidt_dmet_cycles_executed"] = int(ce)
                    if (
                        dmet_sc.get("converged_early_on_gamma") is True
                        or dmet_sc.get("converged_early_on_sweep_max_delta") is True
                    ):
                        sm["schmidt_dmet_converged_early"] = True
    spfv_rs = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_rs, dict) and spfv_rs.get("schema") == SCHMIDT_PER_FRAGMENT_VQE_V1:
        frags = [f for f in (spfv_rs.get("fragments") or []) if isinstance(f, dict)]
        sm["schmidt_per_fragment_vqe_n_fragments"] = len(frags)
        sm["schmidt_per_fragment_vqe_total_nfev"] = sum(int(f.get("nfev", 0)) for f in frags)
        energies = [float(f["energy"]) for f in frags if f.get("energy") is not None]
        if energies:
            sm["schmidt_per_fragment_vqe_min_energy_au"] = min(energies)
            sm["schmidt_per_fragment_vqe_max_energy_au"] = max(energies)
    if out.get("scf_energy") is not None:
        sm["scf_energy"] = out["scf_energy"]
    pqi = out.get("pre_quantum_input")
    if isinstance(pqi, dict):
        if pqi.get("source") is not None:
            sm["pre_quantum_source"] = pqi["source"]
        if pqi.get("backend_tag") is not None:
            sm["pre_quantum_backend_tag"] = pqi["backend_tag"]
        if pqi.get("hamiltonian_branch") is not None:
            sm["pre_quantum_hamiltonian_branch"] = pqi["hamiltonian_branch"]
        if pqi.get("hamiltonian_fingerprint") is not None:
            sm["hamiltonian_fingerprint"] = pqi["hamiltonian_fingerprint"]
        if pqi.get("hamiltonian_fixed_before_variational") is not None:
            sm["hamiltonian_fixed_before_variational"] = bool(
                pqi["hamiltonian_fixed_before_variational"]
            )
        if pqi.get("classical_kernel_bindings") is not None:
            sm["classical_kernel_bindings"] = pqi["classical_kernel_bindings"]
        if pqi.get("classical_epistemic_bound") is not None:
            sm["classical_epistemic_bound"] = pqi["classical_epistemic_bound"]
    cache_stats = out.get("pre_quantum_build_cache")
    if isinstance(cache_stats, dict):
        if cache_stats.get("pack_builds") is not None:
            sm["pre_quantum_pack_builds"] = int(cache_stats["pack_builds"])
        if cache_stats.get("pack_hits") is not None:
            sm["pre_quantum_pack_hits"] = int(cache_stats["pack_hits"])
    cb = out.get("classical_benchmarks")
    if isinstance(cb, dict):
        sm["classical_benchmarks_present"] = True
        if cb.get("schema") is not None:
            sm["classical_benchmarks_schema"] = cb["schema"]
        for method_key in ("hf", "mp2", "ccsd", "casci"):
            blk = cb.get(method_key)
            if isinstance(blk, dict):
                if blk.get("status") is not None:
                    sm[f"classical_bench_{method_key}_status"] = str(blk["status"])
                if blk.get("value") is not None:
                    sm[f"classical_bench_{method_key}_energy_au"] = float(blk["value"])
    cbs = out.get("classical_benchmark_summary")
    if isinstance(cbs, dict):
        sm["classical_benchmark_summary_present"] = True
        if cbs.get("schema") is not None:
            sm["classical_benchmark_summary_schema"] = cbs["schema"]
        if cbs.get("recommended_baseline_method") is not None:
            sm["classical_benchmark_recommended_baseline_method"] = cbs[
                "recommended_baseline_method"
            ]
        if cbs.get("recommended_baseline_energy_au") is not None:
            sm["classical_benchmark_recommended_baseline_energy_au"] = float(
                cbs["recommended_baseline_energy_au"]
            )
        if cbs.get("best_method") is not None:
            sm["classical_benchmark_best_method"] = cbs["best_method"]
        if cbs.get("best_energy_au") is not None:
            sm["classical_benchmark_best_energy_au"] = float(cbs["best_energy_au"])
        if cbs.get("delta_best_vs_hf_au") is not None:
            sm["classical_benchmark_delta_best_vs_hf_au"] = float(cbs["delta_best_vs_hf_au"])
    rcorr = out.get("rdm_correction")
    if isinstance(rcorr, dict):
        sm["rdm_correction_present"] = True
        if rcorr.get("schema") is not None:
            sm["rdm_correction_schema"] = rcorr["schema"]
        if rcorr.get("method") is not None:
            sm["rdm_correction_method"] = rcorr["method"]
        if rcorr.get("status") is not None:
            sm["rdm_correction_status"] = rcorr["status"]
        if rcorr.get("energy_correction_au") is not None:
            sm["rdm_correction_energy_au"] = float(rcorr["energy_correction_au"])
    rr_ready = out.get("rdm_correction_readiness")
    if isinstance(rr_ready, dict):
        sm["rdm_correction_readiness_present"] = True
        if rr_ready.get("schema") is not None:
            sm["rdm_correction_readiness_schema"] = rr_ready["schema"]
        if rr_ready.get("requested_method") is not None:
            sm["rdm_correction_readiness_requested_method"] = rr_ready["requested_method"]
        if rr_ready.get("rdm1_source") is not None:
            sm["rdm_correction_readiness_rdm1_source"] = rr_ready["rdm1_source"]
        if rr_ready.get("rdm_basis") is not None:
            sm["rdm_correction_readiness_rdm_basis"] = rr_ready["rdm_basis"]
        if rr_ready.get("spin_model") is not None:
            sm["rdm_correction_readiness_spin_model"] = rr_ready["spin_model"]
        if rr_ready.get("reference_wavefunction") is not None:
            sm["rdm_correction_readiness_reference_wavefunction"] = rr_ready[
                "reference_wavefunction"
            ]
        if rr_ready.get("kernel_class") is not None:
            sm["rdm_correction_readiness_kernel_class"] = rr_ready["kernel_class"]
        if rr_ready.get("nevpt2_pyscf_status") is not None:
            sm["rdm_correction_readiness_nevpt2_pyscf_status"] = rr_ready["nevpt2_pyscf_status"]
    apply_quantum_and_demo_run_summary_fields(sm, out, cfg, repro)
    if isinstance(out.get("nexus_analog_ledger"), dict):
        sm["nexus_analog_hqc_units"] = out["nexus_analog_ledger"].get("hqc_units")
    if out.get("mitigation_graph_report"):
        sm["mitigation_graph_report_present"] = True
    if out.get("mitigation_dag_execution"):
        sm["mitigation_dag_execution_present"] = True
    from qchem_stack.config.mitigation_helpers import (
        build_mitigation_pec_literature_stub_v1,
        pec_literature_stub_enabled,
    )

    if pec_literature_stub_enabled(cfg.mitigation):
        sm["mitigation_pec_literature_stub_v1"] = build_mitigation_pec_literature_stub_v1()
    if isinstance(out.get("nexus_cloud_repro"), dict):
        sm["nexus_cloud_repro"] = out["nexus_cloud_repro"]
    psnap = repro.get("parity_snapshot")
    if isinstance(psnap, dict):
        qnx = psnap.get("qnexus_probe")
        if isinstance(qnx, dict) and "available" in qnx:
            sm["qnexus_client_probe_available"] = qnx.get("available")
        if psnap.get("tket_first_compiled_circuit_probe"):
            tp = psnap.get("tket_first_compiled_circuit_probe")
            if isinstance(tp, dict) and tp.get("ok") is True:
                sm["tket_first_circuit_stats_ok"] = True
        if psnap.get("dmet_one_shot_open_ledger"):
            sm["dmet_one_shot_open_ledger_present"] = True
            led = psnap.get("dmet_one_shot_open_ledger")
            if (
                isinstance(led, dict)
                and isinstance(led.get("fragments"), list)
                and led["fragments"]
            ):
                fe = led["fragments"][0].get("energy")
                if fe is not None:
                    sm["dmet_fragment_solve_energy"] = fe
        if psnap.get("dmet_solver_mode"):
            sm["dmet_solver_mode"] = psnap["dmet_solver_mode"]
        if psnap.get("open_gap_closure_reference"):
            sm["open_gap_closure_reference_present"] = True
        if psnap.get("dmet_uniform_multifragment_toy"):
            sm["dmet_uniform_multifragment_toy_present"] = True
        if isinstance(psnap.get("schmidt_per_fragment_vqe_summary"), dict):
            sm["schmidt_per_fragment_vqe_in_parity_snapshot"] = True
    pp = repro.get("pipeline_profile")
    if isinstance(pp, dict) and pp.get("schema") == PIPELINE_PROFILE_V1:
        if pp.get("total_wall_ms") is not None:
            sm["pipeline_total_wall_ms"] = pp["total_wall_ms"]
        stages_prof = pp.get("stages") or []
        if stages_prof:
            slow = max(stages_prof, key=lambda x: float(x.get("duration_ms", 0.0)))
            sm["pipeline_slowest_stage"] = slow.get("stage")
            sm["pipeline_slowest_stage_ms"] = slow.get("duration_ms")
    rc = repro.get("run_context")
    if isinstance(rc, dict) and rc.get("trace_id"):
        sm["trace_id"] = rc["trace_id"]
    if isinstance(rc, dict) and rc.get("client_request_id"):
        sm["client_request_id"] = rc["client_request_id"]
    ew = out.get("embedding_workflow")
    if isinstance(ew, dict):
        repro["embedding_workflow"] = ew
    repro["run_summary"] = sm
