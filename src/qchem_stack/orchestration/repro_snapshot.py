from __future__ import annotations

from typing import Any

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ExperimentConfig, compiler_bundle_signature_from_config
from qchem_stack.protocols.product_contract import classify_pauli_expectation_path


def append_open_stack_parity_fields(snap: dict[str, Any], cfg: ExperimentConfig) -> None:
    """Designed open-stack parity block (public-contract L1)."""
    pis = cfg.parity_integrations
    snap["parity_integrations"] = pis.model_dump(mode="json")
    if not pis.enabled:
        return

    from qchem_stack.integrations.tket_fullchain import describe_tket_closure_layer

    snap["open_stack_contract_schema"] = "parity_open_stack_contract_v1"
    snap["open_stack_design_intent"] = (
        "Engineered open paths where vendor code is closed: keep the same workflow *stages* and "
        "auditable artifacts described in public vendor documentation. Implementations use peer-reviewed "
        "building blocks or explicit user hooks (DMET bath updates, UCC regrouping, TN topology)."
    )
    snap["tket_closure_layer_descriptor"] = describe_tket_closure_layer()

    if pis.qnexus_probe:
        from qchem_stack.integrations.nexus_optional import probe_qnexus_installation

        snap["qnexus_probe"] = probe_qnexus_installation()
    if pis.open_qermit_reference:
        from qchem_stack.integrations.qermit_reference import qermit_capability_matrix

        snap["open_qermit_capability_matrix"] = qermit_capability_matrix()
    if pis.tensornet_closure_reference:
        from qchem_stack.integrations.tensornet_closure import tensornet_closure_strategy

        snap["tensornet_closure_reference"] = tensornet_closure_strategy()
    if pis.uccsd_excitation_reference:
        from qchem_stack.integrations.ucc_reference import count_uccsd_excitations

        n_so = 2 * int(cfg.active_space.n_active_orbitals)
        ne = int(cfg.active_space.n_active_electrons)
        snap["uccsd_reference_closed_shell"] = {
            "n_spin_orbitals": n_so,
            "n_electrons_spin": ne,
            "excitation_counts": count_uccsd_excitations(n_so, ne),
            "module": "qchem_stack.integrations.ucc_reference",
            "caveat": "Spatial active space → spin orbitals assumes closed-shell counting; "
            "open-shell or symmetry blocking needs an explicit user mapping.",
        }

    if cfg.embedding.mode == "dmet":
        snap["dmet_open_loop_architecture"] = {
            "schema": "dmet_open_architecture_v1",
            "self_consistency_loop_class": (
                "qchem_stack.integrations.dmet_self_consistent.DMETSelfConsistencyLoop"
            ),
            "one_shot_driver_class": (
                "qchem_stack.integrations.dmet_self_consistent.OneShotEmbeddingDriver"
            ),
            "fragment_solver_hook": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
            "scf_cycles_yaml": cfg.embedding.n_scf_cycles_embedding,
            "fragment_labels": list(cfg.embedding.fragment_labels),
            "dmet_hamiltonian_source": cfg.embedding.dmet_hamiltonian_source,
            "classical_reference_method": cfg.embedding.classical_reference_method,
            "workflow_note": (
                "Commercial stacks embed bath construction + global correlation updates; "
                "this repository implements the orchestration contract and records stub or "
                "whole_active_system impurity VQE (see EmbeddingSpec.dmet_hamiltonian_source). "
                "Plug bath-aware build_fragment_hamiltonian + DMETSelfConsistencyLoop for full DMET."
            ),
        }

    if cfg.embedding.mode == "projection":
        emb = cfg.embedding
        trace: dict[str, Any] = {
            "schema": "projection_embedding_open_trace_v1",
            "low_level": emb.projection_low_level,
            "high_level": emb.projection_high_level,
            "threshold": float(emb.projection_threshold),
            "projection_quantum_hamiltonian": emb.projection_quantum_hamiltonian,
            "module": "qchem_stack.chem.embedding.projection",
        }
        if emb.projection_quantum_hamiltonian == "fragment_mulliken_mo":
            trace["projection_hamiltonian_source"] = "fragment_mulliken_mo_v1"
            trace["projection_module"] = "qchem_stack.chem.embedding.projection_hamiltonian"
            trace["fermion_qubit_mapping"] = cfg.active_space.fermion_qubit_mapping
            trace["caveat"] = (
                "Variational Hamiltonian is built from RHF MOs, Mulliken-ranked fragment orbitals, "
                f"PySCF CASCI active integrals, and fermion→qubit mapping "
                f"{cfg.active_space.fermion_qubit_mapping!r} (see projection_hamiltonian)."
            )
            trace["epistemic_bound"] = (
                "Not full many-body projection embedding of the environment; not bit-wise parity "
                "with closed vendor PySCF projection drivers."
            )
        else:
            trace["projection_hamiltonian_source"] = "global_active_space"
            trace["fermion_qubit_mapping"] = cfg.active_space.fermion_qubit_mapping
            trace["caveat"] = (
                "Variational stage uses the global ActiveSpaceSpec qubit Hamiltonian "
                f"(mapping {cfg.active_space.fermion_qubit_mapping!r}; same as embedding.mode:none "
                "for the qubit operator). This block records projection workflow metadata only."
            )
            trace["epistemic_bound"] = (
                "Open-stack L1 trace - not numerical parity with proprietary projection stacks."
            )
        snap["projection_embedding_open_trace"] = trace

    if pis.gap_closure_reference_bundle:
        from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference

        snap["open_gap_closure_reference"] = build_open_gap_closure_reference(cfg)


