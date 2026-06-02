"""Stable parity export keys and public expectation/mitigation semantics bundles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.config.quantum_helpers import (
    PAULI_PATH_EXACT,
    PAULI_PATH_QISKIT_COUNTS,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
)
from qchem_stack.contracts.schema_ids import (
    MITIGATION_EXECUTION_MODEL_V1,
    OPEN_STACK_DIFFERENTIATORS_V1,
    PROTOCOL_EXPECTATION_SEMANTICS_V1,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig

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


def mitigation_execution_model_public() -> dict[str, Any]:
    """Structured mitigation execution boundary for capability surfaces."""
    return {
        "schema": MITIGATION_EXECUTION_MODEL_V1,
        "sync_dag": {
            "open_stack": "mitigation/qermit_analog.py JSON graph + optional mitigation_dag_execution trace on pipeline result",
        },
        "async_batch_execution": {
            "open_stack": "jobs/mitigation_queue.py LocalMitigationJobQueue.drain_all",
            "status": "implemented_local_inprocess",
            "note": "In-process asyncio FIFO queue; not a distributed Nexus MitEx scheduler.",
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
