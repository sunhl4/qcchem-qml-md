"""
Internal competitive-alignment helpers and legacy key registries.

Integrators and docs should import the stable re-export
``qchem_stack.protocols.inquanto_contract`` (same symbols as this module).
Release-facing *product* defaults may also use ``qchem_stack.protocols.product_contract``.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig, QuantumSpec

# Stable JSON tokens for `repro.parity_snapshot.pauli_protocol_expectation_path` / export scripts.
PAULI_PATH_DISABLED = "pauli_protocol_disabled"
PAULI_PATH_EXACT = "exact_executor"
PAULI_PATH_STATEVECTOR_SHOT_SIM = "statevector_grouped_shot_simulation"
PAULI_PATH_QISKIT_COUNTS = "qiskit_get_counts_bitstrings"

# InQuanto (public API / docs) → qchem_stack (open). Values are import paths or module file stems.
INQUANTO_TO_QCHEM_OBJECT_MAP: dict[str, str] = {
    "Protocol (five stages)": "qchem_stack.protocols.protocol.PauliAveragingProtocol + ProtocolPhase",
    "AlgorithmVQE": "qchem_stack.quantum.algorithms.vqe.VQE",
    "AlgorithmAdaptVQE": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
    "Operator pool registry (ADAPT/IQEB)": (
        "qchem_stack.quantum.operator_pool_registry (quantum.adapt_pool_id / quantum.iqeb_pool_id; "
        "pool_id_aliases; operator_pool_registry_export_v1 under algorithm_registry_alignment_v1 when "
        "resource_estimation_preview; same schema on GET /v1/meta/capability-surface)"
    ),
    "YAML quantum.algorithm_factory (variational plugins)": (
        "qchem_stack.quantum.variational_plugins (spec, loader, registry); "
        "examples/echo_runner.py; configs/example_h2_echo_variational_plugin.yaml"
    ),
    "AlgorithmIQEB": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE (outer-loop Pauli correction + VQE; set quantum.algorithm=iqeb; configs/example_h2_iqeb.yaml)",
    "AlgorithmVQD": (
        "qchem_stack.quantum.algorithms.excited.VQD "
        "(HEA: configs/example_h2_excited_smoke.yaml; UCCSD deflation: configs/example_h2_vqd_uccsd.yaml)"
    ),
    "AlgorithmQSE": "qchem_stack.quantum.algorithms.excited.QSE + quantum.qse_transition (Pauli transition shot modes)",
    "AlgorithmSCEOM": "qchem_stack.quantum.algorithms.sceom.run_sceom_nested_commutator_from_hea",
    "Algorithm*QPE (track)": (
        "qchem_stack.qpe_qec_demo.pipeline_track + pipeline._attach_qpe_demo_track_if_requested "
        "(qpe_demo_track_after_variational | qpe_pipeline_integration); "
        "run_summary.qpe_open_stack_contract_v1 points at quantum/algorithms/qpe.AlgorithmKitaevQPE / Deterministic / InfoTheory"
    ),
    "AlgorithmVQS / AlgorithmMcLachlan*": (
        "qchem_stack.quantum.algorithms.vqs (AlgorithmVQS, AlgorithmMcLachlanRealTime, AlgorithmMcLachlanImagTime) + "
        "vqs_pipeline_track.vqs_track_payload; optional main-line YAML quantum.vqs_track_after_variational | "
        "vqs_pipeline_integration → pipeline attaches vqs_track + run_summary.vqs_open_stack_contract_v1"
    ),
    "AlgorithmBayesianQPE + Phayes": "qchem_stack.qpe_qec_demo.BayesianQPEStub",
    "Qubit Hamiltonian (JW)": (
        "qchem_stack.chem.hamiltonian.QubitHamiltonian + molecular_hamiltonian_from_classical_reference / "
        "qubit_hamiltonian_from_spatial_chemist_integrals (JW or Bravyi–Kitaev via "
        "active_space.fermion_qubit_mapping)"
    ),
    "Fermion→qubit names (Tangelo / tutorial aliases)": (
        "qchem_stack.chem.fermion_mapping_registry.tangelo_public_mapping_alias_surface_v1() "
        "(GET /v1/meta/capability-surface); YAML literals in DOCUMENTED_FERMION_QUBIT_MAPPINGS "
        "only — JKMN/HCB not executable in open stack until separately wired"
    ),
    "IntegralSolver (Tangelo toolbox shape)": (
        "qchem_stack.chem.solvers.base.ChemIntegralSolver "
        "(set_physical_data, compute_mean_field, get_integrals hook; "
        "PySCF get_integrals returns CASCI active-space MO blocks + OpenFermion reorder)"
    ),
    "dataframe_circuit / shot rows": "qchem_stack.backends.spec.circuit_resource_row, dataframe_circuit_shot_rows",
    "Computable (expectation from circuits)": (
        "qchem_stack.protocols.computable + "
        "qchem_stack.integrations.inquanto_workflow_preview.computable_graph_v2 + POST /v1/meta/workflow-preview"
    ),
    "TKET / pytket pass metrics": "optional: qchem_stack.integrations.tket_fullchain + backends.pytket_bridge (parity_integrations.tket_first_circuit_stats)",
    "qnexus / Nexus jobs": "qchem_stack.jobs: SqliteJobStore + nexus_analog_ledger + nexus_cloud (optional HTTP/mock), job nexus_analog_billing",
    "DMET fragment solver (stub)": "qchem_stack.chem.embedding.dmet.VQEFragmentSolverStub",
    "DMET self-consistency (density feedback)": "integrations/schmidt_dmet_self_consistent.run_schmidt_density_feedback_cycles + DMETSelfConsistencyLoop.run_with_hooks",
    "DMET Schmidt optional per-fragment VQE": "orchestration/pipeline._run_schmidt_per_fragment_vqe (EmbeddingSpec.schmidt_run_vqe_on_all_fragments)",
    "Noise mitigation (Qermit-style)": "qermit_analog (DAG) + qermit_runtime (linear trace) + mitigation/ (PMSV/ZNE/SPAM stubs)",
    "Device counts → expectation (Qiskit path)": "QuantumSpec.run_qiskit_shots_pauli_protocol + protocol Pauli evaluate path (see pauli_contract)",
    "Classical chemistry surface (COSMO / PBC names)": "chem.inquanto_driver_surface.INQUANTO_DRIVER_ALIAS_TO_CONFIG + PySCF drivers",
    "Molecule geometry (Cartesian vs Z-matrix)": (
        "config.MoleculeSpec (coordinates XOR zmatrix); "
        "chem.bridges.facade.molecular_system_from_experiment → MolecularSystem.meta['geometry_source'] "
        "(cartesian|zmatrix); parity export key geometry_source (config-only)"
    ),
    "CuTensorNet-protocol stub": "tensornet.cutensornet_protocol_stub.run_cutensornet_expectation_stub",
}


def mitigation_execution_model_public() -> dict[str, Any]:
    """
    Structured boundary vs public MitRes/MitEx docs (L1). Surfaced on ``GET /v1/meta/capability-surface``
    and embedded under the ``qermit_graph`` gap row for dashboards.
    """
    return {
        "schema": "mitigation_execution_model_v1",
        "sync_dag": {
            "open_stack": "mitigation/qermit_analog.py JSON graph + optional mitigation_dag_execution trace on pipeline result",
            "public_doc_anchor": "MitRes-style graphs (Quantinuum errmit manual — URL below)",
        },
        "async_batch_execution": {
            "open_stack": "not_implemented_mitex_batch_scheduler",
            "note": "Local SQLite jobs run whole experiments; not a Qermit MitEx multi-task batch runtime.",
        },
        "public_doc_urls": ["https://docs.quantinuum.com/inquanto/manual/errmit.html"],
        "epistemic_bound": "Open analog only — not the closed Qermit wheel or vendor execution engine.",
    }


def open_stack_differentiators_public() -> dict[str, Any]:
    """
    Where the **open** stack intentionally **exceeds** *public-documentation* parity
    in **auditability and extensibility** — **excluding** commercial cloud (Nexus/HQC)
    and proprietary hardware specialization.

    Surfaced on ``GET /v1/meta/capability-surface``. Not L0 binary parity with closed wheels.
    """
    return {
        "schema": "open_stack_differentiators_v1",
        "scope_excludes": [
            "commercial_Nexus_qnexus_HQC_SLAs",
            "vendor_native_hardware_calibration_topology_lock_in",
        ],
        "beyond_public_doc_bundle": [
            {
                "id": "full_stack_opensource_methods",
                "summary": "Orchestration + protocol + chem drivers + jobs are auditable without closed InQuanto wheels.",
                "evidence_modules": ["qchem_stack/"],
            },
            {
                "id": "parity_export_and_ci_gates",
                "summary": "Frozen export keys + multi-config sample script + pytest registry for parity_snapshot.",
                "evidence_modules": [
                    "scripts/export_parity_criteria_table.py",
                    "scripts/check_parity_export_sample.py",
                    "protocols/inquanto_contract.py",
                    "tests/test_repro_top_level_key_registry.py",
                ],
            },
            {
                "id": "strict_repro_run_summary",
                "summary": "Single JSON blob: repro.parity_snapshot + run_summary stage semantics for papers.",
                "evidence_modules": ["orchestration/pipeline.py", "repro/"],
            },
            {
                "id": "multi_backend_no_single_vendor_gate",
                "summary": "adapter-first chemistry plus statevector / qiskit / ionstack mock executors under one YAML.",
                "evidence_modules": ["backends/"],
            },
            {
                "id": "md_ml_dataset_lane",
                "summary": "QMEFDataset + md_bridge export hooks vs chemistry-only product cores.",
                "evidence_modules": ["md_bridge/"],
            },
            {
                "id": "iqeb_and_projection_l1_wiring",
                "summary": "Non-default IQEB pipeline + projection embedding L1 trace YAMLs (honest caveats).",
                "evidence_modules": [
                    "quantum/algorithms/iqeb.py",
                    "orchestration/pipeline.py",
                    "configs/example_h2_iqeb.yaml",
                    "configs/example_h2_projection_trace.yaml",
                ],
            },
            {
                "id": "operator_pool_and_variational_plugin_registry_exports",
                "summary": (
                    "ADAPT/IQEB operator pools (+ YAML aliases) on GET /v1/meta/capability-surface "
                    "(operator_pool_registry_export_v1) and under algorithm_registry_alignment_v1 when "
                    "parity_integrations.resource_estimation_preview is on variational/registry exports."
                ),
                "evidence_modules": [
                    "quantum/operator_pool_registry.py",
                    "api/app.py",
                    "quantum/variational_plugins/registry.py",
                    "scripts/export_parity_criteria_table.py",
                    "integrations/l3_algorithm_benchmark.py",
                ],
            },
            {
                "id": "mitigation_dag_trace_l1",
                "summary": "Qermit-analog DAG node kinds match linear mitigation execution trace order (audit invariant).",
                "evidence_modules": [
                    "mitigation/qermit_analog.py",
                    "mitigation/qermit_runtime.py",
                    "tests/test_mitigation_dag_trace_homology.py",
                ],
            },
            {
                "id": "molecular_geometry_lineage_l1",
                "summary": (
                    "Explicit geometry_source (cartesian vs zmatrix) on MolecularSystem.meta from YAML and on "
                    "parity export (Methods / competitor tables); aligns problem-construction transparency vs "
                    "public InQuanto PySCF narratives without claiming closed-wheel parity."
                ),
                "evidence_modules": [
                    "chem/bridges/facade.py",
                    "chem/system.py",
                    "config.py",
                    "scripts/export_parity_criteria_table.py",
                    "tests/test_classical_bridge_interchange.py",
                    "configs/example_h2_zmatrix_sto3g.yaml",
                ],
            },
            {
                "id": "tangelo_fermion_mapping_alias_surface",
                "summary": (
                    "Static JW/BK/SCBK ↔ tutorial nickname table vs Tangelo/OpenFermion wording; JKMN/HCB "
                    "disclosed as not executable until OpenFermion parity work lands."
                ),
                "evidence_modules": [
                    "chem/fermion_mapping_registry.py",
                    "api/app.py",
                ],
            },
        ],
        "epistemic_bound": (
            "Beyond means transparency and optional open extras — not numerical equivalence to closed "
            "vendor binaries or internal heuristics."
        ),
    }


# Registry for CI: every key emitted by ``_repro_quantum_snapshot`` / ``_append_open_stack_parity_fields`` /
# ``_finalize_open_stack_parity_snapshot`` must appear here (update when adding snapshot fields).
PARITY_SNAPSHOT_DOCUMENTED_KEYS: frozenset[str] = frozenset(
    {
        "quantum_algorithm",
        "use_pauli_protocol",
        "vqe_depth",
        "vqe_maxiter",
        "adapt_max_iter",
        "iqeb_max_rounds",
        "fermion_qubit_mapping",
        "variational_ansatz",
        "uccsd_n_parameters",
        "uccsd_trotter_steps",
        "zne_qiskit_unification_v1",
        "projection_embedding_open_trace",
        "run_sampled_pauli_protocol",
        "run_qiskit_shots_pauli_protocol",
        "pauli_protocol_expectation_path",
        "record_pauli_measurement_histograms",
        "pauli_grouping",
        "shots_per_circuit",
        "target_energy_stderr",
        "backend_provider",
        "pmsv_enabled",
        "zne_enabled",
        "spam_calibration_enabled",
        "classical_shadows_stub_enabled",
        "classical_shadows_budget_pairs",
        "mitigation_execution_class",
        "mitigation_zne_scales",
        "mitigation_zne_mode",
        "compiler_native_twoq",
        "compiler_optimization_level",
        "compiler_preoptimize_passes",
        "compiler_passes_yaml",
        "compiler_bundle_signature",
        "pauli_support_max_terms",
        "vqd_after_variational",
        "vqd_n_states",
        "vqd_penalty_weight",
        "vqd_penalty_weights",
        "vqd_optimizer_method_yaml",
        "vqd_init_strategy_yaml",
        "vqd_init_noise_scale_yaml",
        "vqd_max_overlap_warn_yaml",
        "vqd_overlap_mode_yaml",
        "vqd_shots_objective",
        "vqd_shots_overlap",
        "vqd_shots_weight",
        "vqd_overlap_exponent_yaml",
        "vqd_cobyla_maxiter_yaml",
        "qse_after_variational",
        "qse_subspace_dim",
        "qse_max_basis",
        "qse_shot_mode",
        "qse_shots_per_matrix_element",
        "qse_shots_per_ij_term",
        "sceom_after_variational",
        "sceom_subspace_dim",
        "sceom_shots_per_matrix_element",
        "sceom_generator_strategy_yaml",
        "vqs_track_after_variational",
        "vqs_pipeline_integration",
        "vqs_mode",
        "vqs_n_times",
        "vqs_dt",
        "vqs_rhs_mode_yaml",
        "vqs_tangent_fd_epsilon_yaml",
        "qpe_demo_track_after_variational_yaml",
        "qpe_demo_track_n_bits_yaml",
        "qpe_pipeline_integration_yaml",
        "qpe_three_pack_after_variational_yaml",
        "qpe_three_pack_time_yaml",
        "hamiltonian_meta",
        "embedding_mode",
        "n_scf_cycles_embedding",
        "classical_reference_method",
        "embedding_fragment_labels",
        "schmidt_dmet_max_cycles",
        "schmidt_dmet_mixing_alpha",
        "schmidt_multifragment",
        "schmidt_multifragment_n",
        "chemistry_extended",
        "nexus_analog",
        "nexus_cloud",
        "tensornet_expectation_stub",
        "tensornet_contraction_engine",
        "parity_integrations",
        "open_stack_contract_schema",
        "open_stack_design_intent",
        "tket_closure_layer_descriptor",
        "qnexus_probe",
        "open_qermit_capability_matrix",
        "tensornet_closure_reference",
        "uccsd_reference_closed_shell",
        "dmet_open_loop_architecture",
        "open_gap_closure_reference",
        "tket_first_compiled_circuit_probe",
        "dmet_one_shot_open_ledger",
        "dmet_solver_mode",
        "schmidt_embedding_production",
        "dmet_fragment_solve_error",
        "schmidt_per_fragment_vqe_summary",
        "dmet_uniform_multifragment_toy",
        "tensornet_engine_resolved",
        "tensornet_fallback_reason",
    }
)


# Top-level export JSON keys guaranteed by ``scripts/export_parity_criteria_table.py`` (config-only).
PARITY_EXPORT_V2_STABLE_KEYS: frozenset[str] = frozenset(
    {
        "parity_export_schema_version",
        "experiment_id",
        "computable_abstract",
        "excited_resource_from_config",
        "inquanto_gap_categories",
        "iqeb_implementation_path",
        "pauli_protocol_expectation_path",
        "protocol_expectation_semantics_v1",
        "geometry_source",
        "embedding",
    }
)


# Registry for CI: every key written by ``orchestration.pipeline._attach_run_summary`` must appear here
# (update when adding run_summary fields).
RUN_SUMMARY_DOCUMENTED_KEYS: frozenset[str] = frozenset(
    {
        "stages_completed",
        "quantum_algorithm",
        "quantum_algorithm_yaml",
        "quantum_algorithm_factory_yaml",
        "classical_backend_id",
        "classical_benchmark_backend_yaml",
        "variational_ansatz_yaml",
        "uccsd_n_parameters",
        "pauli_protocol_expectation_path",
        "energy_after_variational",
        "mitigation_zne_mode_yaml",
        "mitigation_zne_scales_yaml",
        "spam_calibration_enabled_yaml",
        "classical_shadows_stub_enabled_yaml",
        "classical_shadows_budget_pairs_yaml",
        "embedding_input_representation_yaml",
        "embedding_input_system_schema",
        "energy_components_present",
        "energy_components_schema",
        "energy_components_mean_field_total_au",
        "energy_components_nuclear_repulsion_au",
        "dmet_embedding_active",
        "dmet_hamiltonian_source_yaml",
        "dmet_fragment_count",
        "dmet_uniform_multifragment_toy_yaml",
        "dmet_stub_one_shot_ledger_yaml",
        "decomposition_plugin_yaml",
        "decomposition_primary_fragment_id",
        "decomposition_fragment_count",
        "decomposition_total_pauli_terms",
        "dmet_fragment_solve_present",
        "dmet_fragment_solve_schema",
        "schmidt_dmet_max_cycles_yaml",
        "schmidt_dmet_cycles_executed",
        "schmidt_dmet_converged_early",
        "schmidt_per_fragment_vqe_n_fragments",
        "schmidt_per_fragment_vqe_total_nfev",
        "schmidt_per_fragment_vqe_min_energy_au",
        "schmidt_per_fragment_vqe_max_energy_au",
        "scf_energy",
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
        "rdm_correction_present",
        "rdm_correction_schema",
        "rdm_correction_method",
        "rdm_correction_status",
        "rdm_correction_energy_au",
        "rdm_correction_readiness_present",
        "rdm_correction_readiness_schema",
        "rdm_correction_readiness_requested_method",
        "rdm_correction_readiness_rdm1_source",
        "rdm_correction_readiness_rdm_basis",
        "rdm_correction_readiness_spin_model",
        "rdm_correction_readiness_reference_wavefunction",
        "rdm_correction_readiness_kernel_class",
        "rdm_correction_readiness_nevpt2_pyscf_status",
        "vqe_maxiter_yaml",
        "vqe_nfev",
        "adapt_max_iter_yaml",
        "adapt_total_gradient_evals",
        "adapt_steps_recorded",
        "adapt_excitation_layers",
        "adapt_pool_id_yaml",
        "iqeb_max_rounds_yaml",
        "iqeb_outer_rounds_recorded",
        "iqeb_selected_pauli_count",
        "iqeb_final_inner_vqe_nfev",
        "iqeb_implementation_path",
        "iqeb_pool_id_yaml",
        "sum_shots_total_with_excited_upper_bound",
        "excited_shots_upper_bound",
        "pauli_averaging_protocol_ran",
        "sum_shots_backend_protocol",
        "n_pauli_terms",
        "n_pauli_groups",
        "n_circuits",
        "n_qubits",
        "energy_pauli_protocol",
        "protocol_expectation_source",
        "protocol_zne_mode",
        "protocol_energy_stderr_model",
        "protocol_total_shots_budget",
        "protocol_n_measurement_circuits",
        "protocol_shots_per_circuit_effective",
        "protocol_energy_stderr",
        "protocol_pmsv_report",
        "vqd_n_states_yaml",
        "vqd_overlap_exponent_yaml",
        "vqd_cobyla_maxiter_yaml",
        "vqd_n_energies_recorded",
        "vqd_deflation_levels_completed",
        "vqd_reused_pipeline_ground",
        "vqd_three_protocol_present",
        "vqd_channels_count",
        "vqd_shots_objective_yaml",
        "vqd_shots_overlap_yaml",
        "vqd_shots_weight_yaml",
        "vqd_optimizer_method_yaml",
        "vqd_init_strategy_yaml",
        "vqd_overlap_mode_yaml",
        "vqd_warnings_present",
        "vqd_variety_yaml",
        "qse_shot_mode",
        "qse_subspace_dim_yaml",
        "qse_max_basis_yaml",
        "qse_n_excitation_energies",
        "qse_shot_noise_model",
        "qse_basis_dimension_K",
        "qse_n_transition_tasks",
        "qse_total_shots_upper_bound",
        "sceom_shots_per_matrix_element",
        "sceom_subspace_dim_yaml",
        "sceom_generator_strategy_yaml",
        "sceom_n_energies_recorded",
        "sceom_shot_noise_model",
        "sceom_active_generator_count",
        "sceom_matrix_construction",
        "async_job_id",
        "protocol_hash_prefix",
        "job_async_expectation",
        "job_async_energy_stderr",
        "job_async_total_shots_budget",
        "qpe_demo_track_ran",
        "qpe_open_stack_contract_v1",
        "qpe_three_pack_ran",
        "qpe_three_pack_deterministic_energy_est",
        "qpe_three_pack_kitaev_energy_est",
        "qpe_three_pack_info_theory_energy_est",
        "vqs_track_ran",
        "vqs_open_stack_contract_v1",
        "nexus_analog_hqc_units",
        "mitigation_graph_report_present",
        "mitigation_dag_execution_present",
        "nexus_cloud_repro",
        "qnexus_client_probe_available",
        "tket_first_circuit_stats_ok",
        "dmet_one_shot_open_ledger_present",
        "dmet_fragment_solve_energy",
        "dmet_solver_mode",
        "open_gap_closure_reference_present",
        "dmet_uniform_multifragment_toy_present",
        "schmidt_per_fragment_vqe_in_parity_snapshot",
        "pipeline_total_wall_ms",
        "pipeline_slowest_stage",
        "pipeline_slowest_stage_ms",
        "trace_id",
        "client_request_id",
    }
)


# Keys allowed on ``repro`` root after ``collect_repro_metadata`` + pipeline finalization (P1 audit).
REPRO_DOCUMENTED_KEYS: frozenset[str] = frozenset(
    {
        "experiment_id",
        "random_seed",
        "config_sha256_prefix",
        "config_path",
        "python",
        "packages",
        "classical_software_versions",
        "pyscf_version",
        "embedding_config",
        "chemistry_extended_config",
        "nexus_analog_config",
        "nexus_cloud_config",
        "parity_snapshot",
        "workflow_preview_v1",
        "workflow_preview_variational_execution_v1",
        "workflow_preview_qpe_track_v1",
        "workflow_preview_vqs_track_v1",
        "run_context",
        "run_summary",
        "pipeline_profile",
        "embedding_workflow",
        "qmef_ml_attachment_v1",
    }
)


# Keys emitted by ``integrations.resource_estimation_preview.build_resource_estimation_preview_v1``.
RESOURCE_ESTIMATION_PREVIEW_V1_DOCUMENTED_KEYS: frozenset[str] = frozenset(
    {
        "schema",
        "mode",
        "epistemic_bound",
        "quantum_algorithm_yaml",
        "algorithm_factory_yaml",
        "adapt_pool_id_yaml",
        "iqeb_pool_id_yaml",
        "variational_ansatz_yaml",
        "fermion_qubit_mapping_yaml",
        "backend_provider_yaml",
        "zne_enabled_yaml",
        "mitigation_zne_mode_yaml",
        "mitigation_zne_scales_yaml",
        "pmsv_enabled_yaml",
        "run_sampled_pauli_protocol_yaml",
        "run_qiskit_shots_pauli_protocol_yaml",
        "pauli_protocol_expectation_path_yaml",
        "qpe_demo_track_after_variational",
        "qpe_pipeline_integration",
        "qpe_demo_track_n_bits",
        "qpe_three_pack_after_variational",
        "qpe_three_pack_time_yaml",
        "qpe_three_pack_deterministic_rounds_yaml",
        "qpe_three_pack_kitaev_bits_yaml",
        "qpe_three_pack_info_samples_yaml",
        "vqs_track_after_variational",
        "vqs_pipeline_integration",
        "vqs_mode_yaml",
        "vqs_n_times_yaml",
        "vqs_dt_yaml",
        "vqs_rhs_mode_yaml",
        "vqs_tangent_fd_epsilon_yaml_preview",
        "vqd_overlap_exponent_yaml",
        "vqd_cobyla_maxiter_yaml",
        "vqd_overlap_mode_yaml",
        "vqd_optimizer_method_yaml",
        "vqd_init_strategy_yaml",
        "vqd_init_noise_scale_yaml",
        "vqd_max_overlap_warn_yaml",
        "sceom_generator_strategy_yaml",
        "parity_integrations_tket_first_circuit_stats",
        "use_pauli_protocol",
        "spam_calibration_enabled_yaml",
        "classical_shadows_stub_enabled_yaml",
        "classical_shadows_budget_pairs_yaml",
        "classical_benchmark_enabled_yaml",
        "classical_benchmark_active",
        "classical_benchmark_summary_schema",
        "classical_benchmark_recommended_baseline_policy",
        "classical_benchmark_recommended_baseline_method",
        "classical_benchmark_recommended_baseline_energy_au",
        "classical_benchmark_best_method",
        "classical_benchmark_best_energy_au",
        "resource_summary_n_circuits",
        "resource_summary_n_qubits",
        "resource_summary_sum_shots",
        "resource_summary_max_depth",
        "resource_summary_sum_twoq",
        "resource_summary_n_pauli_terms",
        "resource_summary_n_pauli_groups",
        "resource_summary_pauli_averaging_protocol_ran",
        "resource_summary_excited_shots_upper_bound",
        "resource_summary_sum_shots_total_with_excited_upper_bound",
        "run_summary_protocol_total_shots_budget",
        "run_summary_protocol_n_measurement_circuits",
        "run_summary_protocol_shots_per_circuit_effective",
        "run_summary_protocol_energy_stderr",
        "run_summary_protocol_expectation_source",
        "run_summary_protocol_energy_stderr_model",
        "run_summary_protocol_zne_mode",
        "run_summary_excited_shots_upper_bound",
        "run_summary_sum_shots_total_with_excited_upper_bound",
        "run_summary_pauli_averaging_protocol_ran",
        "run_summary_qpe_three_pack_ran",
        "qpe_three_pack_deterministic_energy_est_from_run",
        "qpe_three_pack_kitaev_energy_est_from_run",
        "qpe_three_pack_info_theory_energy_est_from_run",
        "parity_snapshot_mitigation_zne_scales",
        "parity_snapshot_mitigation_zne_mode",
    }
)


# Top-level keys on ``integrations.methods_resource_unified.build_methods_resource_unified_v1`` output.
METHODS_RESOURCE_UNIFIED_V1_DOCUMENTED_KEYS: frozenset[str] = frozenset(
    {
        "schema",
        "classical_backend_id",
        "classical_benchmark_backend_yaml",
        "quantum_algorithm_yaml",
        "quantum_algorithm_factory_yaml",
        "resource_summary",
        "qpe_demo_track",
        "run_summary_qpe_demo_track_ran",
        "run_summary_qpe_three_pack_ran",
        "qpe_three_pack_deterministic_energy_est",
        "qpe_three_pack_kitaev_energy_est",
        "qpe_three_pack_info_theory_energy_est",
        "qpe_open_stack_contract_v1",
        "run_summary_vqs_track_ran",
        "vqs_open_stack_contract_v1",
        "excited_protocol_contract_v1_present",
        "tket_first_compiled_circuit_probe_schema",
        "classical_benchmark_active",
        "classical_benchmark_summary_schema",
        "classical_benchmark_recommended_baseline_policy",
        "classical_benchmark_recommended_baseline_method",
        "classical_benchmark_recommended_baseline_energy_au",
        "classical_benchmark_best_method",
        "classical_benchmark_best_energy_au",
        "mitigation_zne_mode_yaml",
        "mitigation_zne_scales_yaml",
        "run_summary_protocol_total_shots_budget",
        "run_summary_protocol_n_measurement_circuits",
        "run_summary_protocol_shots_per_circuit_effective",
        "run_summary_protocol_energy_stderr",
        "run_summary_protocol_expectation_source",
        "run_summary_protocol_energy_stderr_model",
        "run_summary_protocol_zne_mode",
        "run_summary_excited_shots_upper_bound",
        "run_summary_sum_shots_total_with_excited_upper_bound",
        "run_summary_pauli_averaging_protocol_ran",
    }
)


def classify_pauli_expectation_path(q: QuantumSpec) -> str:
    """
    How ``energy_pauli_protocol`` is produced when the Pauli averaging stage is **enabled in YAML**.

    This classifies *intent* from config; the run may still omit ``energy_pauli_protocol`` if
    the pipeline is cut short, but the snapshot is for Methods reproducibility.
    """
    if not q.use_pauli_protocol:
        return PAULI_PATH_DISABLED
    if q.run_sampled_pauli_protocol and q.run_qiskit_shots_pauli_protocol:
        raise ValueError(
            "run_sampled_pauli_protocol and run_qiskit_shots_pauli_protocol are mutually exclusive"
        )
    if q.run_sampled_pauli_protocol:
        return PAULI_PATH_STATEVECTOR_SHOT_SIM
    if q.run_qiskit_shots_pauli_protocol:
        return PAULI_PATH_QISKIT_COUNTS
    return PAULI_PATH_EXACT


def pauli_protocol_expectation_path_for_config(cfg: ExperimentConfig) -> str:
    """Convenience: classify from a full :class:`ExperimentConfig`."""
    return classify_pauli_expectation_path(cfg.quantum)


def protocol_expectation_semantics_public() -> dict[str, Any]:
    """
    P0 / Methods: stable mapping from YAML intent to ``pauli_protocol_expectation_path`` tokens and
    typical ``protocol_counts`` keys (see ``PauliAveragingProtocol`` run/evaluate branches).

    Narrative doc: ``docs/技术文档_设备比特串与Qiskit采样路径.md`` §2.
    """
    return {
        "schema": "protocol_expectation_semantics_v1",
        "doc_anchor": "docs/技术文档_设备比特串与Qiskit采样路径.md (section 2)",
        "yaml_mutual_exclusion": (
            "QuantumSpec.run_sampled_pauli_protocol XOR run_qiskit_shots_pauli_protocol "
            "(validated in QuantumSpec model_validator)"
        ),
        "paths": [
            {
                "order": 1,
                "label": "default_exact_executor",
                "when": {
                    "use_pauli_protocol": True,
                    "run_sampled_pauli_protocol": False,
                    "run_qiskit_shots_pauli_protocol": False,
                },
                "pauli_protocol_expectation_path": PAULI_PATH_EXACT,
                "protocol_counts_expectation_source": "executor_exact_or_device_mean",
                "protocol_counts_energy_stderr_model": "conservative_sum_bound_equal_shots",
            },
            {
                "order": 2,
                "label": "statevector_grouped_shot_simulation",
                "when": {"use_pauli_protocol": True, "run_sampled_pauli_protocol": True},
                "pauli_protocol_expectation_path": PAULI_PATH_STATEVECTOR_SHOT_SIM,
                "protocol_counts_expectation_source": "grouped_shot_simulation_statevector",
                "protocol_counts_energy_stderr_model": "sample_stderr_independent_groups_approx",
            },
            {
                "order": 3,
                "label": "qiskit_get_counts_histogram",
                "when": {"use_pauli_protocol": True, "run_qiskit_shots_pauli_protocol": True},
                "pauli_protocol_expectation_path": PAULI_PATH_QISKIT_COUNTS,
                "protocol_counts_expectation_source": "qiskit_shot_counts_get_counts",
                "protocol_counts_energy_stderr_model": "empirical_shot_variance_independent_groups_approx",
            },
        ],
    }


def inquanto_object_map_for_docs() -> dict[str, str]:
    """Read-only copy of the public name → implementation map (for export / tests)."""
    return dict(INQUANTO_TO_QCHEM_OBJECT_MAP)


def inquanto_gap_categories() -> list[dict[str, Any]]:
    """
    Machine-readable gap list (high level). Mirrors ``docs/与InQuanto能力差距与实施计划.md`` §1.

    For dashboards / regression tooling only — not a substitute for the narrative doc.
    """
    return [
        {
            "id": "cloud_nexus",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — qnexus/HQC (non-cloud L1 parity: analog only)",
            "inquanto_surface": "Nexus / qnexus / HQC (cloud + local ledger)",
            "qchem_stack": "jobs/nexus_analog + jobs/nexus_cloud + integrations/nexus_optional (import probe)",
            "status": "analog_v1_plus_adapter",
        },
        {
            "id": "http_submit_poll_workspace",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — 作业提交/列表/轮询",
            "inquanto_surface": "HTTPS job submit, list, poll status (Nexus-shaped product UX)",
            "qchem_stack": "qchem_stack.api FastAPI: capability-surface, POST/GET /v1/runs (project_slug + workspace), GET /v1/runs/{id}/summary, GET /v1/runs/{id}/events (timeline_json), GET /v1/meta/product-analog, POST /v1/meta/workflow-preview, GET /v1/meta/parity-gaps, POST /v1/meta/computables-preview, GET /v1/meta/queue-stats, SQLite JobStore.list_jobs",
            "status": "local_analog_v1",
        },
        {
            "id": "qermit_graph",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — Qermit; see mitigation_execution_model",
            "inquanto_surface": "Qermit MitRes / MitEx graphs and execution",
            "qchem_stack": (
                "qermit_analog + qermit_runtime + integrations/qermit_reference (capability matrix); "
                "MitigationSpec.zne_mode=circuit_scale_fold wires Pauli protocol zne_curve into mitigation_dag_execution"
            ),
            "status": "analog_v2_runtime",
            "dag_trace_order_invariant": (
                "L1: ``mitigation_graph_report.nodes`` (excluding in/out shells) kinds sequence equals "
                "``mitigation_dag_execution.trace[].node`` order — ``tests/test_mitigation_dag_trace_homology.py``"
            ),
            "mitigation_execution_model": mitigation_execution_model_public(),
        },
        {
            "id": "composable_computable",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — Computable / workflow-preview",
            "inquanto_surface": "Computable graph",
            "qchem_stack": "list_computables_for_config + computable_graph_v2 (semantic DAG + YAML computable_extra_edges/remove_edges) + POST /v1/meta/workflow-preview + optional computables_rich_v1 (include_computables_rich); PauliAveragingProtocol at run time",
            "status": "analog_v2_semantic_graph_rich_optional",
        },
        {
            "id": "evaluate_support_set",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — resource / Pauli support",
            "inquanto_surface": "evaluate_expectation_value / measurement-plan support reuse (public docs)",
            "qchem_stack": "protocol_counts hamiltonian_pauli_strings + protocols.pauli_support.assert_evaluate_compatible",
            "status": "improved_v1",
        },
        {
            "id": "compiler_pass_bundle",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §4 — TKET; gap id compiler_pass_bundle",
            "inquanto_surface": "preoptimize_passes / compiler_passes / optimization_level (protocol compile stage)",
            "qchem_stack": "CompilerSpec + compiler_bundle_signature_from_config + CircuitIR passes + integrations/tket_fullchain (pytket stats)",
            "status": "improved_v1",
        },
        {
            "id": "ucc_chem_ansatz",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §2 — ADAPT / IQEB / UCC",
            "inquanto_surface": "UCC / chemically aware pools",
            "qchem_stack": (
                "HEA + ADAPT + IQEB + ``quantum.variational_ansatz=uccsd`` dense cluster ansatz "
                "(UCCSDVQE / UCCSDTrotterVQE — **Jordan–Wigner** with JW particle-sector projector, "
                "or **Bravyi–Kitaev** BK-matched exponentials without JW projector; rejects "
                "**symmetry_conserving_bravyi_kitaev** qubit truncation); JW & BK operator pools "
                "``fermionic_uccsd*`` slices in ``operator_pool_registry_export_v1``; "
                "`configs/example_h2_uccsd.yaml`, `configs/example_h2_uccsd_trotter.yaml`, BK example "
                "`configs/example_h2_uccsd_bk.yaml` + integrations/ucc_reference; HEA+VQE stays valid on BK/SCBK Hamiltonians alone"
            ),
            "status": "partial_jw_sector_projector_bk_dense_packaged_scbk_truncation_na",
        },
        {
            "id": "adapt_iqeb_operator_pool_surface",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §2 — quantum.adapt_pool_id / iqeb_pool_id export",
            "inquanto_surface": "Chemically motivated excitation / pool selection (vendor documentation narrative)",
            "qchem_stack": (
                "quantum.operator_pool_registry (JW spin-UCCSD + singles/doubles slices; "
                "BK-mapped pools ``fermionic_uccsd_bravyi_kitaev`` + BK singles/doubles/concat; "
                "iqeb qubit-excitation pool; toy_pair_xx; aliases "
                "`qubit_excitation`→`iqeb_qubit_excitation`, `uccsd_jw`→`fermionic_uccsd`, "
                "`uccsd_bravyi_kitaev`/`uccsd_bk`→`fermionic_uccsd_bravyi_kitaev` via "
                "`operator_pool_registry_export_v1.pool_id_aliases`); YAML quantum.adapt_pool_id / quantum.iqeb_pool_id; "
                "run_summary echoes pool ids when adapt/iqeb runs; operator_pool_registry_export_v1 "
                "in algorithm_registry_alignment_v1 parity export block"
            ),
            "status": "executable_pools_partial_vs_vendor_full_excitation_taxonomy",
        },
        {
            "id": "dmet_scf_loop",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §3 — DMET / Schmidt",
            "inquanto_surface": "Full DMET self-consistency",
            "qchem_stack": (
                "schmidt_dmet_density_feedback_v1 + schmidt_dmet_multifragment_density_feedback_v1 + "
                "DMETSelfConsistencyLoop generic hooks + optional dense fragment ED "
                "(QubitHamiltonianFragmentSolverExact; configs/example_h4_dmet_fragment_exact_small.yaml); "
                "optional schmidt_bath_sidecar_json_path → embedding_workflow.schmidt_bath_sidecar_v1; "
                "ONIOM toy layers → embedding_workflow.oniom_toy_v1 (configs/example_oniom_toy.yaml)"
            ),
            "status": "schmidt_density_feedback_v1_plus_hooks_oniom_toy_yaml",
        },
        {
            "id": "tensornet",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — CuTensorNet; parity_snapshot tensornet_engine_resolved",
            "inquanto_surface": "CuTensorNetProtocol",
            "qchem_stack": "cutensornet_protocol_stub + integrations/tensornet_closure (strategy map)",
            "status": (
                "n_a_no_shipped_l3_chemistry_contraction_reason_open_stack_stub_only_not_inquanto_cutensornet"
            ),
        },
        {
            "id": "integrations_closure_layer",
            "parity_matrix_anchor": "docs/工程记忆_Quantinuum对标与数据流技术文档.md §0; open_gap_closure_reference",
            "inquanto_surface": "Product defaults (TKET boxes, UCC regrouping, DMET, Nexus, Qermit, TN)",
            "qchem_stack": "Package qchem_stack.integrations — see docs/工程记忆_Quantinuum对标与数据流技术文档.md §0 (L1 not L0)",
            "status": "reference_v1",
        },
        {
            "id": "drivers_cosmo_pbc",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §3 — chem/inquanto_driver_surface.py",
            "inquanto_surface": "COSMO / PBC / full driver surface",
            "qchem_stack": "ddCOSMO; pbc RHF/KRHF + k-mesh + optional PBC ddCOSMO",
            "status": "partial_kmesh",
        },
        {
            "id": "qpu_shot_histogram",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1–2 — Qiskit shots / device counts",
            "inquanto_surface": "Device counts → expectation",
            "qchem_stack": "Qiskit get_counts path + statevector sim",
            "status": "yes_qiskit",
        },
    ]


def _gap_id_and_anchor_pairs(gaps: list[dict[str, Any]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in gaps:
        rid = row.get("id")
        anchor = row.get("parity_matrix_anchor")
        if isinstance(rid, str) and rid and isinstance(anchor, str) and anchor:
            pairs.append((rid, anchor))
    return pairs


def inquanto_gap_anchor_index_v1() -> dict[str, Any]:
    """
    Stable machine-readable index for gap ``id`` <-> ``parity_matrix_anchor`` mappings.

    This is intentionally derived from :func:`inquanto_gap_categories` so parity dashboards can
    compare list payloads and anchor mappings with a single schema.
    """
    gaps = inquanto_gap_categories()
    pairs = _gap_id_and_anchor_pairs(gaps)
    return {
        "schema": "inquanto_gap_anchor_index_v1",
        "id_to_anchor": {rid: anchor for rid, anchor in pairs},
        "anchor_to_ids": {
            anchor: sorted([rid for rid, anchor2 in pairs if anchor2 == anchor])
            for anchor in sorted({anchor for _, anchor in pairs})
        },
    }


def validate_inquanto_gap_categories() -> list[str]:
    """
    Validate row-level invariants for :func:`inquanto_gap_categories`.

    Returns a list of error strings; empty list means valid.
    """
    gaps = inquanto_gap_categories()
    errors: list[str] = []
    if not isinstance(gaps, list) or not gaps:
        return ["gaps must be a non-empty list"]
    ids: list[str] = []
    anchors: list[str] = []
    for idx, row in enumerate(gaps):
        if not isinstance(row, dict):
            errors.append(f"row[{idx}] must be mapping")
            continue
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"row[{idx}] missing non-empty id")
        else:
            ids.append(rid)
        anchor = row.get("parity_matrix_anchor")
        if not isinstance(anchor, str) or not anchor:
            errors.append(f"row[{idx}] missing non-empty parity_matrix_anchor")
        else:
            anchors.append(anchor)
    if len(ids) != len(set(ids)):
        errors.append("duplicated gap id detected")
    if len(anchors) != len(set(anchors)):
        errors.append("duplicated parity_matrix_anchor detected")
    return errors
