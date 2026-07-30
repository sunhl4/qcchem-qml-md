"""Stable GQE API + GqeSpec config contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig, GqeSpec, load_experiment_config
from qchem_stack.config.gqe_helpers import (
    gqe_enabled,
    gqe_model_sizes,
    gqe_repro_fields,
    gqe_skip_variational,
    gqe_train_overrides,
)
from qchem_stack.contracts.schema_ids import GQE_TRAIN_REPORT_V1

REPO = Path(__file__).resolve().parents[2]
YAML = REPO / "configs" / "example_h2_gqe_plan_b.yaml"


def test_gqe_spec_forbid_extra() -> None:
    with pytest.raises(ValidationError):
        GqeSpec.model_validate({"enabled": False, "not_a_field": 1})


def test_gqe_helpers_from_example_yaml() -> None:
    cfg = load_experiment_config(YAML)
    assert gqe_enabled(cfg) is True
    assert gqe_skip_variational(cfg) is True
    assert cfg.gqe.mode == "paper"
    assert cfg.gqe.molecule == "h2"
    ov = gqe_train_overrides(cfg)
    assert ov["loss_mode"] == "grpo"
    assert ov["n_epochs"] == 5
    d_model, n_layers = gqe_model_sizes(cfg)
    assert d_model == 32 and n_layers == 2
    fields = gqe_repro_fields(cfg)
    assert fields["gqe_enabled_yaml"] is True
    assert fields["gqe_mode_yaml"] == "paper"


def test_gqe_paper_model_sizes() -> None:
    g = GqeSpec(enabled=True, paper_model=True, d_model=16, n_layers=1)
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "gqe_size",
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "gqe": g.model_dump(),
        }
    )
    assert gqe_model_sizes(cfg) == (192, 6)


@pytest.mark.gqe
def test_run_gqe_from_config_smoke() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("optax")
    from qchem_stack.integrations.gqe import run_gqe_from_config

    report = run_gqe_from_config(YAML)
    assert report["schema"] == GQE_TRAIN_REPORT_V1
    assert report["gqe_mode"] == "paper"
    assert report.get("paper") == "arXiv:2401.09253"
    assert isinstance(report["best_energy"], float)
    assert report["n_energy_evals"] > 0
    assert "best_sequence" in report
