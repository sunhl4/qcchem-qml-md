"""Stable schema identifiers shared across modules.

Import from :mod:`qchem_stack.contracts` (or this module) instead of scattering
literal ``"*_v1"`` strings. Repro TypedDict guards live in :mod:`qchem_stack.repro.schema`.
"""

# Chemistry / pre-quantum handoff
PRE_QUANTUM_INPUT_SCHEMA_V1 = "pre_quantum_input_v1"
CLASSICAL_REFERENCE_BUNDLE_V1 = "classical_reference_bundle_v1"
PRECOMPUTED_MANIFEST_SCHEMA_V1 = "precomputed_manifest_v1"
PYSCF_ACTIVE_SPACE_INTEGRALS_V1 = "pyscf_active_space_integrals_v1"
EMBEDDING_INPUT_SYSTEM_V1 = "embedding_input_system_v1"
SCHMIDT_PRODUCTION_PIPELINE_V1 = "schmidt_production_pipeline_v1"

# Jobs / API surface
JOB_TIMELINE_V1 = "job_timeline_v1"
JOB_LIST_V1 = "job_list_v1"
JOB_STATUS_V1 = "job_status_v1"
JOB_EVENTS_V1 = "job_events_v1"
RUN_ENQUEUE_RESPONSE_V1 = "run_enqueue_response_v1"
RUN_REPRO_ONLY_V1 = "run_repro_only_v1"
RUN_PRODUCT_SUMMARY_V1 = "run_product_summary_v1"
PRODUCT_SURFACE_V1 = "product_surface_v1"
CAPABILITY_SURFACE_V2 = "capability_surface_v2"
CAPABILITY_GAP_EXPORT_V1 = "capability_gap_export_v1"
COMPUTABLES_PREVIEW_V1 = "computables_preview_v1"
QUEUE_STATS_V1 = "queue_stats_v1"

# Integrations / workflow preview
WORKFLOW_PREVIEW_V1 = "workflow_preview_v1"
COMPUTABLE_GRAPH_V1 = "computable_graph_v1"
COMPUTABLE_GRAPH_V2 = "computable_graph_v2"
COMPUTABLES_RICH_V1 = "computables_rich_v1"
VARIATIONAL_YAML_PLUGIN_DISPATCH_V1 = "variational_yaml_plugin_dispatch_v1"
WORKFLOW_PREVIEW_VQS_TRACK_V1 = "workflow_preview_vqs_track_v1"
WORKFLOW_PREVIEW_QPE_TRACK_V1 = "workflow_preview_qpe_track_v1"

# Orchestration / excited / protocol finalize
EXCITED_PROTOCOL_CONTRACT_V1 = "excited_protocol_contract_v1"
EXCITED_VQD_BUNDLE_V1 = "excited_vqd_bundle_v1"
EXCITED_QSE_BUNDLE_V1 = "excited_qse_bundle_v1"
EXCITED_SCEOM_BUNDLE_V1 = "excited_sceom_bundle_v1"
QPE_ALGORITHM_THREE_PACK_V1 = "qpe_algorithm_three_pack_v1"
PIPELINE_PROFILE_V1 = "pipeline_profile_v1"
PIPELINE_RESULT_V1 = "pipeline_result_v1"
ACTIVE_SPACE_EXPORTERS_REGISTRY_V1 = "active_space_exporters_registry_v1"
PRE_QUANTUM_BRANCH_REGISTRY_V1 = "pre_quantum_branch_registry_v1"

# Parity / repro / embedding snapshots
SCHMIDT_PER_FRAGMENT_VQE_V1 = "schmidt_per_fragment_vqe_v1"
SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1 = "schmidt_per_fragment_vqe_parity_summary_v1"
TKET_STATS_SKIPPED_V1 = "tket_stats_skipped_v1"
ZNE_QISKIT_UNIFICATION_V1 = "zne_qiskit_unification_v1"
CUTENSORTNET_PROTOCOL_STUB_V1 = "cutensornet_protocol_stub_v1"
CLASSICAL_BENCHMARK_SUMMARY_V1 = "classical_benchmark_summary_v1"
QPE_OPEN_STACK_CONTRACT_V1 = "qpe_open_stack_contract_v1"
VQS_OPEN_STACK_CONTRACT_V1 = "vqs_open_stack_contract_v1"
DMET_OPEN_ARCHITECTURE_V1 = "dmet_open_architecture_v1"
PROJECTION_EMBEDDING_OPEN_TRACE_V1 = "projection_embedding_open_trace_v1"
EMBEDDING_WORKFLOW_V1 = "embedding_workflow_v1"
PROJECTION_EMBEDDING_WORKFLOW_V1 = "projection_embedding_workflow_v1"
ONIOM_TOY_V1 = "oniom_toy_v1"

