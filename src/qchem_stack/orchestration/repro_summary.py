from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig
from qchem_stack.protocols.product_contract import classify_pauli_expectation_path


def classical_benchmark_summary(cb: dict[str, Any]) -> dict[str, Any]:
    """Compact Methods-friendly digest for ``classical_benchmarks``."""
    rows: dict[str, dict[str, Any]] = {}
    for method_key in ("hf", "mp2", "ccsd", "casci"):
        v = cb.get(method_key)
        if isinstance(v, dict):
            rows[method_key] = v
    ok_vals: dict[str, float] = {}
    for k, row in rows.items():
        if row.get("status") == "ok" and row.get("value") is not None:
            ok_vals[k] = float(row["value"])
    hf = ok_vals.get("hf")
    best_method: str | None = None
    best_energy: float | None = None
    if ok_vals:
        best_method = min(ok_vals, key=ok_vals.get)
        best_energy = float(ok_vals[best_method])
    deltas_vs_hf: dict[str, float] = {}
    if hf is not None:
        for k, v in ok_vals.items():
            if k == "hf":
                continue
            deltas_vs_hf[k] = float(v - hf)
    recommended_baseline_method: str | None = None
    for preferred in ("ccsd", "mp2", "hf"):
        if preferred in ok_vals:
            recommended_baseline_method = preferred
            break
    recommended_baseline_energy: float | None = (
        float(ok_vals[recommended_baseline_method])
        if recommended_baseline_method is not None
        else None
    )
    return {
        "schema": "classical_benchmark_summary_v1",
        "recommended_baseline_policy": "prefer_ccsd_else_mp2_else_hf",
        "recommended_baseline_method": recommended_baseline_method,
        "recommended_baseline_energy_au": recommended_baseline_energy,
        "methods_reported": sorted(rows.keys()),
        "methods_ok": sorted(ok_vals.keys()),
        "methods_non_ok": sorted(k for k in rows if k not in ok_vals),
        "reference_hf_energy_au": hf,
        "best_method": best_method,
        "best_energy_au": best_energy,
        "delta_best_vs_hf_au": (
            float(best_energy - hf) if (best_energy is not None and hf is not None) else None
        ),
        "method_deltas_vs_hf_au": deltas_vs_hf,
    }


