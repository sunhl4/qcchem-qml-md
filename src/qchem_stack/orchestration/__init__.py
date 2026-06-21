"""YAML-driven pipelines (solver bridge → pre-quantum → variational → Pauli protocol → jobs)."""

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.pipeline_runner import register_pipeline_runner
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

register_pipeline_runner(run_pipeline_sync)

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