# Integrations / RDM
RDM_CORRECTION_REPORT_V1 = "rdm_correction_report_v1"
RDM_CORRECTION_READINESS_V1 = "rdm_correction_readiness_v1"

# Integrations / DMET / TKET / Nexus / benchmarks
DMET_ONE_SHOT_V1 = "dmet_one_shot_v1"
DMET_SELF_CONSISTENCY_V1 = "dmet_self_consistency_v1"
DMET_UNIFORM_MULTIFRAGMENT_TOY_V1 = "dmet_uniform_multifragment_toy_v1"
SCHMIDT_DMET_DENSITY_FEEDBACK_V1 = "schmidt_dmet_density_feedback_v1"
SCHMIDT_DMET_MULTIFRAGMENT_DENSITY_FEEDBACK_V1 = "schmidt_dmet_multifragment_density_feedback_v1"
CROSS_SOLVER_HF_PARITY_V1 = "cross_solver_hf_parity_v1"
OPEN_DRIVER_SURFACE_V1 = "open_driver_surface_v1"
OPEN_GAP_CLOSURE_REFERENCE_V1 = "open_gap_closure_reference_v1"
RESOURCE_ESTIMATION_PREVIEW_V1 = "resource_estimation_preview_v1"
METHODS_RESOURCE_UNIFIED_V1 = "methods_resource_unified_v1"
ALGORITHM_BENCHMARK_BUNDLE_V1 = "algorithm_benchmark_bundle_v1"
MERGED_EXPERIMENT_BENCHMARK_V1 = "merged_experiment_benchmark_v1"
TENSORNET_CLOSURE_REFERENCE_V1 = "tensornet_closure_reference_v1"
QERMIT_OPEN_REFERENCE_V1 = "qermit_open_reference_v1"
QERMIT_EXECUTION_OVERLAY_V1 = "qermit_execution_overlay_v1"
TKET_CLOSURE_LAYER_V1 = "tket_closure_layer_v1"
TKET_STATS_ATTEMPT_V1 = "tket_stats_attempt_v1"
TKET_PEEPHOLE_OPTIMIZE_V1 = "tket_peephole_optimize_v1"
QNEXUS_PROBE_V1 = "qnexus_probe_v1"
NEXUS_PUBLIC_WORKFLOW_BLUEPRINT_V1 = "nexus_public_workflow_blueprint_v1"

# Parity export (stable top-level keys documented in repro.schema)
PARITY_EXPORT_SCHEMA_VERSION_V3 = 3

# L3 / MD bridge / mapping registry
L3_ENERGY_BOOTSTRAP_STUB_V1 = "l3_energy_bootstrap_stub_v1"
ML_MD_BRIDGE_SURFACE_V1 = "ml_md_bridge_surface_v1"
QMEF_ML_ATTACHMENT_V1 = "qmef_ml_attachment_v1"
TANGELO_PUBLIC_MAPPING_ALIAS_SURFACE_V1 = "tangelo_public_mapping_alias_surface_v1"

# Chemistry / embedding / integration (P12)
PSI4_ACTIVE_SPACE_INTEGRALS_V1 = "psi4_active_space_integrals_v1"
PRECOMPUTED_CONFIG_FINGERPRINT_V1 = "precomputed_config_fingerprint_v1"
SCHMIDT_IMPURITY_INTEGRALS_V1 = "schmidt_impurity_integrals_v1"
SCHMIDT_FCI_FRAGMENT_V1 = "schmidt_fci_fragment_v1"
DMET_MU_BISECTION_V1 = "dmet_mu_bisection_v1"
INTEGRAL_CROSSCHECK_CASCI_V1 = "integral_crosscheck_casci_v1"
RESTRICTED_ACTIVE_SPACE_QUANTUM_PROBLEM_V1 = "restricted_active_space_quantum_problem_v1"
RUN_BUILD_CACHE_V1 = "run_build_cache_v1"
CASSCF_ORBITAL_AUDIT_V1 = "casscf_orbital_audit_v1"
PROJECTION_MULLIKEN_MO_AUDIT_V1 = "projection_mulliken_mo_audit_v1"
MO_COEFF_TRANSFORM_HOOK_V1 = "mo_coeff_transform_hook_v1"
INTEGRATION_CHECKLIST_REPORT_V1 = "integration_checklist_report_v1"
CHEMISTRY_PROBLEM_BUNDLE_V1 = "chemistry_problem_bundle_v1"
ENERGY_COMPONENTS_V1 = "energy_components_v1"
SOLVER_ADAPTER_CONTRACT_REPORT_V1 = "solver_adapter_contract_report_v1"
DENSE_EXPECTATION_REFERENCE_V1 = "dense_expectation_reference_v1"

