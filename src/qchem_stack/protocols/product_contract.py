"""
Release-facing product contracts and stable export registries.

This module is the public contract surface for qchem_stack itself. Competitive
alignment artifacts are intentionally kept out of the default release payloads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.config.quantum_helpers import (
    PAULI_PATH_EXACT,
    PAULI_PATH_QISKIT_COUNTS,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
)
from qchem_stack.contracts.schema_ids import (
    ANSATZ_PROTOCOL_MATRIX_V1,
    MITIGATION_EXECUTION_MODEL_V1,
    OPEN_STACK_DIFFERENTIATORS_V1,
    PRODUCT_GAP_ANCHOR_INDEX_V1,
    PROTOCOL_EXPECTATION_SEMANTICS_V1,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig, QuantumSpec

# Stable JSON tokens for parity snapshot / export scripts (canonical in quantum_helpers).

PARITY_EXPORT_V3_STABLE_KEYS: frozenset[str] = frozenset(
    {
        "parity_export_schema_version",
        "experiment_id",
        "computable_abstract",
        "excited_resource_from_config",
        "capability_gap_categories",
        "iqeb_implementation_path",
        "pauli_protocol_expectation_path",
        "protocol_expectation_semantics_v1",
        "geometry_source",
        "embedding",
        "pre_quantum_semantics_from_config",
    }
)

PRODUCT_CAPABILITY_MAP: dict[str, str] = {
    "ProtocolLifecycle": "qchem_stack.protocols.protocol.PauliAveragingProtocol + ProtocolPhase",
    "VQE": "qchem_stack.quantum.algorithms.vqe.VQE",
    "AdaptVQE": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
    "IQEB": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
    "ExcitedStateVQDQSE": "qchem_stack.quantum.algorithms.excited",
    "SCEOM": "qchem_stack.quantum.algorithms.sceom.run_sceom_nested_commutator_from_hea",
    "QPETracks": "qchem_stack.quantum.algorithms.qpe + qchem_stack.qpe_qec_demo.pipeline_track",
    "VQSTracks": "qchem_stack.quantum.algorithms.vqs + vqs_pipeline_track",
    "ComputableGraph": "qchem_stack.protocols.computable + workflow_preview.computable_graph_v2 integration",
    "ResourceRows": "qchem_stack.backends.spec.circuit_resource_row + dataframe_circuit_shot_rows",
    "JobRuntime": "qchem_stack.jobs.store.SqliteJobStore + qchem_stack.jobs.nexus_analog",
    "MitigationPipeline": "qchem_stack.mitigation.qermit_analog + qchem_stack.mitigation.qermit_runtime",
    "ChemistryDrivers": "qchem_stack.chem.solvers + qchem_stack.chem.bridges (legacy: chem.drivers)",
    "EmbeddingFlow": "qchem_stack.chem.embedding + qchem_stack.integrations.dmet_self_consistent",
    "MLMDBridge": "qchem_stack.md_bridge",
}

PRODUCT_GAP_CATEGORIES_V1: list[dict[str, Any]] = [
    {
        "id": "managed_cloud_runtime",
        "release_anchor": "product_capability_matrix.md#managed-cloud-runtime",
        "open_stack_surface": "Local SQLite queue, optional HTTP sidecar adapters, and analog billing only.",
        "status": "local_runtime_only",
    },
    {
        "id": "http_submission_workspace_ops",
        "release_anchor": "product_capability_matrix.md#http-submission-and-ops",
        "open_stack_surface": "FastAPI submit/list/poll endpoints with project/workspace fields.",
        "status": "available",
    },
    {
        "id": "mitigation_batch_scheduler",
        "release_anchor": "product_capability_matrix.md#mitigation-runtime",
        "open_stack_surface": "DAG + linear trace are implemented; distributed async mitigation scheduler is not.",
        "status": "partial_runtime",
    },
    {
        "id": "computable_composition_surface",
        "release_anchor": "product_capability_matrix.md#computable-and-workflow-preview",
        "open_stack_surface": "Computable graph preview and rich slices are implemented for YAML-driven flows.",
        "status": "available",
    },
    {
        "id": "evaluate_support_set_reasoning",
        "release_anchor": "product_capability_matrix.md#evaluate-support-set",
        "open_stack_surface": "Conservative Pauli set-containment checks are implemented.",
        "status": "available",
    },
    {
        "id": "compiler_pass_depth",
        "release_anchor": "product_capability_matrix.md#compiler-and-pass-bundle",
        "open_stack_surface": "CompilerSpec + CircuitIR pass bundle are implemented; managed pass presets remain limited.",
        "status": "partial",
    },
    {
        "id": "chemically_aware_ansatz_pack",
        "release_anchor": "product_capability_matrix.md#ansatz-and-operator-pools",
        "open_stack_surface": "HEA + UCCSD/JW/BK options implemented with explicit boundaries.",
        "status": "partial",
    },
    {
        "id": "operator_pool_taxonomy_depth",
        "release_anchor": "product_capability_matrix.md#operator-pool-registry",
        "open_stack_surface": "Executable ADAPT/IQEB pools and aliases are implemented; broader taxonomy is still growing.",
        "status": "partial",
    },
    {
        "id": "dmet_self_consistency_depth",
        "release_anchor": "product_capability_matrix.md#embedding-and-dmet",
        "open_stack_surface": "Density-feedback and hook-based loops are available with explicit caveats.",
        "status": "partial",
    },
    {
        "id": "tensor_network_engine",
        "release_anchor": "product_capability_matrix.md#tensor-network",
        "open_stack_surface": "Stub workflow and strategy resolution are available; full production contraction stack is out of scope.",
        "status": "stub_only",
    },
    {
        "id": "integration_closure",
        "release_anchor": "product_capability_matrix.md#integration-closure-layer",
        "open_stack_surface": "Integration closure helpers are available as open reference implementations.",
        "status": "reference",
    },
    {
        "id": "driver_surface_breadth",
        "release_anchor": "product_capability_matrix.md#driver-surface",
        "open_stack_surface": "PySCF-focused surface with ddCOSMO and PBC variants; broader driver matrix is partial.",
        "status": "partial",
    },
    {
        "id": "device_shot_histogram_flow",
        "release_anchor": "product_capability_matrix.md#shot-histogram-paths",
        "open_stack_surface": "Statevector grouped shots and Qiskit counts pipelines are implemented.",
        "status": "available",
    },
]


def classify_pauli_expectation_path(q: QuantumSpec) -> str:
    """Classify how ``energy_pauli_protocol`` is produced from config intent."""
    from qchem_stack.config.quantum_helpers import classify_pauli_expectation_path_from_flags

    return classify_pauli_expectation_path_from_flags(
        use_protocol=bool(q.pauli.use_protocol),
        run_sampled=bool(q.pauli.run_sampled),
        run_qiskit_shots=bool(q.pauli.run_qiskit_shots),
    )


def pauli_protocol_expectation_path_for_config(cfg: ExperimentConfig) -> str:
    """Convenience wrapper over :func:`classify_pauli_expectation_path_for_config`."""
    from qchem_stack.config.quantum_helpers import classify_pauli_expectation_path_for_config

    return classify_pauli_expectation_path_for_config(cfg)


def protocol_expectation_semantics_public() -> dict[str, Any]:
    """Stable mapping from YAML intent to protocol expectation semantics."""
    return {
        "schema": PROTOCOL_EXPECTATION_SEMANTICS_V1,
        "doc_anchor": "docs/技术文档_设备比特串与Qiskit采样路径.md (section 2)",
        "yaml_mutual_exclusion": (
            "QuantumSpec.pauli.run_sampled XOR run_qiskit_shots_pauli_protocol "
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


def ansatz_protocol_matrix_v1() -> dict[str, Any]:
    """Ansatz × protocol compatibility matrix (InQuanto/Tangelo-style orthogonality)."""
    return {
        "schema": ANSATZ_PROTOCOL_MATRIX_V1,
        "doc_anchor": "docs/quantum_模块风格约定.md#8-epistemic-bounds算法实现边界",
        "entries": [
            {
                "ansatz": "hea",
                "protocol": "pauli_averaging_exact",
                "status": "supported",
                "prep": "hea_operations",
            },
            {
                "ansatz": "hea",
                "protocol": "pauli_averaging_sampled",
                "status": "supported",
                "prep": "hea_operations",
            },
            {
                "ansatz": "hea",
                "protocol": "pauli_averaging_qiskit",
                "status": "supported",
                "prep": "hea_operations",
            },
            {
                "ansatz": "hea",
                "protocol": "zne_circuit_scale_fold",
                "status": "supported",
                "prep": "hea_depth_fold",
            },
            {
                "ansatz": "uccsd",
                "protocol": "pauli_averaging_exact",
                "status": "supported",
                "prep": "uccsd_circuit_ir_jw",
                "mapping": "jordan_wigner",
            },
            {
                "ansatz": "uccsd",
                "protocol": "pauli_averaging_sampled",
                "status": "supported",
                "prep": "uccsd_circuit_ir_jw",
                "mapping": "jordan_wigner",
            },
            {
                "ansatz": "uccsd",
                "protocol": "pauli_averaging_qiskit",
                "status": "supported",
                "prep": "uccsd_circuit_ir_jw",
                "mapping": "jordan_wigner",
            },
            {
                "ansatz": "uccsd",
                "protocol": "zne_circuit_scale_fold",
                "status": "unsupported",
                "reason": "HEA-only depth fold; use zne.mode=scalar_stub",
            },
            {
                "ansatz": "hea",
                "protocol": "qse_pauli_transitions",
                "status": "supported",
                "basis": "hea_pauli_x_bump_legacy",
            },
            {
                "ansatz": "uccsd",
                "protocol": "qse_pauli_transitions",
                "status": "supported",
                "basis": "uccsd_fermionic_singles",
            },
        ],
    }


def mitigation_execution_model_public() -> dict[str, Any]:
    """Structured mitigation execution boundary for capability surfaces."""
    return {
        "schema": MITIGATION_EXECUTION_MODEL_V1,
        "sync_dag": {
            "open_stack": "mitigation/qermit_analog.py JSON graph + optional mitigation_dag_execution trace on pipeline result",
        },
        "async_batch_execution": {
            "open_stack": "not_implemented_distributed_mitigation_batch_scheduler",
            "note": "Local SQLite jobs run whole experiments; mitigation executes inline in pipeline runs.",
        },
        "epistemic_bound": "Open-stack execution model only.",
    }


def open_stack_differentiators_public() -> dict[str, Any]:
    """Open-stack strengths as a machine-readable bundle."""
    return {
        "schema": OPEN_STACK_DIFFERENTIATORS_V1,
        "scope_excludes": ["managed_cloud_runtime", "proprietary_hardware_calibration"],
        "bundle": [
            {
                "id": "full_stack_open_methods",
                "summary": "Orchestration, protocol, chemistry drivers, jobs, and exports are auditable end-to-end.",
                "evidence_modules": ["qchem_stack/"],
            },
            {
                "id": "strict_contract_and_ci_gates",
                "summary": "Frozen export keys, sample export checks, and registry tests enforce stable contracts.",
                "evidence_modules": [
                    "scripts/export_parity_criteria_table.py",
                    "scripts/check_parity_export_sample.py",
                    "protocols/product_contract.py",
                ],
            },
            {
                "id": "multi_backend_execution",
                "summary": "Single YAML can drive statevector, Qiskit, and mocked device-style backends.",
                "evidence_modules": ["backends/"],
            },
            {
                "id": "md_ml_extension_lane",
                "summary": "Integrated MD/ML bridge and dataset contracts are first-class in the same stack.",
                "evidence_modules": ["md_bridge/"],
            },
        ],
    }


def product_capability_map_for_docs() -> dict[str, str]:
    """Product-facing capability map."""
    return dict(PRODUCT_CAPABILITY_MAP)


def product_gap_categories() -> list[dict[str, Any]]:
    """Product-facing capability gaps for release surfaces."""
    return [dict(row) for row in PRODUCT_GAP_CATEGORIES_V1]


def _gap_id_and_anchor_pairs(gaps: list[dict[str, Any]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in gaps:
        rid = row.get("id")
        anchor = row.get("release_anchor")
        if isinstance(rid, str) and rid and isinstance(anchor, str) and anchor:
            pairs.append((rid, anchor))
    return pairs


def product_gap_anchor_index_v1() -> dict[str, Any]:
    """Stable index for gap ``id`` <-> ``release_anchor`` mappings."""
    gaps = product_gap_categories()
    pairs = _gap_id_and_anchor_pairs(gaps)
    return {
        "schema": PRODUCT_GAP_ANCHOR_INDEX_V1,
        "id_to_anchor": {rid: anchor for rid, anchor in pairs},
        "anchor_to_ids": {
            anchor: sorted([rid for rid, anchor2 in pairs if anchor2 == anchor])
            for anchor in sorted({anchor for _, anchor in pairs})
        },
    }


def validate_product_gap_categories() -> list[str]:
    """Validate row-level invariants for :func:`product_gap_categories`."""
    gaps = product_gap_categories()
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
        anchor = row.get("release_anchor")
        if not isinstance(anchor, str) or not anchor:
            errors.append(f"row[{idx}] missing non-empty release_anchor")
        else:
            anchors.append(anchor)
    if len(ids) != len(set(ids)):
        errors.append("duplicated gap id detected")
    if len(anchors) != len(set(anchors)):
        errors.append("duplicated release_anchor detected")
    return errors
