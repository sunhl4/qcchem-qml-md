"""Additive GQE integration smoke tests (Plan B native core)."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.integrations.gqe import (
    gqe_integration_blueprint,
    probe_cudaq_solvers_installation,
    probe_gqe_jax_installation,
)
from qchem_stack.integrations.gqe.cudaq_adapter import describe_cudaq_gqe_adapter
from qchem_stack.integrations.gqe.native import (
    CHEMICAL_ACCURACY_HARTREE,
    BetaSchedule,
    apply_pool_sequence,
    build_gqe_operator_pool,
    chemical_accuracy_report,
    make_gqe_cost,
    make_gqe_oracle,
    reweight_dataset_energies,
    run_random_baseline,
)
from qchem_stack.integrations.gqe.native.pauli_features import (
    hamiltonian_coefficients,
    pauli_basis_from_hamiltonian,
)
from qchem_stack.integrations.gqe.native.trainer import _mix_replay_batch


def _toy_h2_like_hamiltonian(n_qubits: int = 2) -> QubitHamiltonian:
    # Minimal 2-qubit Ising-like H for unit tests (no PySCF).
    op = QubitOperator("Z0", 0.5) + QubitOperator("Z1", 0.5) + QubitOperator("X0 X1", 0.2)
    return QubitHamiltonian(operator=op, n_qubits=n_qubits, fermion_space=None)


def test_gqe_blueprint_plan_b() -> None:
    bp = gqe_integration_blueprint()
    assert bp["plan"] == "B"
    assert "native" in bp["modules"]
    assert bp["schema"].startswith("gqe_")


def test_probes_never_raise() -> None:
    jax_probe = probe_gqe_jax_installation()
    cudaq_probe = probe_cudaq_solvers_installation()
    assert "available" in jax_probe
    assert "available" in cudaq_probe
    assert describe_cudaq_gqe_adapter()["recommended_native_entry"].endswith("run_gqe_lm_loop")


def test_operator_pool_and_cost_bridge_random_baseline() -> None:
    ham = _toy_h2_like_hamiltonian(2)
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=False
    )
    assert pool.vocab_size >= 1
    exe = StatevectorHeaExecutor()
    cost = make_gqe_cost(exe, ham.operator, pool, n_electrons=None)
    e0 = cost([])
    assert np.isfinite(e0)
    seq = [0] * min(2, pool.vocab_size)
    e1 = cost(seq)
    assert np.isfinite(e1)
    ref = np.zeros(2**pool.n_qubits, dtype=np.complex128)
    ref[0] = 1.0
    st = apply_pool_sequence(pool, seq, ref)
    assert st.shape == (2**pool.n_qubits,)
    assert abs(np.linalg.norm(st) - 1.0) < 1e-10

    report = run_random_baseline(cost, pool, seq_len=2, n_samples=8, seed=0)
    assert report["plan"] == "B-baseline"
    assert np.isfinite(report["best_energy"])
    assert len(report["best_sequence"]) == 2


def test_mix_replay_batch_includes_replay_entries() -> None:
    rng = np.random.default_rng(0)
    epoch_seqs = [np.array([0, 1], dtype=np.int32), np.array([1, 0], dtype=np.int32)]
    epoch_energies = [1.0, 2.0]
    replay = [
        {
            "candidate": {"token_sequence": [0, 0]},
            "labels": {"energy_hartree": -1.0},
        }
    ]
    toks, ens = _mix_replay_batch(
        epoch_seqs=epoch_seqs,
        epoch_energies=epoch_energies,
        replay=replay,
        mix_fraction=0.5,
        seq_len=2,
        rng=rng,
    )
    assert toks.shape[0] == 2
    assert -1.0 in ens.tolist()


def test_beta_schedule_linear_and_chemical_accuracy() -> None:
    sched = BetaSchedule(kind="linear", beta_start=1.0, beta_end=10.0)
    assert abs(sched.value(0, 5) - 1.0) < 1e-12
    assert abs(sched.value(4, 5) - 10.0) < 1e-12
    mid = sched.value(2, 5)
    assert 1.0 < mid < 10.0

    exp = BetaSchedule(kind="exponential", beta_start=1.0, beta_end=16.0)
    assert abs(exp.value(0, 5) - 1.0) < 1e-12
    assert abs(exp.value(4, 5) - 16.0) < 1e-12

    rep = chemical_accuracy_report(
        best_energy=-1.137,
        reference_energy=-1.1375,
        scf_energy=-1.1167,
    )
    assert rep["within_chemical_accuracy"] is True
    assert float(rep["abs_error_hartree"]) < CHEMICAL_ACCURACY_HARTREE
    assert "correlation_captured" in rep


def test_pauli_reweight_matches_direct_energy() -> None:
    ham = _toy_h2_like_hamiltonian(2)
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=False
    )
    exe = StatevectorHeaExecutor()
    oracle = make_gqe_oracle(exe, ham.operator, pool, store_pauli_features=True)
    rec = oracle([0, 0])
    assert "pauli_features" in rec
    feats = rec["pauli_features"]
    assert abs(feats["energy_from_features"] - rec["labels"]["energy_hartree"]) < 1e-8

    # Reweight with same H → same energy
    basis = pauli_basis_from_hamiltonian(ham.operator)
    identity, h = hamiltonian_coefficients(ham.operator, basis)
    rew = reweight_dataset_energies([rec], identity_coeff=identity, h_coeffs=h)
    assert abs(rew[0]["labels"]["energy_hartree"] - rec["labels"]["energy_hartree"]) < 1e-10

    # Different coefficients → different energy
    h2 = h * 0.5
    rew2 = reweight_dataset_energies([rec], identity_coeff=identity, h_coeffs=h2)
    assert abs(rew2[0]["labels"]["energy_hartree"] - rec["labels"]["energy_hartree"]) > 1e-6


@pytest.mark.skipif(
    not probe_gqe_jax_installation().get("available"),
    reason="jax+optax not installed",
)
@pytest.mark.parametrize("loss_mode", ["lm", "grpo"])
def test_native_jax_lm_loop_smoke(loss_mode: str) -> None:
    from qchem_stack.integrations.gqe.native import GQETrainConfig, run_gqe_lm_loop

    ham = _toy_h2_like_hamiltonian(2)
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=False
    )
    exe = StatevectorHeaExecutor()
    cost = make_gqe_cost(exe, ham.operator, pool)
    result = run_gqe_lm_loop(
        cost,
        pool,
        config=GQETrainConfig(
            seq_len=2,
            n_epochs=1,
            samples_per_epoch=4,
            d_model=16,
            n_layers=1,
            seed=0,
            loss_mode=loss_mode,  # type: ignore[arg-type]
            replay_mix_fraction=0.25,
            beta_schedule=BetaSchedule(kind="linear", beta_start=1.0, beta_end=5.0),
        ),
        reference_energy=-1.0,
        scf_energy=0.0,
    )
    assert np.isfinite(result.best_energy)
    assert result.report["plan"] == "B"
    assert result.report["config"]["loss_mode"] == loss_mode
    assert result.report["config"]["beta_schedule"] is not None
    assert "chemical_accuracy" in result.report
    assert len(result.history) == 1
    assert "beta" in result.history[0]


@pytest.mark.skipif(
    not probe_gqe_jax_installation().get("available"),
    reason="jax+optax not installed",
)
def test_pretrain_on_oracle_dataset() -> None:
    from qchem_stack.integrations.gqe.native import GQETrainConfig, run_gqe_lm_loop

    ham = _toy_h2_like_hamiltonian(2)
    pool = build_gqe_operator_pool(
        ham, pool_id="toy_pair_xx", default_angle=0.05, include_identity=False
    )
    exe = StatevectorHeaExecutor()
    cost = make_gqe_cost(exe, ham.operator, pool)
    oracle = make_gqe_oracle(exe, ham.operator, pool, store_pauli_features=True)
    # toy_pair_xx has vocab_size=1 on 2-qubit H; keep fixed seq_len=2
    dataset = [oracle([0, 0]), oracle([0, 0]), oracle([0, 0])]
    result = run_gqe_lm_loop(
        cost,
        pool,
        config=GQETrainConfig(
            seq_len=2,
            n_epochs=1,
            samples_per_epoch=2,
            d_model=16,
            n_layers=1,
            seed=1,
            pretrain_epochs=2,
            loss_mode="lm",
        ),
        oracle_fn=oracle,
        pretrain_dataset=dataset,
    )
    assert len(result.report["pretrain_history"]) == 2
    assert np.isfinite(result.best_energy)


@pytest.mark.pyscf
def test_build_gqe_problem_from_h2_config() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.integrations.gqe.native import build_gqe_problem_from_config
    from tests.helpers.paths import configs_path

    cfg = configs_path("example_h2_gqe_plan_b.yaml")
    if not cfg.is_file():
        pytest.skip(f"missing {cfg}")
    bundle = build_gqe_problem_from_config(
        cfg, pool_id="fermionic_uccsd", default_angle=0.1, compute_fci=True
    )
    assert bundle.n_qubits >= 2
    assert bundle.pool.vocab_size >= 1
    assert bundle.scf_energy is not None
    assert bundle.fci_energy is not None
    assert bundle.fci_energy < bundle.scf_energy + 1e-6
    e_ref = bundle.cost_fn([])
    assert np.isfinite(e_ref)
    # HF reference energy should be near SCF (active-space H expectation)
    assert abs(e_ref - bundle.scf_energy) < 0.05
    baseline = run_random_baseline(bundle.cost_fn, bundle.pool, seq_len=2, n_samples=4, seed=1)
    assert np.isfinite(baseline["best_energy"])
    rec = bundle.oracle_fn([0])
    assert "pauli_features" in rec


@pytest.mark.pyscf
def test_h2_angle_grid_reaches_chemical_accuracy_random() -> None:
    """With correct UCCSD convention + angle grid, random search hits chem. accuracy."""
    pytest.importorskip("pyscf")
    from qchem_stack.integrations.gqe.native import (
        CHEMICAL_ACCURACY_HARTREE,
        build_gqe_problem_from_config,
        run_random_baseline,
    )
    from tests.helpers.paths import configs_path

    cfg = configs_path("example_h2_gqe_plan_b.yaml")
    if not cfg.is_file():
        pytest.skip(f"missing {cfg}")
    bundle = build_gqe_problem_from_config(
        cfg,
        pool_id="fermionic_uccsd",
        angle_grid=(-0.3, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.3),
        compute_fci=True,
    )
    assert bundle.fci_energy is not None
    # L=1 exhaustive over vocab is enough (double excitation ~0.1)
    best = float("inf")
    for i in range(bundle.pool.vocab_size):
        best = min(best, float(bundle.cost_fn([i])))
    assert abs(best - bundle.fci_energy) <= CHEMICAL_ACCURACY_HARTREE

    baseline = run_random_baseline(bundle.cost_fn, bundle.pool, seq_len=1, n_samples=200, seed=0)
    # Random search should at least beat SCF and approach FCI
    assert baseline["best_energy"] < bundle.scf_energy - 0.01
    assert abs(baseline["best_energy"] - bundle.fci_energy) < 0.01


@pytest.mark.pyscf
def test_bond_scan_reweight_transfer() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.integrations.gqe.native import (
        build_gqe_problems_bond_scan,
        transfer_dataset_to_bundle,
    )
    from tests.helpers.paths import configs_path

    cfg = configs_path("example_h2_gqe_plan_b.yaml")
    if not cfg.is_file():
        pytest.skip(f"missing {cfg}")
    bundles = build_gqe_problems_bond_scan(
        cfg,
        bond_lengths_bohr=[1.2, 1.4],
        pool_id="fermionic_uccsd",
        default_angle=0.1,
    )
    assert len(bundles) == 2
    src, tgt = bundles[0], bundles[1]
    # Same active-space size → same Pauli labels for H2 sto-3g CAS(2,2)
    rec = src.oracle_fn([0, 1])
    transferred = transfer_dataset_to_bundle([rec], tgt)
    e_direct = float(tgt.cost_fn(rec["candidate"]["token_sequence"]))
    e_rew = float(transferred[0]["labels"]["energy_hartree"])
    # Reweighting uses source-state Pauli expectations with target coeffs —
    # not equal to applying the same circuit under target H (different HF ref /
    # orbitals). Just check finite + marked reweighted.
    assert np.isfinite(e_rew)
    assert transferred[0]["labels"].get("reweighted") is True
    assert np.isfinite(e_direct)
