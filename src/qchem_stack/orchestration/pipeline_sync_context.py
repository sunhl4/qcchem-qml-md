"""Mutable context passed through registry-driven ``run_pipeline_sync`` stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.config import ExperimentConfig
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import numpy as np

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.pre_quantum_input import PreQuantumInput
    from qchem_stack.orchestration.excited_stages_types import ExcitedResourceSummary
    from qchem_stack.orchestration.pipeline_result import PipelineResultV1

    AnglesLike = np.ndarray | list[float]


@dataclass
class PipelineSyncContext:
    """In-process pipeline state threaded across stage runners."""

    cfg: ExperimentConfig
    cfg_path: Path | None
    profile: PipelineStageTimer
    build_cache: RunBuildCache
    trace_id: str | None
    run_context: RunContext | None
    hamiltonian_out: list[QubitHamiltonian] | None
    job_timeline_emit: Callable[[dict[str, object]], None] | None
    collect_repro_metadata_fn: Callable[..., dict[str, object]]
    stage_completion_data: dict[str, object] = field(default_factory=dict)
    rhf: ClassicalMeanFieldReference | None = None
    qh: QubitHamiltonian | None = None
    pre_q_input: PreQuantumInput | None = None
    schmidt_ctx: dict[str, object] | None = None
    angles: AnglesLike | None = None
    energy_pre: float = 0.0
    energy_components: dict[str, object] | None = None
    embedding_input_payload: dict[str, object] | None = None
    classical_benchmarks: dict[str, object] | None = None
    rdm_bundle_meta: dict[str, object] | None = None
    rdm_correction_report: dict[str, object] | None = None
    rdm_correction_readiness: dict[str, object] | None = None
    repro: dict[str, object] = field(default_factory=dict)
    bspec: BackendSpec | None = None
    exe: HamiltonianExpectationExecutor | None = None
    bundle: CompilerPassBundle | None = None
    out: dict[str, object] = field(default_factory=dict)
    excited_rs: ExcitedResourceSummary | None = None
    result: PipelineResultV1 | None = None
