"""Quantum algorithm / demo track fields for run_summary."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.config.quantum_helpers import (
    quantum_algorithm_report_run_summary_fields,
    quantum_demo_open_stack_yaml_flags,
    quantum_excited_run_summary_yaml_fields,
    quantum_variational_run_summary_yaml_fields,
    resolve_vqe_maxiter,
)
from qchem_stack.contracts.schema_ids import (
    QPE_OPEN_STACK_CONTRACT_V1,
    VQS_OPEN_STACK_CONTRACT_V1,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def apply_quantum_and_demo_run_summary_fields(
    sm: dict[str, Any],
    out: dict[str, Any],
    cfg: ExperimentConfig,
    repro: dict[str, Any],
) -> None:
    q = cfg.quantum
    sm.update(quantum_algorithm_report_run_summary_fields(out))
    if q.algorithm == "vqe":
        sm["vqe_maxiter_yaml"] = resolve_vqe_maxiter(cfg)
        if "nfev" in out:
            sm["vqe_nfev"] = out["nfev"]
    variational_yaml = quantum_variational_run_summary_yaml_fields(cfg)
    if q.algorithm in ("adapt", "tetris_adapt"):
        sm["adapt_pool_id_yaml"] = variational_yaml["adapt_pool_id_yaml"]
        sm["adapt_max_iter_yaml"] = variational_yaml["adapt_max_iter_yaml"]
        sm["adapt_grad_tol_yaml"] = variational_yaml["adapt_grad_tol_yaml"]
        am = out.get("adapt_meta")
        if isinstance(am, dict) and "total_gradient_evals" in am:
            sm["adapt_total_gradient_evals"] = am["total_gradient_evals"]
        if isinstance(am, dict) and am.get("grad_tol_used") is not None:
            sm["adapt_grad_tol_used"] = float(am["grad_tol_used"])
        if isinstance(am, dict):
            steps = am.get("adapt_steps")
            if isinstance(steps, list):
                sm["adapt_steps_recorded"] = len(steps)
        pool = out.get("adapt_pool")
        if isinstance(pool, list):
            sm["adapt_excitation_layers"] = len(pool)
    elif q.algorithm == "iqeb":
        sm["iqeb_pool_id_yaml"] = variational_yaml["iqeb_pool_id_yaml"]
        sm["iqeb_max_rounds_yaml"] = variational_yaml["iqeb_max_rounds_yaml"]
        sm["iqeb_pool_id_resolved"] = str(variational_yaml["iqeb_pool_id_yaml"])
        im = out.get("iqeb_meta")
        if isinstance(im, dict) and im.get("rounds") is not None:
            sm["iqeb_outer_rounds_recorded"] = int(im["rounds"])
        selected = out.get("iqeb_selected_pauli_strings")
        if selected is not None:
            sm["iqeb_selected_pauli_count"] = len(selected)
            sm["iqeb_selected_pauli_strings_head"] = list(selected[:8])
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
        if pc.get("classical_shadows_expectation") is not None:
            sm["protocol_classical_shadows_expectation"] = pc["classical_shadows_expectation"]
        if pc.get("classical_shadows_runtime"):
            sm["protocol_classical_shadows_runtime"] = pc["classical_shadows_runtime"]
    vqd = out.get("vqd")
    excited_yaml = quantum_excited_run_summary_yaml_fields(cfg)
    if isinstance(vqd, dict):
        sm.update(
            {
                k: excited_yaml[k]
                for k in (
                    "vqd_n_states_yaml",
                    "vqd_overlap_exponent_yaml",
                    "vqd_cobyla_maxiter_yaml",
                    "vqd_optimizer_method_yaml",
                    "vqd_init_strategy_yaml",
                    "vqd_overlap_mode_yaml",
                )
            }
        )
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
            if vm.get("vqd_warnings"):
                sm["vqd_warnings_present"] = True
            if vm.get("vqd_variety_yaml"):
                sm["vqd_variety_yaml"] = vm["vqd_variety_yaml"]
    qse_out = out.get("qse")
    if isinstance(qse_out, dict):
        sm.update(
            {
                k: excited_yaml[k]
                for k in ("qse_shot_mode", "qse_subspace_dim_yaml", "qse_max_basis_yaml")
            }
        )
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
        sm.update(
            {
                k: excited_yaml[k]
                for k in (
                    "sceom_shots_per_matrix_element",
                    "sceom_subspace_dim_yaml",
                    "sceom_generator_strategy_yaml",
                )
            }
        )
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
        demo_flags = quantum_demo_open_stack_yaml_flags(cfg)
        sm["qpe_demo_track_ran"] = True
        sm["qpe_open_stack_contract_v1"] = {
            "schema": QPE_OPEN_STACK_CONTRACT_V1,
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
                "qpe_demo_track_after_variational": demo_flags["qpe_demo_track_after_variational"],
                "qpe_pipeline_integration": demo_flags["qpe_pipeline_integration"],
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
        demo_flags = quantum_demo_open_stack_yaml_flags(cfg)
        sm["vqs_track_ran"] = True
        sm["vqs_open_stack_contract_v1"] = {
            "schema": VQS_OPEN_STACK_CONTRACT_V1,
            "track_payload_schema": out["vqs_track"].get("schema"),
            "implementations": {
                "vqs": "qchem_stack.quantum.algorithms.vqs.AlgorithmVQS",
                "mclachlan_real_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanRealTime",
                "mclachlan_imag_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanImagTime",
            },
            "pipeline_track_module": "qchem_stack.quantum.algorithms.vqs_pipeline_track",
            "yaml_flags": {
                "vqs_track_after_variational": demo_flags["vqs_track_after_variational"],
                "vqs_pipeline_integration": demo_flags["vqs_pipeline_integration"],
                "vqs_rhs_mode_yaml": demo_flags["vqs_rhs_mode_yaml"],
                "vqs_tangent_fd_epsilon_yaml": demo_flags["vqs_tangent_fd_epsilon_yaml"],
            },
            "vqs_mode_yaml": demo_flags["vqs_mode_yaml"],
            "pipeline_attach": "_attach_vqs_track_if_requested (orchestration/pipeline.py)",
        }
