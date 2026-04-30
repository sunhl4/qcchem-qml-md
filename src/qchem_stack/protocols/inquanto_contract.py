"""
Public contract helpers: map InQuanto *documentation-level* names to this stack.

This does **not** import closed-source InQuanto; it is for reproducibility / Methods tables only.
See ``docs/与InQuanto能力差距与实施计划.md`` and ``docs/inquanto_public_parity_matrix.md``.
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
    "AlgorithmIQEB": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE (outer-loop Pauli correction + VQE; set quantum.algorithm=iqeb; configs/example_h2_iqeb.yaml)",
    "AlgorithmVQD": "qchem_stack.quantum.algorithms.excited.VQD",
    "AlgorithmQSE": "qchem_stack.quantum.algorithms.excited.QSE + quantum.qse_transition (Pauli transition shot modes)",
    "AlgorithmSCEOM": "qchem_stack.quantum.algorithms.sceom.run_sceom_nested_commutator_from_hea",
    "Algorithm*QPE (track)": "qchem_stack.qpe_qec_demo + pipeline._attach_qpe_demo_track_if_requested (qpe_demo_track_after_variational)",
    "AlgorithmBayesianQPE + Phayes": "qchem_stack.qpe_qec_demo.BayesianQPEStub",
    "Qubit Hamiltonian (JW)": "qchem_stack.chem.hamiltonian.QubitHamiltonian / molecular_hamiltonian_from_pyscf",
    "dataframe_circuit / shot rows": "qchem_stack.backends.spec.circuit_resource_row, dataframe_circuit_shot_rows",
    "Computable (expectation from circuits)": "qchem_stack.protocols.computable + integrations.inquanto_workflow_preview.computable_graph_v2 + POST /v1/meta/workflow-preview",
    "TKET / pytket pass metrics": "optional: qchem_stack.integrations.tket_fullchain + backends.pytket_bridge (parity_integrations.tket_first_circuit_stats)",
    "qnexus / Nexus jobs": "qchem_stack.jobs: SqliteJobStore + nexus_analog_ledger + nexus_cloud (optional HTTP/mock), job nexus_analog_billing",
    "DMET fragment solver (stub)": "qchem_stack.chem.embedding.dmet.VQEFragmentSolverStub",
    "DMET self-consistency (density feedback)": "integrations/schmidt_dmet_self_consistent.run_schmidt_density_feedback_cycles + DMETSelfConsistencyLoop.run_with_hooks",
    "DMET Schmidt optional per-fragment VQE": "orchestration/pipeline._run_schmidt_per_fragment_vqe (EmbeddingSpec.schmidt_run_vqe_on_all_fragments)",
    "Noise mitigation (Qermit-style)": "qermit_analog (DAG) + qermit_runtime (linear trace) + mitigation/ (PMSV/ZNE/SPAM stubs)",
    "Device counts → expectation (Qiskit path)": "QuantumSpec.run_qiskit_shots_pauli_protocol + protocol Pauli evaluate path (see pauli_contract)",
    "Classical chemistry surface (COSMO / PBC names)": "chem.inquanto_driver_surface.INQUANTO_DRIVER_ALIAS_TO_CONFIG + PySCF drivers",
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
                ],
            },
            {
                "id": "strict_repro_run_summary",
                "summary": "Single JSON blob: repro.parity_snapshot + run_summary stage semantics for papers.",
                "evidence_modules": ["orchestration/pipeline.py", "repro/"],
            },
            {
                "id": "multi_backend_no_single_vendor_gate",
                "summary": "statevector / qiskit / ionstack mock executors under one YAML.",
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
        "mitigation_execution_class",
        "mitigation_zne_scales",
        "compiler_native_twoq",
        "compiler_optimization_level",
        "compiler_preoptimize_passes",
        "compiler_passes_yaml",
        "compiler_bundle_signature",
        "pauli_support_max_terms",
        "vqd_after_variational",
        "vqd_n_states",
        "vqd_penalty_weight",
        "vqd_shots_objective",
        "vqd_shots_overlap",
        "vqd_shots_weight",
        "qse_after_variational",
        "qse_subspace_dim",
        "qse_max_basis",
        "qse_shot_mode",
        "qse_shots_per_matrix_element",
        "qse_shots_per_ij_term",
        "sceom_after_variational",
        "sceom_subspace_dim",
        "sceom_shots_per_matrix_element",
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
        "embedding",
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
        raise ValueError("run_sampled_pauli_protocol and run_qiskit_shots_pauli_protocol are mutually exclusive")
    if q.run_sampled_pauli_protocol:
        return PAULI_PATH_STATEVECTOR_SHOT_SIM
    if q.run_qiskit_shots_pauli_protocol:
        return PAULI_PATH_QISKIT_COUNTS
    return PAULI_PATH_EXACT


def pauli_protocol_expectation_path_for_config(cfg: ExperimentConfig) -> str:
    """Convenience: classify from a full :class:`ExperimentConfig`."""
    return classify_pauli_expectation_path(cfg.quantum)


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
            "qchem_stack": "qermit_analog + qermit_runtime + integrations/qermit_reference (capability matrix)",
            "status": "analog_v2_runtime",
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
            "qchem_stack": "HEA + ADAPT + IQEB (quantum.algorithm=iqeb; configs/example_h2_iqeb.yaml) + integrations/ucc_reference (fermion generators + ChemicallyAwareUCCPolicy hook)",
            "status": "partial",
        },
        {
            "id": "dmet_scf_loop",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §3 — DMET / Schmidt",
            "inquanto_surface": "Full DMET self-consistency",
            "qchem_stack": "schmidt_dmet_density_feedback_v1 + schmidt_dmet_multifragment_density_feedback_v1 + DMETSelfConsistencyLoop generic hooks",
            "status": "schmidt_density_feedback_v1",
        },
        {
            "id": "tensornet",
            "parity_matrix_anchor": "inquanto_public_parity_matrix.md §1 — CuTensorNet; parity_snapshot tensornet_engine_resolved",
            "inquanto_surface": "CuTensorNetProtocol",
            "qchem_stack": "cutensornet_protocol_stub + integrations/tensornet_closure (strategy map)",
            "status": "stub_plus_vendor_hooks",
        },
        {
            "id": "integrations_closure_layer",
            "parity_matrix_anchor": "docs/架构_InQuanto闭源能力闭合与可复现边界.md; open_gap_closure_reference",
            "inquanto_surface": "Product defaults (TKET boxes, UCC regrouping, DMET, Nexus, Qermit, TN)",
            "qchem_stack": "Package qchem_stack.integrations — see docs/架构_InQuanto闭源能力闭合与可复现边界.md (L1 not L0)",
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
