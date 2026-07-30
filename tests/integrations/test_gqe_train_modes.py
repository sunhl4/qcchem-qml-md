"""Tests for GQE train_mode: gpt / prefill / condition."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.config import GqeSpec, load_experiment_config
from qchem_stack.config.gqe_helpers import gqe_train_overrides
from qchem_stack.contracts.schema_ids import GQE_TRAIN_REPORT_V1

REPO = Path(__file__).resolve().parents[2]
YAML_PLAN_B = REPO / "configs" / "example_h2_gqe_plan_b.yaml"
YAML_PREFILL = REPO / "configs" / "example_h2_gqe_prefill.yaml"
YAML_CONDITION = REPO / "configs" / "example_h2_gqe_condition.yaml"
YAML_GPT = REPO / "configs" / "example_h2_gqe_gpt.yaml"


def test_train_mode_in_spec_and_helpers() -> None:
    assert GqeSpec().train_mode == "gpt"
    cfg = load_experiment_config(YAML_PREFILL)
    assert cfg.gqe.train_mode == "prefill"
    ov = gqe_train_overrides(cfg)
    assert ov["train_mode"] == "prefill"
    assert ov["warmup_samples"] == 64


def test_condition_yaml_parses() -> None:
    cfg = load_experiment_config(YAML_CONDITION)
    assert cfg.gqe.train_mode == "condition"
    assert cfg.gqe.condition_bonds == [0.74, 1.0, 1.5]
    ov = gqe_train_overrides(cfg)
    assert ov["condition_bonds"] == [0.74, 1.0, 1.5]


@pytest.mark.gqe
def test_prefill_mode_warmup_only() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("optax")
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.executor_base import StatevectorHeaExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.integrations.gqe.native.cost_bridge import make_gqe_cost
    from qchem_stack.integrations.gqe.native.operator_pool import build_gqe_operator_pool
    from qchem_stack.integrations.gqe.native.paper_trainer import (
        PaperTrainConfig,
        run_paper_gqe_loop,
    )

    ham = QubitHamiltonian(
        operator=QubitOperator("Z0", 0.5) + QubitOperator("Z1", 0.5),
        n_qubits=2,
        fermion_space=None,
    )
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=True
    )
    cost = make_gqe_cost(StatevectorHeaExecutor(), ham.operator, pool)
    warmup = 12
    result = run_paper_gqe_loop(
        cost,
        pool,
        config=PaperTrainConfig(
            seq_len=2,
            n_epochs=50,  # must be ignored in prefill
            n_sample=20,
            warmup_samples=warmup,
            buffer_max=32,
            d_model=16,
            n_layers=1,
            train_mode="prefill",
            seed=1,
        ),
    )
    assert result.report["train_mode"] == "prefill"
    assert result.n_energy_evals == warmup
    assert len(result.history) == 1
    assert result.history[0]["phase"] == "prefill"
    assert np.isfinite(result.best_energy)


@pytest.mark.gqe
def test_run_gqe_prefill_from_config() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("optax")
    from qchem_stack.integrations.gqe import run_gqe_from_config

    report = run_gqe_from_config(YAML_PREFILL)
    assert report["schema"] == GQE_TRAIN_REPORT_V1
    assert report["train_mode"] == "prefill"
    assert report["n_energy_evals"] == 64
    assert np.isfinite(report["best_energy"])


@pytest.mark.gqe
def test_run_gqe_condition_from_config() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("optax")
    from qchem_stack.integrations.gqe import run_gqe_from_config

    report = run_gqe_from_config(YAML_CONDITION)
    assert report["schema"] == GQE_TRAIN_REPORT_V1
    assert report["train_mode"] == "condition"
    assert report["plan"] == "B-condition"
    assert report["n_energy_evals"] > 0
    assert np.isfinite(report["best_energy"])
    assert report.get("config", {}).get("bonds") == [0.74, 1.0, 1.5]


@pytest.mark.gqe
def test_gpt_yaml_still_runs() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("optax")
    from qchem_stack.integrations.gqe import run_gqe_from_config

    report = run_gqe_from_config(YAML_GPT)
    assert report["train_mode"] == "gpt"
    assert report["n_energy_evals"] > report["config"]["warmup_samples"]
    assert len(report["history"]) == 5
