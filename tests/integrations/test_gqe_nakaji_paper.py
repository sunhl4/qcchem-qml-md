"""Nakaji GPT-QE paper-faithful components (arXiv:2401.09253)."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.integrations.gqe.native.cost_bridge import make_gqe_cost
from qchem_stack.integrations.gqe.native.paper_losses import DispersionBetaState
from qchem_stack.integrations.gqe.native.paper_pool import (
    verify_paper_unitary,
)
from qchem_stack.integrations.gqe.native.paper_spec import (
    PAPER_TIME_GRID,
    paper_reproduction_checklist,
)
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation


def _toy_ham(n: int = 2) -> QubitHamiltonian:
    op = QubitOperator("Z0", 0.5) + QubitOperator("Z1", 0.5) + QubitOperator("X0 X1", 0.2)
    return QubitHamiltonian(operator=op, n_qubits=n, fermion_space=None)


def test_paper_checklist_keys() -> None:
    c = paper_reproduction_checklist()
    assert c["paper"] == "arXiv:2401.09253"
    assert "B1_logit_matching" in c["targets"]


def test_dispersion_beta_schedule() -> None:
    st = DispersionBetaState(beta=1.0, alpha=0.02, tau_disp=1e-5)
    b1 = st.update([0.0, 1.0, 2.0])
    assert b1 > 1.0
    st.beta = 1.0
    b2 = st.update([1.0, 1.0, 1.0])
    assert b2 < 1.0


def test_paper_time_grid_matches_appendix() -> None:
    assert len(PAPER_TIME_GRID) == 12
    assert abs(PAPER_TIME_GRID[0] - 1 / 320) < 1e-15
    assert abs(PAPER_TIME_GRID[5] - 32 / 320) < 1e-15
    assert abs(PAPER_TIME_GRID[6] + 1 / 320) < 1e-15


@pytest.mark.skipif(
    not probe_gqe_jax_installation().get("available"),
    reason="jax+optax not installed",
)
def test_paper_loop_smoke_toy(tmp_path) -> None:
    from qchem_stack.integrations.gqe.native.operator_pool import build_gqe_operator_pool
    from qchem_stack.integrations.gqe.native.paper_trainer import (
        PaperTrainConfig,
        run_paper_gqe_loop,
    )

    ham = _toy_ham(2)
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=True
    )
    exe = StatevectorHeaExecutor()
    cost = make_gqe_cost(exe, ham.operator, pool)
    result = run_paper_gqe_loop(
        cost,
        pool,
        config=PaperTrainConfig(
            seq_len=2,
            n_epochs=2,
            n_sample=4,
            n_batch=4,
            n_iter=1,
            buffer_max=32,
            warmup_samples=8,
            d_model=16,
            n_layers=1,
            loss_mode="grpo",
            seed=0,
            checkpoint_dir=str(tmp_path / "ckpt"),
            checkpoint_every=1,
            log_every=1,
        ),
        reference_energy=-1.0,
    )
    assert np.isfinite(result.best_energy)
    assert result.report["plan"] == "B-paper"
    assert len(result.history) == 2
    latest = tmp_path / "ckpt" / "checkpoint_latest.json"
    assert latest.is_file()
    import json

    payload = json.loads(latest.read_text(encoding="utf-8"))
    assert payload["epoch"] == 2
    assert "best_energy" in payload


@pytest.mark.pyscf
def test_paper_pool_h2_and_problem() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.integrations.gqe.native.paper_molecules import build_paper_gqe_problem

    pb = build_paper_gqe_problem("h2", bond_length_angstrom=0.74, compute_fci=True)
    assert pb.n_qubits == 4
    assert pb.fci_energy is not None
    assert pb.scf_energy is not None
    assert abs(pb.cost_fn([]) - float(pb.scf_energy)) < 1e-6
    # |T|=12 time values (+ identity)
    assert len(set(pb.pool.angles) - {0.0}) == 12
    assert pb.pool.vocab_size > 12
    assert verify_paper_unitary(pb.pool, min(5, pb.pool.vocab_size - 1))
    # paper pool should be able to go below HF with some token
    best = float(pb.scf_energy)
    for i in range(1, pb.pool.vocab_size):
        best = min(best, float(pb.cost_fn([i])))
    assert best < float(pb.scf_energy) - 1e-4
