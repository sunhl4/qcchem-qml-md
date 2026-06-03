"""Mutable context passed through registry-driven ``run_pipeline_sync`` stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.config import ExperimentConfig
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.orchestration.pipeline_result import PipelineResultV1


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
    job_timeline_emit: Callable[[dict[str, Any]], None] | None
    collect_repro_metadata_fn: Callable[..., dict[str, Any]]
    stage_completion_data: dict[str, Any] = field(default_factory=dict)
    rhf: Any = None
    qh: QubitHamiltonian | None = None
    pre_q_input: Any = None
    schmidt_ctx: Any = None
    angles: Any = None
    energy_pre: float = 0.0
    energy_components: Any = None
    embedding_input_payload: Any = None
    classical_benchmarks: dict[str, Any] | None = None
    rdm_bundle_meta: dict[str, Any] | None = None
    rdm_correction_report: Any = None
    rdm_correction_readiness: Any = None
    repro: dict[str, Any] = field(default_factory=dict)
    bspec: Any = None
    exe: Any = None
    bundle: Any = None
    out: dict[str, Any] = field(default_factory=dict)
    excited_rs: Any = None
    result: PipelineResultV1 | None = None