def attach_run_summary(out: dict[str, Any], cfg: ExperimentConfig) -> None:
    """Merge machine-readable stage list and resource hints into ``out['repro']``."""
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    q = cfg.quantum
    stages: list[str] = ["scf"]
    if cfg.embedding.mode == "projection":
        stages.append("projection_embedding_trace")
    if cfg.embedding.mode == "plugin":
        stages.append("decomposition_plugin")
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        if int(cfg.embedding.schmidt_dmet_max_cycles) > 1:
            stages.append("schmidt_dmet_density_feedback")
        elif cfg.embedding.schmidt_multi_fragment_atom_groups:
            stages.append("schmidt_embedding_multifragment_sweep")
        else:
            stages.append("schmidt_embedding_single_shot")
    stages.append("variational")
    spfv_out = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_out, dict) and spfv_out.get("schema") == "schmidt_per_fragment_vqe_v1":
        stages.append("schmidt_per_fragment_vqe")
    if q.vqd_after_variational and "vqd" in out:
        stages.append("vqd")
    if q.qse_after_variational and "qse" in out:
        stages.append("qse")
    if q.sceom_after_variational and "sceom" in out:
        stages.append("sceom")
    if q.use_pauli_protocol and "energy_pauli_protocol" in out:
        stages.append("pauli_averaging_protocol")
    sm: dict[str, Any] = {
        "stages_completed": stages,
        "quantum_algorithm": q.algorithm,
        "quantum_algorithm_yaml": q.algorithm,
        "classical_backend_id": str(cfg.scf.driver),
        "variational_ansatz_yaml": q.variational_ansatz,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(q),
        "energy_after_variational": out.get("energy_after_variational"),
        "mitigation_zne_mode_yaml": cfg.mitigation.zne_mode,
        "mitigation_zne_scales_yaml": [float(x) for x in cfg.mitigation.zne_scales],
        "spam_calibration_enabled_yaml": cfg.mitigation.spam_calibration_enabled,
        "classical_shadows_stub_enabled_yaml": cfg.mitigation.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs_yaml": int(cfg.mitigation.classical_shadows_budget_pairs),
        "embedding_input_representation_yaml": cfg.embedding.embedding_input_representation,
        "classical_benchmark_backend_yaml": cfg.chemistry_extended.classical_benchmark_backend,
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
    if emb.mode == "dmet":
        sm["dmet_embedding_active"] = True
        sm["dmet_hamiltonian_source_yaml"] = emb.dmet_hamiltonian_source
        frag_labels = [x for x in (emb.fragment_labels or []) if str(x).strip()]
        sm["dmet_fragment_count"] = len(frag_labels)
        sm["dmet_uniform_multifragment_toy_yaml"] = bool(emb.dmet_uniform_multifragment_toy)
        sm["dmet_stub_one_shot_ledger_yaml"] = bool(
            cfg.parity_integrations.dmet_stub_one_shot_ledger
        )
    elif emb.mode == "plugin":
        sm["decomposition_plugin_yaml"] = emb.decomposition_plugin
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
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        sm["schmidt_dmet_max_cycles_yaml"] = int(cfg.embedding.schmidt_dmet_max_cycles)
        hm = out.get("hamiltonian_meta")
        if isinstance(hm, dict):
            aud = hm.get("schmidt_production_audit")
            if isinstance(aud, dict):
                dmet = aud.get("schmidt_dmet_self_consistency")
                if isinstance(dmet, dict):
                    ce = dmet.get("cycles_executed")
                    if ce is None:
                        ce = dmet.get("outer_cycles_executed")
                    if ce is not None:
                        sm["schmidt_dmet_cycles_executed"] = int(ce)
                    if (
                        dmet.get("converged_early_on_gamma") is True
                        or dmet.get("converged_early_on_sweep_max_delta") is True
                    ):
                        sm["schmidt_dmet_converged_early"] = True
    spfv_rs = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_rs, dict) and spfv_rs.get("schema") == "schmidt_per_fragment_vqe_v1":
        frags = [f for f in (spfv_rs.get("fragments") or []) if isinstance(f, dict)]
        sm["schmidt_per_fragment_vqe_n_fragments"] = len(frags)
        sm["schmidt_per_fragment_vqe_total_nfev"] = sum(int(f.get("nfev", 0)) for f in frags)
        energies = [float(f["energy"]) for f in frags if f.get("energy") is not None]
        if energies:
            sm["schmidt_per_fragment_vqe_min_energy_au"] = min(energies)
            sm["schmidt_per_fragment_vqe_max_energy_au"] = max(energies)
    if out.get("scf_energy") is not None:
        sm["scf_energy"] = out["scf_energy"]
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
    if q.algorithm == "vqe":
        sm["vqe_maxiter_yaml"] = q.vqe_maxiter
        if "nfev" in out:
            sm["vqe_nfev"] = out["nfev"]
    elif q.algorithm in ("adapt", "tetris_adapt"):
        sm["adapt_pool_id_yaml"] = q.adapt_pool_id
        sm["adapt_max_iter_yaml"] = q.adapt_max_iter
        am = out.get("adapt_meta")
        if isinstance(am, dict) and "total_gradient_evals" in am:
            sm["adapt_total_gradient_evals"] = am["total_gradient_evals"]
        if isinstance(am, dict):
            steps = am.get("adapt_steps")
            if isinstance(steps, list):
                sm["adapt_steps_recorded"] = len(steps)
        pool = out.get("adapt_pool")
        if isinstance(pool, list):
            sm["adapt_excitation_layers"] = len(pool)
    elif q.algorithm == "iqeb":
        sm["iqeb_pool_id_yaml"] = q.iqeb_pool_id
        sm["iqeb_max_rounds_yaml"] = q.iqeb_max_rounds
        im = out.get("iqeb_meta")
        if isinstance(im, dict) and im.get("rounds") is not None:
            sm["iqeb_outer_rounds_recorded"] = int(im["rounds"])
        if out.get("iqeb_selected_pauli_strings") is not None:
            sm["iqeb_selected_pauli_count"] = len(out["iqeb_selected_pauli_strings"])
        if "nfev" in out:
            sm["iqeb_final_inner_vqe_nfev"] = out["nfev"]
        sm["iqeb_implementation_path"] = "qchem_stack.quantum.algorithms.iqeb.IQEBVQE"
    rs = out.get("resource_summary")
    if isinstance(rs, dict):
        if "sum_shots_total_with_excited_upper_bound" in rs:
            sm["sum_shots_total_with_excited_upper_bound"] = rs[
                "sum_shots_total_with_excited_upper_bound"
            ]
        if "excited_shots_upper_bound" in rs:
            sm["excited_shots_upper_bound"] = rs["excited_shots_upper_bound"]
        if "pauli_averaging_protocol_ran" in rs:
            sm["pauli_averaging_protocol_ran"] = rs["pauli_averaging_protocol_ran"]
        if "sum_shots" in rs:
            sm["sum_shots_backend_protocol"] = rs["sum_shots"]
        if rs.get("n_pauli_terms") is not None:
            sm["n_pauli_terms"] = rs["n_pauli_terms"]
        if rs.get("n_pauli_groups") is not None:
            sm["n_pauli_groups"] = rs["n_pauli_groups"]
        if rs.get("n_circuits") is not None:
            sm["n_circuits"] = rs["n_circuits"]
        if rs.get("n_qubits") is not None:
            sm["n_qubits"] = rs["n_qubits"]
    if out.get("energy_pauli_protocol") is not None:
        sm["energy_pauli_protocol"] = out["energy_pauli_protocol"]
    pc = out.get("protocol_counts")
    if isinstance(pc, dict):
        if pc.get("expectation_source"):
            sm["protocol_expectation_source"] = pc["expectation_source"]
        if pc.get("zne_mode") is not None:
            sm["protocol_zne_mode"] = pc["zne_mode"]
        if pc.get("energy_stderr_model"):
            sm["protocol_energy_stderr_model"] = pc["energy_stderr_model"]
        if pc.get("total_shots_budget") is not None:
            sm["protocol_total_shots_budget"] = pc["total_shots_budget"]
        if pc.get("n_measurement_circuits") is not None:
            sm["protocol_n_measurement_circuits"] = pc["n_measurement_circuits"]
        if pc.get("shots_per_circuit_effective") is not None:
            sm["protocol_shots_per_circuit_effective"] = pc["shots_per_circuit_effective"]
        if pc.get("energy_stderr") is not None:
            sm["protocol_energy_stderr"] = pc["energy_stderr"]
        if isinstance(pc.get("pmsv_report"), dict):
            sm["protocol_pmsv_report"] = pc["pmsv_report"]
    vqd = out.get("vqd")
    if isinstance(vqd, dict):
        sm["vqd_n_states_yaml"] = q.vqd_n_states
        sm["vqd_overlap_exponent_yaml"] = float(q.vqd_overlap_exponent)
        sm["vqd_cobyla_maxiter_yaml"] = int(q.vqd_cobyla_maxiter)
        en = vqd.get("energies")
        if isinstance(en, list):
            sm["vqd_n_energies_recorded"] = len(en)
            sm["vqd_deflation_levels_completed"] = max(0, len(en) - 1)
        vm = vqd.get("meta")
        if isinstance(vm, dict):
            if "reused_pipeline_ground" in vm:
                sm["vqd_reused_pipeline_ground"] = vm["reused_pipeline_ground"]
            ch = vm.get("vqd_channels")
            if isinstance(ch, list):
                sm["vqd_three_protocol_present"] = any(
                    isinstance(c, dict) and "three_protocol" in c for c in ch
                )
                sm["vqd_channels_count"] = len(ch)
            if vm.get("shots_objective") is not None:
                sm["vqd_shots_objective_yaml"] = vm["shots_objective"]
            if vm.get("shots_overlap") is not None:
                sm["vqd_shots_overlap_yaml"] = vm["shots_overlap"]
            if vm.get("shots_weight") is not None:
                sm["vqd_shots_weight_yaml"] = vm["shots_weight"]
            sm["vqd_optimizer_method_yaml"] = q.vqd_optimizer_method
            sm["vqd_init_strategy_yaml"] = q.vqd_init_strategy
            sm["vqd_overlap_mode_yaml"] = q.vqd_overlap_mode
            if vm.get("vqd_warnings"):
                sm["vqd_warnings_present"] = True
            if vm.get("vqd_variety_yaml"):
                sm["vqd_variety_yaml"] = vm["vqd_variety_yaml"]
    qse_out = out.get("qse")
    if isinstance(qse_out, dict):
        sm["qse_shot_mode"] = q.qse_shot_mode
        sm["qse_subspace_dim_yaml"] = q.qse_subspace_dim
        sm["qse_max_basis_yaml"] = q.qse_max_basis
        exc = qse_out.get("excitation_energies")
        if isinstance(exc, list):
            sm["qse_n_excitation_energies"] = len(exc)
        qmeta = qse_out.get("meta")
        if isinstance(qmeta, dict):
            if qmeta.get("shot_noise_model"):
                sm["qse_shot_noise_model"] = qmeta["shot_noise_model"]
            if qmeta.get("K") is not None:
                sm["qse_basis_dimension_K"] = qmeta["K"]
            sched = qmeta.get("qse_pauli_transition_schedule")
            if isinstance(sched, dict):
                if sched.get("n_transition_tasks") is not None:
                    sm["qse_n_transition_tasks"] = sched["n_transition_tasks"]
                if sched.get("total_shots_upper_bound") is not None:
                    sm["qse_total_shots_upper_bound"] = sched["total_shots_upper_bound"]
    sceom_out = out.get("sceom")
    if isinstance(sceom_out, dict):
        sm["sceom_shots_per_matrix_element"] = q.sceom_shots_per_matrix_element
        sm["sceom_subspace_dim_yaml"] = q.sceom_subspace_dim
        sm["sceom_generator_strategy_yaml"] = q.sceom_generator_strategy
        sce = sceom_out.get("energies")
        if isinstance(sce, list):
            sm["sceom_n_energies_recorded"] = len(sce)
        sceom_meta = sceom_out.get("meta")
        if isinstance(sceom_meta, dict):
            if sceom_meta.get("shot_noise_model") is not None:
                sm["sceom_shot_noise_model"] = sceom_meta["shot_noise_model"]
            if sceom_meta.get("subspace_dim") is not None:
                sm["sceom_active_generator_count"] = int(sceom_meta["subspace_dim"])
            if sceom_meta.get("construction") is not None:
                sm["sceom_matrix_construction"] = str(sceom_meta["construction"])
    job = out.get("job")
    if isinstance(job, dict):
        if job.get("job_id") is not None:
            sm["async_job_id"] = job["job_id"]
        if job.get("protocol_hash") is not None:
            sm["protocol_hash_prefix"] = job["protocol_hash"]
    jr = out.get("job_result")
    if isinstance(jr, dict):
        if jr.get("expectation") is not None:
            sm["job_async_expectation"] = jr["expectation"]
        if jr.get("energy_stderr") is not None:
            sm["job_async_energy_stderr"] = jr["energy_stderr"]
        if jr.get("total_shots_budget") is not None:
            sm["job_async_total_shots_budget"] = jr["total_shots_budget"]
    if isinstance(out.get("qpe_demo_track"), dict):
        sm["qpe_demo_track_ran"] = True
        sm["qpe_open_stack_contract_v1"] = {
            "schema": "qpe_open_stack_contract_v1",
            "demo_track_payload_schema": out["qpe_demo_track"].get("schema"),
            "kitaev_dense_energy_fn": (
                "qchem_stack.qpe_qec_demo.pipeline_track.kitaev_qpe_energy_estimate — dense phase readout shortcut"
            ),
            "algorithm_classes": {
                "kitaev": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
                "info_theory": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
                "deterministic": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
            },
            "bayesian_stub": "qchem_stack.qpe_qec_demo.BayesianQPEStub",
            "yaml_flags": {
                "qpe_demo_track_after_variational": q.qpe_demo_track_after_variational,
                "qpe_pipeline_integration": q.qpe_pipeline_integration,
            },
            "pipeline_attach": "_attach_qpe_demo_track_if_requested (orchestration/pipeline.py)",
        }
    if isinstance(out.get("qpe_algorithm_three_pack"), dict):
        qp3 = out["qpe_algorithm_three_pack"]
        sm["qpe_three_pack_ran"] = True
        sm["qpe_three_pack_deterministic_energy_est"] = (
            qp3.get("deterministic_qpe_report_v1") or {}
        ).get("energy_estimate")
        sm["qpe_three_pack_kitaev_energy_est"] = (qp3.get("kitaev_qpe_report_v1") or {}).get(
            "energy_estimate"
        )
        sm["qpe_three_pack_info_theory_energy_est"] = (
            qp3.get("info_theory_qpe_report_v1") or {}
        ).get("energy_estimate")
    if isinstance(out.get("vqs_track"), dict):
        sm["vqs_track_ran"] = True
        sm["vqs_open_stack_contract_v1"] = {
            "schema": "vqs_open_stack_contract_v1",
            "track_payload_schema": out["vqs_track"].get("schema"),
            "implementations": {
                "vqs": "qchem_stack.quantum.algorithms.vqs.AlgorithmVQS",
                "mclachlan_real_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanRealTime",
                "mclachlan_imag_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanImagTime",
            },
            "pipeline_track_module": "qchem_stack.quantum.algorithms.vqs_pipeline_track",
            "yaml_flags": {
                "vqs_track_after_variational": q.vqs_track_after_variational,
                "vqs_pipeline_integration": q.vqs_pipeline_integration,
                "vqs_rhs_mode_yaml": q.vqs_rhs_mode,
                "vqs_tangent_fd_epsilon_yaml": float(q.vqs_tangent_fd_epsilon),
            },
            "vqs_mode_yaml": q.vqs_mode,
            "pipeline_attach": "_attach_vqs_track_if_requested (orchestration/pipeline.py)",
        }
    if isinstance(out.get("nexus_analog_ledger"), dict):
        sm["nexus_analog_hqc_units"] = out["nexus_analog_ledger"].get("hqc_units")
    if out.get("mitigation_graph_report"):
        sm["mitigation_graph_report_present"] = True
    if out.get("mitigation_dag_execution"):
        sm["mitigation_dag_execution_present"] = True
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
    if isinstance(pp, dict) and pp.get("schema") == "pipeline_profile_v1":
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
