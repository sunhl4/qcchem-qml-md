"""Pipeline attaches ``energy_components_v1`` after classical mean-field (PySCF)."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_example_h2_pipeline_energy_components_schema() -> None:
    cfg_path = configs_path("example_h2.yaml")
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    ec = out.get("energy_components")
    assert isinstance(ec, dict)
    assert ec.get("schema") == "energy_components_v1"
    assert ec.get("mean_field_total_au") is not None
    nr = ec.get("nuclear_repulsion_au")
    assert nr is None or isinstance(nr, (int, float))