# Jobs / nexus (P12)
NEXUS_CLOUD_ADAPTER_V1 = "nexus_cloud_adapter_v1"
NEXUS_ANALOG_V1 = "nexus_analog_v1"
FULL_PIPELINE_JOB_RESULT_V1 = "full_pipeline_job_result_v1"

# MD bridge (P12)
QMEF_VALIDATE_V1 = "qmef_validate_v1"
ML_MD_TRAINER_STUB_FIT_V1 = "ml_md_trainer_stub_fit_v1"

# Quantum algorithms / QPE demo (P12)
TANGELO_DEFLATION_ANALOGY_V1 = "tangelo_deflation_analogy_v1"
VQD_CROSS_STACK_SEMANTICS_V1 = "vqd_cross_stack_semantics_v1"
UCCSD_MAPPING_SUPPORT_MATRIX_V1 = "uccsd_mapping_support_matrix_v1"
OPERATOR_POOL_REGISTRY_EXPORT_V1 = "operator_pool_registry_export_v1"
VQS_TRACK_V1 = "vqs_track_v1"
VQS_INTEGRATION_CONTRACT_V1 = "vqs_integration_contract_v1"
ALGORITHM_VQE_REPORT_V1 = "algorithm_vqe_report_v1"
PHASE_ESTIMATION_CONTRACT_V1 = "phase_estimation_contract_v1"
QPE_QEC_DEMO_TRACK_V1 = "qpe_qec_demo_track_v1"
BAYESIAN_QPE_STUB_MAP_V1 = "bayesian_qpe_stub_map_v1"

# Protocols / mitigation (P12)
PROTOCOL_EXPECTATION_SEMANTICS_V1 = "protocol_expectation_semantics_v1"
MITIGATION_EXECUTION_MODEL_V1 = "mitigation_execution_model_v1"
OPEN_STACK_DIFFERENTIATORS_V1 = "open_stack_differentiators_v1"
PRODUCT_GAP_ANCHOR_INDEX_V1 = "product_gap_anchor_index_v1"
QERMIT_RUNTIME_V1 = "qermit_runtime_v1"
MAPPING_STATUS_ROWS_V1 = "mapping_status_rows_v1"

