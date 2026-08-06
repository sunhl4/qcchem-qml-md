"""Unit tests for GQE family (peer algorithms to VQE; Yaozheng GQE review A1–A8)."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec, SCFSpec
from qchem_stack.quantum.algorithms.gqe import (
    VARIANT_TO_CLASS,
    AdaptGQE,
    AugerGQE,
    ConditionalGQE,
    GQE,
    GQEConfig,
    GQKAE,
    PersistentDPOGQE,
    QSCIGQE,
    SmilesTransferGQE,
    SpinGQE,
)
from qchem_stack.quantum.algorithms.gqe.pool import build_gqe_pool
from qchem_stack.quantum.variational_plugins.registry import (
    is_registered_variational_id,
    list_registered_variational_ids,
)


def _toy_h2_like() -> QubitHamiltonian:
    # Minimal 2-qubit Ising-like Hamiltonian with known ground energy -1.
    op = QubitOperator(((0, "Z"),), 0.5) + QubitOperator(((1, "Z"),), 0.5)
    op += QubitOperator(((0, "X"), (1, "X")), -1.0)
    return QubitHamiltonian(operator=op, n_qubits=2)


def _tiny_cfg(**gqe_kw: object) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="gqe_unit",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(dict(gqe_kw)),  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "algo_id",
    [
        "gqe",
        "conditional_gqe",
        "pdpo_gqe",
        "smiles_gqe",
        "gqe_qsci",
        "auger_gqe",
        "gqkae",
        "spin_gqe",
        "adapt_gqe",
    ],
)
def test_gqe_algorithms_registered_peer_to_vqe(algo_id: str) -> None:
    assert is_registered_variational_id("vqe")
    assert is_registered_variational_id(algo_id)
    ids = list_registered_variational_ids()
    assert "vqe" in ids and algo_id in ids


@pytest.mark.parametrize(
    "algo_id",
    [
        "gqe",
        "conditional_gqe",
        "pdpo_gqe",
        "smiles_gqe",
        "gqe_qsci",
        "auger_gqe",
        "gqkae",
        "spin_gqe",
        "adapt_gqe",
    ],
)
def test_quantum_spec_accepts_gqe_algorithms(algo_id: str) -> None:
    cfg = _tiny_cfg(algorithm=algo_id, gqe={"max_iters": 2, "batch_size": 2, "n_gates": 3})
    assert cfg.quantum.algorithm == algo_id


def test_build_gqe_pool_includes_identity() -> None:
    qh = _toy_h2_like()
    tokens = build_gqe_pool(qh, mode="simple", time_exponents=(0, 1), max_paulis=8)
    assert tokens[0].is_identity
    assert len(tokens) > 1


@pytest.mark.parametrize(
    "cls",
    [GQE, ConditionalGQE, PersistentDPOGQE, SmilesTransferGQE, QSCIGQE, AugerGQE, GQKAE, SpinGQE, AdaptGQE],
)
def test_gqe_variant_smoke_run(cls: type) -> None:
    qh = _toy_h2_like()
    cfg = GQEConfig(
        n_gates=3,
        max_iters=3,
        batch_size=3,
        buffer_size=8,
        embed_dim=4,
        time_exponents=(0, 1),
        learning_rate=1.0e-2,
        seed=1,
        pool_mode="simple",
        qcc_budget=6.0,
        condition_dim=2,
    )
    model = cls(qh, config=cfg)
    cond = np.asarray([0.1, -0.2], dtype=float) if cls is ConditionalGQE else None
    teachers = [[0, 1, 0]] if cls is AdaptGQE else None
    result = model.build(condition=cond, teacher_sequences=teachers).run()
    assert np.isfinite(result.energy)
    assert result.n_oracle_calls >= cfg.batch_size
    assert len(result.best_sequence) == cfg.n_gates
    report = model.generate_report()
    assert report["schema"] == "algorithm_gqe_report_v1"
    assert "final_value" in report


def test_variant_to_class_covers_registry_ids() -> None:
    for algo_id in (
        "gqe",
        "conditional_gqe",
        "pdpo_gqe",
        "smiles_gqe",
        "gqe_qsci",
        "auger_gqe",
        "gqkae",
        "spin_gqe",
        "adapt_gqe",
    ):
        assert algo_id in VARIANT_TO_CLASS
