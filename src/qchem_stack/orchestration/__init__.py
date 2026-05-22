"""YAML-driven pipelines (solver bridge → pre-quantum → variational → Pauli protocol → jobs)."""

from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline import (
    collect_repro_metadata,
    run_pipeline_from_config,
    run_pipeline_sync,
)
from qchem_stack.orchestration.pipeline_result import (
    PipelineResultV1,
    assert_pipeline_result_core_keys,
    tag_pipeline_result,
)
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext
from qchem_stack.orchestration.workflow import WorkflowCoordinator

__all__ = [
    "PipelineError",
    "PipelineResultV1",
    "PipelineStageTimer",
    "RunContext",
    "WorkflowCoordinator",
    "assert_pipeline_result_core_keys",
    "collect_repro_metadata",
    "run_pipeline_from_config",
    "run_pipeline_sync",
    "tag_pipeline_result",
]