__all__ = [
    "PRE_QUANTUM_INPUT_SCHEMA_V1",
    "CLASSICAL_REFERENCE_BUNDLE_V1",
    "PRECOMPUTED_MANIFEST_SCHEMA_V1",
    "PYSCF_ACTIVE_SPACE_INTEGRALS_V1",
    "EMBEDDING_INPUT_SYSTEM_V1",
    "SCHMIDT_PRODUCTION_PIPELINE_V1",
    "JOB_TIMELINE_V1",
    "JOB_LIST_V1",
    "JOB_STATUS_V1",
    "JOB_EVENTS_V1",
    "RUN_ENQUEUE_RESPONSE_V1",
    "RUN_REPRO_ONLY_V1",
    "RUN_PRODUCT_SUMMARY_V1",
    "PRODUCT_SURFACE_V1",
    "CAPABILITY_SURFACE_V2",
    "CAPABILITY_GAP_EXPORT_V1",
    "COMPUTABLES_PREVIEW_V1",
    "QUEUE_STATS_V1",
    "WORKFLOW_PREVIEW_V1",
    "COMPUTABLE_GRAPH_V1",
    "COMPUTABLE_GRAPH_V2",
    "COMPUTABLES_RICH_V1",
    "VARIATIONAL_YAML_PLUGIN_DISPATCH_V1",
    "WORKFLOW_PREVIEW_VQS_TRACK_V1",
    "WORKFLOW_PREVIEW_QPE_TRACK_V1",
    "EXCITED_PROTOCOL_CONTRACT_V1",
    "EXCITED_VQD_BUNDLE_V1",
    "EXCITED_QSE_BUNDLE_V1",
    "EXCITED_SCEOM_BUNDLE_V1",
    "QPE_ALGORITHM_THREE_PACK_V1",
    "PIPELINE_PROFILE_V1",
    "PIPELINE_RESULT_V1",
    "ACTIVE_SPACE_EXPORTERS_REGISTRY_V1",
    "PRE_QUANTUM_BRANCH_REGISTRY_V1",
    "SCHMIDT_PER_FRAGMENT_VQE_V1",
    "SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1",
    "TKET_STATS_SKIPPED_V1",
    "ZNE_QISKIT_UNIFICATION_V1",
    "CUTENSORTNET_PROTOCOL_STUB_V1",
    "CLASSICAL_BENCHMARK_SUMMARY_V1",
    "QPE_OPEN_STACK_CONTRACT_V1",
    "VQS_OPEN_STACK_CONTRACT_V1",
    "DMET_OPEN_ARCHITECTURE_V1",
    "PROJECTION_EMBEDDING_OPEN_TRACE_V1",
    "EMBEDDING_WORKFLOW_V1",
    "PROJECTION_EMBEDDING_WORKFLOW_V1",
    "ONIOM_TOY_V1",
    "RDM_CORRECTION_REPORT_V1",
    "RDM_CORRECTION_READINESS_V1",
    "DMET_ONE_SHOT_V1",
    "DMET_SELF_CONSISTENCY_V1",
    "DMET_UNIFORM_MULTIFRAGMENT_TOY_V1",
    "SCHMIDT_DMET_DENSITY_FEEDBACK_V1",
    "SCHMIDT_DMET_MULTIFRAGMENT_DENSITY_FEEDBACK_V1",
    "CROSS_SOLVER_HF_PARITY_V1",
    "OPEN_DRIVER_SURFACE_V1",
    "OPEN_GAP_CLOSURE_REFERENCE_V1",
    "RESOURCE_ESTIMATION_PREVIEW_V1",
    "METHODS_RESOURCE_UNIFIED_V1",
    "ALGORITHM_BENCHMARK_BUNDLE_V1",
    "MERGED_EXPERIMENT_BENCHMARK_V1",
    "TENSORNET_CLOSURE_REFERENCE_V1",
    "QERMIT_OPEN_REFERENCE_V1",
    "QERMIT_EXECUTION_OVERLAY_V1",
    "TKET_CLOSURE_LAYER_V1",
    "TKET_STATS_ATTEMPT_V1",
    "TKET_PEEPHOLE_OPTIMIZE_V1",
    "QNEXUS_PROBE_V1",
    "NEXUS_PUBLIC_WORKFLOW_BLUEPRINT_V1",
    "PARITY_EXPORT_SCHEMA_VERSION_V3",
    "L3_ENERGY_BOOTSTRAP_STUB_V1",
    "ML_MD_BRIDGE_SURFACE_V1",
    "QMEF_ML_ATTACHMENT_V1",
    "TANGELO_PUBLIC_MAPPING_ALIAS_SURFACE_V1",
    "PSI4_ACTIVE_SPACE_INTEGRALS_V1",
    "PRECOMPUTED_CONFIG_FINGERPRINT_V1",
    "SCHMIDT_IMPURITY_INTEGRALS_V1",
    "SCHMIDT_FCI_FRAGMENT_V1",
    "DMET_MU_BISECTION_V1",
    "INTEGRAL_CROSSCHECK_CASCI_V1",
    "RESTRICTED_ACTIVE_SPACE_QUANTUM_PROBLEM_V1",
    "RUN_BUILD_CACHE_V1",
    "CASSCF_ORBITAL_AUDIT_V1",
    "PROJECTION_MULLIKEN_MO_AUDIT_V1",
    "MO_COEFF_TRANSFORM_HOOK_V1",
    "INTEGRATION_CHECKLIST_REPORT_V1",
    "CHEMISTRY_PROBLEM_BUNDLE_V1",
    "ENERGY_COMPONENTS_V1",
    "SOLVER_ADAPTER_CONTRACT_REPORT_V1",
    "DENSE_EXPECTATION_REFERENCE_V1",
    "NEXUS_CLOUD_ADAPTER_V1",
    "NEXUS_ANALOG_V1",
    "FULL_PIPELINE_JOB_RESULT_V1",
    "QMEF_VALIDATE_V1",
    "ML_MD_TRAINER_STUB_FIT_V1",
    "TANGELO_DEFLATION_ANALOGY_V1",
    "VQD_CROSS_STACK_SEMANTICS_V1",
    "UCCSD_MAPPING_SUPPORT_MATRIX_V1",
    "OPERATOR_POOL_REGISTRY_EXPORT_V1",
    "VQS_TRACK_V1",
    "VQS_INTEGRATION_CONTRACT_V1",
    "ALGORITHM_VQE_REPORT_V1",
    "PHASE_ESTIMATION_CONTRACT_V1",
    "QPE_QEC_DEMO_TRACK_V1",
    "BAYESIAN_QPE_STUB_MAP_V1",
    "PROTOCOL_EXPECTATION_SEMANTICS_V1",
    "MITIGATION_EXECUTION_MODEL_V1",
    "OPEN_STACK_DIFFERENTIATORS_V1",
    "PRODUCT_GAP_ANCHOR_INDEX_V1",
    "QERMIT_RUNTIME_V1",
    "MAPPING_STATUS_ROWS_V1",
]
