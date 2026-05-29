"""ONIOM two-layer demo: classical MM term in ``energy_components_v1``."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_example_oniom_qm_mm_demo_energy_components_mm_term() -> None:
    cfg_path = configs_path("example_oniom_qm_mm_demo.yaml")
    cfg = load_experiment_config(cfg_path)
    assert cfg.embedding.oniom_layers_v1
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    ec = out.get("energy_components")
    assert isinstance(ec, dict)
    assert ec.get("schema") == "energy_components_v1"
    mm = ec.get("classical_mm_energy_au")
    assert mm is not None and float(mm) > 0.0
    assert ec.get("oniom_mm_atom_indices") == [2, 3]
    assert ec.get("oniom_qm_atom_indices") == [0, 1]
