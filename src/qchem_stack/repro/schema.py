"""Typed repro / parity payload shapes (stable keys and write-side guards).

Schema id strings live in :mod:`qchem_stack.contracts.schema_ids`;
use :func:`qchem_stack.contracts.validate.assert_payload_schema` for runtime checks.

Pipeline sync output shapes: :mod:`qchem_stack.orchestration.pipeline_result`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

from qchem_stack.contracts.schema_ids import (
    PARITY_EXPORT_SCHEMA_VERSION_V3,
    PIPELINE_PROFILE_V1,
    PRE_QUANTUM_INPUT_SCHEMA_V1,
    WORKFLOW_PREVIEW_V1,
)
from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS

if TYPE_CHECKING:
    from collections.abc import Mapping


class ParitySnapshotV1(TypedDict, total=False):
    quantum_algorithm: str
    fermion_qubit_mapping: str
    use_pauli_protocol: bool
    vqe_depth: int
    vqe_maxiter: int
    pre_quantum_handoff_v1: dict[str, object]
    pipeline_profile: PipelineProfileV1
    workflow_preview_v1: WorkflowPreviewReproV1


class PipelineProfileV1(TypedDict):
    schema: str
    stages: list[dict[str, object]]
    total_wall_ms: float


class WorkflowPreviewReproV1(TypedDict, total=False):
    schema: str
    experiment_id: str
    protocol_stages: list[dict[str, object]]
    computable_graph: dict[str, object]
    computable_abstract: dict[str, object]


class RunSummaryV1(TypedDict, total=False):
    stages_completed: list[str]
    quantum_algorithm: str
    classical_backend_id: str
    pauli_protocol_expectation_path: str
    pipeline_total_wall_ms: float
    pipeline_slowest_stage: str


class PreQuantumHandoffV1(TypedDict, total=False):
    """Subset of pre-quantum summary; canonical id ``PRE_QUANTUM_INPUT_SCHEMA_V1``."""

    source: str
    backend_tag: str
    hamiltonian_fingerprint: str
    hamiltonian_branch: NotRequired[str]
    integral_source: NotRequired[str]


class ParityExportV3Payload(TypedDict):
    """Top-level parity criteria export (``scripts/export_parity_criteria_table.py``)."""

    parity_export_schema_version: int
    experiment_id: str
    computable_abstract: dict[str, object]
    excited_resource_from_config: dict[str, object]
    capability_gap_categories: list[dict[str, object]]
    iqeb_implementation_path: str
    pauli_protocol_expectation_path: str
    protocol_expectation_semantics_v1: dict[str, object]
    geometry_source: dict[str, object]
    embedding: dict[str, object]
    pre_quantum_semantics_from_config: dict[str, object]


# Re-export for repro consumers documenting canonical schema ids.
PRE_QUANTUM_HANDOFF_SCHEMA_V1 = PRE_QUANTUM_INPUT_SCHEMA_V1
PIPELINE_PROFILE_SCHEMA_V1 = PIPELINE_PROFILE_V1
WORKFLOW_PREVIEW_REPRO_SCHEMA_V1 = WORKFLOW_PREVIEW_V1


def assert_parity_export_keys_stable(payload: Mapping[str, object]) -> None:
    """Raise if any required parity export v3 key is missing from a mapping."""
    missing = sorted(k for k in PARITY_EXPORT_V3_STABLE_KEYS if k not in payload)
    if missing:
        raise KeyError("parity export payload missing stable keys: " + ", ".join(missing))


def assert_parity_export_schema_version(payload: Mapping[str, object]) -> None:
    """Raise when ``parity_export_schema_version`` is not v3."""
    ver = payload.get("parity_export_schema_version")
    if ver != PARITY_EXPORT_SCHEMA_VERSION_V3:
        raise ValueError(
            f"expected parity_export_schema_version={PARITY_EXPORT_SCHEMA_VERSION_V3!r}, "
            f"got {ver!r}"
        )
