"""Typed shapes for :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync` outputs.

Runtime payloads remain ``dict[str, Any]`` for forward compatibility; these TypedDicts
document stable keys for integrators, HTTP adapters, and static analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast

from qchem_stack.contracts.schema_ids import PIPELINE_RESULT_V1

if TYPE_CHECKING:
    from collections.abc import Mapping

    from qchem_stack.orchestration.excited_stages_types import ExcitedResourceSummary
    from qchem_stack.repro.schema import ParitySnapshotV1, PipelineProfileV1, RunSummaryV1


class PipelineReproV1(TypedDict, total=False):
    """``out['repro']`` block written during sync pipeline runs."""

    parity_snapshot: ParitySnapshotV1
    run_summary: RunSummaryV1
    run_context: dict[str, object]
    pipeline_profile: PipelineProfileV1
    environment: dict[str, object]


class PipelinePreQuantumSummaryV1(TypedDict, total=False):
    schema: str
    source: str
    backend_tag: str
    n_qubits: int
    reference_energy_au: float
    scf_energy_au: float
    hamiltonian_fingerprint: str
    hamiltonian_branch: str
    hamiltonian_meta: dict[str, object]
    meta: dict[str, object]


class PipelineResourceSummaryV1(TypedDict, total=False):
    n_circuits: int
    sum_shots: int
    max_depth: int
    sum_twoq: int
    n_qubits: int
    n_pauli_terms: int | None
    n_pauli_groups: int | None
    pauli_averaging_protocol_ran: bool
    excited_stages: ExcitedResourceSummary
    excited_shots_upper_bound: int
    sum_shots_total_with_excited_upper_bound: int


class PipelineJobEnqueueV1(TypedDict):
    job_id: str
    protocol_hash: str
    store: str


class PipelineResultV1(TypedDict, total=False):
    """Top-level mapping returned by ``run_pipeline_sync`` / ``run_pipeline_from_config``."""

    schema: str
    repro: PipelineReproV1
    scf_energy: float
    energy_after_variational: float
    angles: list[float]
    pre_quantum_input: PipelinePreQuantumSummaryV1
    energy_components: dict[str, object]
    hamiltonian_meta: dict[str, object]
    pre_quantum_build_cache: dict[str, object]
    classical_benchmarks: dict[str, object]
    classical_benchmark_summary: dict[str, object]
    embedding_input_system: dict[str, object]
    rdm_bundle_meta: dict[str, object]
    rdm_correction: dict[str, object]
    rdm_correction_readiness: dict[str, object]
    energy_pauli_protocol: float
    protocol_counts: dict[str, object]
    resource_rows: list[dict[str, object]]
    pauli_measurement_ledger: list[dict[str, object]]
    resource_summary: PipelineResourceSummaryV1
    excited_resource_summary: ExcitedResourceSummary
    vqd: dict[str, object]
    qse: dict[str, object]
    sceom: dict[str, object]
    embedding_workflow: dict[str, object]
    job: PipelineJobEnqueueV1
    job_result: dict[str, object]
    methods_sidecar: dict[str, object]
    nfev: NotRequired[int]
    algorithm: NotRequired[str]


PIPELINE_RESULT_CORE_KEYS: frozenset[str] = frozenset(
    {
        "repro",
        "scf_energy",
        "energy_after_variational",
        "angles",
        "pre_quantum_input",
        "energy_components",
        "hamiltonian_meta",
        "pre_quantum_build_cache",
    }
)


def pipeline_result_schema_tag() -> str:
    """Canonical schema id for pipeline sync outputs."""
    return PIPELINE_RESULT_V1


def assert_pipeline_result_core_keys(payload: Mapping[str, object]) -> None:
    """Raise if any required pipeline result key is missing."""
    missing = sorted(k for k in PIPELINE_RESULT_CORE_KEYS if k not in payload)
    if missing:
        raise KeyError("pipeline result payload missing core keys: " + ", ".join(missing))


def tag_pipeline_result(payload: PipelineResultV1 | dict[str, Any]) -> PipelineResultV1:
    """Attach ``schema: pipeline_result_v1`` without mutating nested structures."""
    tagged = dict(payload)
    tagged.setdefault("schema", PIPELINE_RESULT_V1)
    return cast("PipelineResultV1", tagged)


__all__ = [
    "PIPELINE_RESULT_CORE_KEYS",
    "PipelineJobEnqueueV1",
    "PipelinePreQuantumSummaryV1",
    "PipelineReproV1",
    "PipelineResourceSummaryV1",
    "PipelineResultV1",
    "assert_pipeline_result_core_keys",
    "pipeline_result_schema_tag",
    "tag_pipeline_result",
]
