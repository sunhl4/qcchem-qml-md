"""ONIOM embedding energy_components contract (config + pipeline smoke)."""

from __future__ import annotations

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_from_config
from tests.helpers.paths import configs_path


def test_oniom_demo_yaml_has_layers_and_mm_charges() -> None:
    cfg = load_experiment_config(configs_path("example_oniom_qm_mm_demo.yaml"))
    assert cfg.embedding.oniom_layers_v1
    assert cfg.chemistry_extended.mm_charges is not None


def test_oniom_pipeline_emits_energy_components() -> None:
    out = run_pipeline_from_config(configs_path("example_oniom_qm_mm_demo.yaml"))
    ec = out.get("energy_components")
    assert isinstance(ec, dict)
    assert ec.get("oniom_mm_atom_indices") == [2, 3]
    assert ec.get("oniom_qm_atom_indices") == [0, 1]
