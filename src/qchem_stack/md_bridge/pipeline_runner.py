"""Injectable pipeline runner registry (avoids md_bridge -> orchestration imports)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qchem_stack.exceptions import PipelineError

PipelineRunner = Callable[..., Any]

_RUNNER: PipelineRunner | None = None


def register_pipeline_runner(fn: PipelineRunner) -> None:
    """Register the default in-process pipeline runner (called from orchestration)."""
    global _RUNNER
    _RUNNER = fn


def reset_pipeline_runner() -> None:
    """Clear registry (tests only)."""
    global _RUNNER
    _RUNNER = None


def resolve_pipeline_runner(override: PipelineRunner | None = None) -> PipelineRunner:
    """Return explicit override or the registered default runner."""
    if override is not None:
        return override
    if _RUNNER is None:
        raise PipelineError(
            "No pipeline runner registered. Import qchem_stack.orchestration.pipeline "
            "or pass pipeline_runner= explicitly."
        )
    return _RUNNER


__all__ = [
    "PipelineRunner",
    "register_pipeline_runner",
    "reset_pipeline_runner",
    "resolve_pipeline_runner",
]
