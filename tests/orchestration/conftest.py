"""Shared fixtures for orchestration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from qchem_stack.config import ExperimentConfig
from qchem_stack.orchestration.pipeline_sync_context import PipelineSyncContext
from qchem_stack.orchestration.run_context import PipelineStageTimer
from tests.helpers.h2_yaml import h2_yaml_dict

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def make_pipeline_context() -> Callable[..., PipelineSyncContext]:
    """Factory fixture that creates a ``PipelineSyncContext`` with sensible defaults.

    Keyword arguments override the default field values.
    """

    def _factory(**overrides: Any) -> PipelineSyncContext:
        defaults: dict[str, Any] = dict(
            cfg=ExperimentConfig.model_validate(h2_yaml_dict()),
            cfg_path=None,
            profile=PipelineStageTimer(),
            build_cache=MagicMock(),
            trace_id="trace-test",
            run_context=None,
            hamiltonian_out=None,
            job_timeline_emit=None,
            collect_repro_metadata_fn=MagicMock(return_value={}),
            repro={"run_summary": {}},
        )
        defaults.update(overrides)
        return PipelineSyncContext(**defaults)

    return _factory
