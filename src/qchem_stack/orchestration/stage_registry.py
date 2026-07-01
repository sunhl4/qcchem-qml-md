"""Named pipeline stages, lifecycle events, and registry-driven stage runners."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from qchem_stack.orchestration.pipeline_events import PipelineEvents
from qchem_stack.orchestration.pipeline_stage_runners import (
    bind_post_pre_quantum_ctx,
    run_embedding_workflow_stage_ctx,
    run_excited_stage_ctx,
    run_pre_quantum_stage_ctx,
    run_protocol_finalize_stage_ctx,
    run_scf_stage_ctx,
    run_variational_stage_ctx,
)
from qchem_stack.orchestration.pipeline_sync_context import PipelineSyncContext

StageName = Literal[
    "pipeline",
    "scf",
    "pre_quantum",
    "variational",
    "embedding_workflow",
    "excited",
    "protocol_finalize",
]


@dataclass(frozen=True)
class StageLifecycle:
    """Start/complete/failed events emitted around a pipeline stage."""

    name: StageName
    started: str
    completed: str
    failed: str


@dataclass(frozen=True)
class StageSpec:
    """One pipeline stage: lifecycle events plus context mutator."""

    name: StageName
    lifecycle: StageLifecycle
    run: Callable[[PipelineSyncContext], None]
    post_run: Callable[[PipelineSyncContext], None] | None = None


PIPELINE_STAGE_LIFECYCLES: tuple[StageLifecycle, ...] = (
    StageLifecycle(
        "scf",
        PipelineEvents.SCF_STARTED,
        PipelineEvents.SCF_COMPLETED,
        PipelineEvents.SCF_FAILED,
    ),
    StageLifecycle(
        "pre_quantum",
        PipelineEvents.PRE_QUANTUM_STARTED,
        PipelineEvents.PRE_QUANTUM_COMPLETED,
        PipelineEvents.PRE_QUANTUM_FAILED,
    ),
    StageLifecycle(
        "variational",
        PipelineEvents.VARIATIONAL_STARTED,
        PipelineEvents.VARIATIONAL_COMPLETED,
        PipelineEvents.VARIATIONAL_FAILED,
    ),
    StageLifecycle(
        "embedding_workflow",
        PipelineEvents.EMBEDDING_WORKFLOW_STARTED,
        PipelineEvents.EMBEDDING_WORKFLOW_COMPLETED,
        PipelineEvents.EMBEDDING_WORKFLOW_FAILED,
    ),
    StageLifecycle(
        "excited",
        PipelineEvents.EXCITED_STARTED,
        PipelineEvents.EXCITED_COMPLETED,
        PipelineEvents.EXCITED_FAILED,
    ),
    StageLifecycle(
        "protocol_finalize",
        PipelineEvents.PROTOCOL_FINALIZE_STARTED,
        PipelineEvents.PROTOCOL_FINALIZE_COMPLETED,
        PipelineEvents.PROTOCOL_FINALIZE_FAILED,
    ),
)

PIPELINE_WRAPPER_LIFECYCLE = StageLifecycle(
    "pipeline",
    PipelineEvents.PIPELINE_STARTED,
    PipelineEvents.PIPELINE_COMPLETED,
    PipelineEvents.PIPELINE_FAILED,
)

PIPELINE_STAGE_SPECS: tuple[StageSpec, ...] = (
    StageSpec(
        "scf",
        PIPELINE_STAGE_LIFECYCLES[0],
        run_scf_stage_ctx,
    ),
    StageSpec(
        "pre_quantum",
        PIPELINE_STAGE_LIFECYCLES[1],
        run_pre_quantum_stage_ctx,
        post_run=bind_post_pre_quantum_ctx,
    ),
    StageSpec(
        "variational",
        PIPELINE_STAGE_LIFECYCLES[2],
        run_variational_stage_ctx,
    ),
    StageSpec(
        "embedding_workflow",
        PIPELINE_STAGE_LIFECYCLES[3],
        run_embedding_workflow_stage_ctx,
    ),
    StageSpec(
        "excited",
        PIPELINE_STAGE_LIFECYCLES[4],
        run_excited_stage_ctx,
    ),
    StageSpec(
        "protocol_finalize",
        PIPELINE_STAGE_LIFECYCLES[5],
        run_protocol_finalize_stage_ctx,
    ),
)
