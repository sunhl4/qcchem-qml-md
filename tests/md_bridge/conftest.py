"""Shared fixtures for md_bridge tests."""

from __future__ import annotations

import pytest

import qchem_stack.orchestration  # noqa: F401 — registers default pipeline runner


@pytest.fixture(autouse=True)
def _ensure_pipeline_runner_registered() -> None:
    """Re-register after tests that call ``reset_pipeline_runner()``."""
    from qchem_stack.md_bridge.pipeline_runner import register_pipeline_runner
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    register_pipeline_runner(run_pipeline_sync)
