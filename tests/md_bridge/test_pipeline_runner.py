"""Registry for injectable pipeline runners (md_bridge layer boundary)."""

from __future__ import annotations

import pytest

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.pipeline_runner import (
    register_pipeline_runner,
    reset_pipeline_runner,
    resolve_pipeline_runner,
)


def test_resolve_pipeline_runner_requires_registration() -> None:
    reset_pipeline_runner()
    with pytest.raises(PipelineError, match="No pipeline runner registered"):
        resolve_pipeline_runner()


def test_register_and_resolve_pipeline_runner() -> None:
    reset_pipeline_runner()

    def _mock_runner(*args: object, **kwargs: object) -> dict[str, object]:
        return {"ok": True}

    register_pipeline_runner(_mock_runner)
    assert resolve_pipeline_runner() is _mock_runner
    assert resolve_pipeline_runner(_mock_runner) is _mock_runner
    reset_pipeline_runner()
    import qchem_stack.orchestration  # noqa: F401 — restore default runner
