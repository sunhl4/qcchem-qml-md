"""Main config tree runs ``quantum.algorithm: qpe_kitaev`` without demo-track sidecar."""

from __future__ import annotations

import math

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.quantum.variational_plugins.registry import is_registered_variational_id


def test_qpe_kitaev_registered_in_variational_registry() -> None:
    assert is_registered_variational_id("qpe_kitaev")


def test_example_h2_qpe_main_pipeline_without_demo_track() -> None:
    cfg_path = configs_path("example_h2_qpe_main.yaml")
    cfg = load_experiment_config(cfg_path)
    assert cfg.quantum.algorithm == "qpe_kitaev"
    assert cfg.quantum.demos.qpe.track_after_variational is False
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert out.get("algorithm") == "qpe_kitaev"
    e = float(out["energy_after_variational"])
    assert math.isfinite(e)
    assert "qpe_demo_track" not in out
    report = out.get("algorithm_report")
    assert isinstance(report, dict)
    assert report.get("schema") == "algorithm_kitaev_qpe_report_v1"
