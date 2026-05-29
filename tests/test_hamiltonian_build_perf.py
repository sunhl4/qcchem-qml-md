"""Soft performance guard for JW Hamiltonian build (local / nightly)."""

from __future__ import annotations

import time

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.paths import configs_path


@pytest.mark.perf
@pytest.mark.pyscf
def test_h2_hamiltonian_build_wall_time_soft_cap() -> None:
    pytest.importorskip("pyscf")
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    t0 = time.perf_counter()
    run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"))
    elapsed = time.perf_counter() - t0
    assert elapsed < 120.0