def repro_quantum_snapshot(cfg: ExperimentConfig, qh: QubitHamiltonian | None) -> dict[str, Any]:
    """Falsifiability/parity fields aligned with Methods tables."""
    snap: dict[str, Any] = {
        "quantum_algorithm": cfg.quantum.algorithm,
        **(
            {"quantum_algorithm_factory": cfg.quantum.algorithm_factory}
            if cfg.quantum.algorithm_factory
            else {}
        ),
        "use_pauli_protocol": cfg.quantum.use_pauli_protocol,
        "vqe_depth": cfg.quantum.vqe_depth,
        "vqe_maxiter": cfg.quantum.vqe_maxiter,
        "adapt_max_iter": cfg.quantum.adapt_max_iter,
        "iqeb_max_rounds": cfg.quantum.iqeb_max_rounds,
        "fermion_qubit_mapping": cfg.active_space.fermion_qubit_mapping,
        "variational_ansatz": cfg.quantum.variational_ansatz,
        **(
            {"uccsd_trotter_steps": cfg.quantum.uccsd_trotter_steps}
            if cfg.quantum.variational_ansatz == "uccsd"
            else {}
        ),
        "run_sampled_pauli_protocol": cfg.quantum.run_sampled_pauli_protocol,
        "run_qiskit_shots_pauli_protocol": cfg.quantum.run_qiskit_shots_pauli_protocol,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(cfg.quantum),
        "record_pauli_measurement_histograms": cfg.quantum.record_pauli_measurement_histograms,
        "pauli_grouping": cfg.quantum.pauli_grouping,
        "shots_per_circuit": cfg.backend.shots_per_circuit,
        "target_energy_stderr": cfg.backend.target_energy_stderr,
        "backend_provider": cfg.backend.provider,
        "pmsv_enabled": cfg.mitigation.pmsv_enabled,
        "zne_enabled": cfg.mitigation.zne_enabled,
        "spam_calibration_enabled": cfg.mitigation.spam_calibration_enabled,
        "classical_shadows_stub_enabled": cfg.mitigation.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs": int(cfg.mitigation.classical_shadows_budget_pairs),
        "mitigation_execution_class": cfg.mitigation.execution_class,
        "mitigation_zne_scales": [float(x) for x in cfg.mitigation.zne_scales],
        **({"mitigation_zne_mode": cfg.mitigation.zne_mode} if cfg.mitigation.zne_enabled else {}),
        "compiler_native_twoq": cfg.compiler.native_twoq,
        "compiler_optimization_level": cfg.compiler.optimization_level,
        "compiler_preoptimize_passes": list(cfg.compiler.preoptimize_passes),
        "compiler_passes_yaml": list(cfg.compiler.compiler_passes),
        "compiler_bundle_signature": compiler_bundle_signature_from_config(cfg),
        "pauli_support_max_terms": cfg.quantum.pauli_support_max_terms,
        "vqd_overlap_exponent_yaml": float(cfg.quantum.vqd_overlap_exponent),
        "vqd_cobyla_maxiter_yaml": int(cfg.quantum.vqd_cobyla_maxiter),
        "vqd_after_variational": cfg.quantum.vqd_after_variational,
        "vqd_n_states": cfg.quantum.vqd_n_states,
        "vqd_penalty_weight": cfg.quantum.vqd_penalty_weight,
        "vqd_penalty_weights": cfg.quantum.vqd_penalty_weights,
        "vqd_optimizer_method_yaml": cfg.quantum.vqd_optimizer_method,
        "vqd_init_strategy_yaml": cfg.quantum.vqd_init_strategy,
        "vqd_init_noise_scale_yaml": float(cfg.quantum.vqd_init_noise_scale),
        "vqd_max_overlap_warn_yaml": cfg.quantum.vqd_max_overlap_warn,
        "vqd_overlap_mode_yaml": cfg.quantum.vqd_overlap_mode,
        "vqd_shots_objective": cfg.quantum.vqd_shots_objective,
        "vqd_shots_overlap": cfg.quantum.vqd_shots_overlap,
        "vqd_shots_weight": cfg.quantum.vqd_shots_weight,
        "qse_after_variational": cfg.quantum.qse_after_variational,
        "qse_subspace_dim": cfg.quantum.qse_subspace_dim,
        "qse_max_basis": cfg.quantum.qse_max_basis,
        "qse_shot_mode": cfg.quantum.qse_shot_mode,
        "qse_shots_per_matrix_element": cfg.quantum.qse_shots_per_matrix_element,
        "qse_shots_per_ij_term": cfg.quantum.qse_shots_per_ij_term,
        "sceom_after_variational": cfg.quantum.sceom_after_variational,
        "sceom_subspace_dim": cfg.quantum.sceom_subspace_dim,
        "sceom_shots_per_matrix_element": cfg.quantum.sceom_shots_per_matrix_element,
        "sceom_generator_strategy_yaml": cfg.quantum.sceom_generator_strategy,
        "vqs_track_after_variational": cfg.quantum.vqs_track_after_variational,
        "vqs_pipeline_integration": cfg.quantum.vqs_pipeline_integration,
        "vqs_mode": cfg.quantum.vqs_mode,
        "vqs_n_times": cfg.quantum.vqs_n_times,
        "vqs_dt": float(cfg.quantum.vqs_dt),
        "vqs_rhs_mode_yaml": cfg.quantum.vqs_rhs_mode,
        "vqs_tangent_fd_epsilon_yaml": float(cfg.quantum.vqs_tangent_fd_epsilon),
        "qpe_demo_track_after_variational_yaml": cfg.quantum.qpe_demo_track_after_variational,
        "qpe_pipeline_integration_yaml": cfg.quantum.qpe_pipeline_integration,
        "qpe_demo_track_n_bits_yaml": int(cfg.quantum.qpe_demo_track_n_bits),
        "qpe_three_pack_after_variational_yaml": cfg.quantum.qpe_three_pack_after_variational,
        "qpe_three_pack_time_yaml": float(cfg.quantum.qpe_three_pack_time),
    }
    if qh is not None and qh.meta:
        snap["hamiltonian_meta"] = dict(qh.meta)
    emb = cfg.embedding
    snap["embedding_mode"] = emb.mode
    if emb.n_scf_cycles_embedding is not None:
        snap["n_scf_cycles_embedding"] = emb.n_scf_cycles_embedding
    if emb.classical_reference_method:
        snap["classical_reference_method"] = emb.classical_reference_method
    if emb.fragment_labels:
        snap["embedding_fragment_labels"] = list(emb.fragment_labels)
    if emb.dmet_hamiltonian_source == "schmidt_atomic_production":
        snap["schmidt_dmet_max_cycles"] = int(emb.schmidt_dmet_max_cycles)
        snap["schmidt_dmet_mixing_alpha"] = float(emb.schmidt_dmet_mixing_alpha)
        if emb.schmidt_multi_fragment_atom_groups:
            snap["schmidt_multifragment"] = True
            snap["schmidt_multifragment_n"] = len(emb.schmidt_multi_fragment_atom_groups)
    snap["chemistry_extended"] = cfg.chemistry_extended.model_dump(mode="json")
    snap["nexus_analog"] = cfg.nexus_analog.model_dump(mode="json")
    snap["nexus_cloud"] = cfg.nexus_cloud.model_dump(mode="json")
    snap["tensornet_expectation_stub"] = bool(cfg.quantum.tensornet_expectation_stub)
    snap["tensornet_contraction_engine"] = cfg.quantum.tensornet_contraction_engine
    append_open_stack_parity_fields(snap, cfg)
    return snap
