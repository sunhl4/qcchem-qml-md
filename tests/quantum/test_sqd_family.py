"""Unit tests for SQD / sampling family (customer product gates)."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator
from pydantic import ValidationError

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec, SCFSpec
from qchem_stack.config.backend import BackendSpecConfig
from qchem_stack.exceptions import PipelineError, QuantumAlgorithmError
from qchem_stack.quantum.algorithms.sqd import (
    CUSTOMER_SQD_ALGORITHM_IDS,
    EXPERIMENTAL_SQD_ALGORITHM_IDS,
    MAX_SQD_QUBITS,
    VARIANT_TO_CLASS,
    AdaptQSCI,
    CBS,
    EWFTrimSQD,
    HIVQE,
    QBESQD,
    QSCI,
    QSEQSCI,
    SKQD,
    SQD,
    SQDAFQMC,
    SqdConfig,
    SqDRIFT,
)
from qchem_stack.quantum.algorithms.sqd.core import _unitary_pool_rotation
from qchem_stack.quantum.algorithms.sqd.sampling import popcount, prepare_hea_sampling_state
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import qubit_operator_to_sparse
from qchem_stack.quantum.variational_plugins.registry import (
    is_registered_variational_id,
    list_registered_variational_ids,
    run_variational_stage,
)
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

SQD_ALGO_IDS = sorted(CUSTOMER_SQD_ALGORITHM_IDS | EXPERIMENTAL_SQD_ALGORITHM_IDS)


def _toy_h2_like(*, n_electrons: int | None = 1) -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), 0.5) + QubitOperator(((1, "Z"),), 0.5)
    op += QubitOperator(((0, "X"), (1, "X")), -1.0)
    fs = None if n_electrons is None else FermionSpace(n_spin_orbitals=2, n_electrons=n_electrons)
    return QubitHamiltonian(operator=op, n_qubits=2, fermion_space=fs)


def _tiny_cfg(**quantum_kw: object) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="sqd_unit",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec.model_validate(dict(quantum_kw)),  # type: ignore[arg-type]
    )


@pytest.mark.parametrize("algo_id", SQD_ALGO_IDS)
def test_sqd_algorithms_registered_peer_to_vqe(algo_id: str) -> None:
    assert is_registered_variational_id("vqe")
    assert is_registered_variational_id(algo_id)
    ids = list_registered_variational_ids()
    assert "vqe" in ids and algo_id in ids


@pytest.mark.parametrize("algo_id", sorted(CUSTOMER_SQD_ALGORITHM_IDS))
def test_quantum_spec_accepts_customer_sqd_algorithms(algo_id: str) -> None:
    cfg = _tiny_cfg(
        algorithm=algo_id,
        sqd={"n_shots": 64, "subspace_size": 4, "max_iters": 2},
        pauli={"use_protocol": False},
    )
    assert cfg.quantum.algorithm == algo_id


@pytest.mark.parametrize("algo_id", sorted(EXPERIMENTAL_SQD_ALGORITHM_IDS))
def test_experimental_sqd_requires_opt_in(algo_id: str) -> None:
    with pytest.raises(ValidationError, match="allow_experimental"):
        _tiny_cfg(
            algorithm=algo_id,
            sqd={"n_shots": 32, "subspace_size": 4, "allow_experimental": False},
            pauli={"use_protocol": False},
        )
    cfg = _tiny_cfg(
        algorithm=algo_id,
        sqd={"n_shots": 32, "subspace_size": 4, "allow_experimental": True},
        pauli={"use_protocol": False},
    )
    assert cfg.quantum.sqd.allow_experimental is True


def test_hea_on_hf_is_unitary_from_reference() -> None:
    rng = np.random.default_rng(0)
    angles = rng.uniform(-0.2, 0.2, size=4)
    psi = prepare_hea_sampling_state(2, angles, 1, n_electrons=1)
    assert abs(float(np.linalg.norm(psi)) - 1.0) < 1e-10
    assert np.count_nonzero(np.abs(psi) > 1e-8) >= 2


def test_n_qubits_hard_limit() -> None:
    op = QubitOperator(((0, "Z"),), 1.0)
    qh = QubitHamiltonian(operator=op, n_qubits=MAX_SQD_QUBITS + 1)
    with pytest.raises(QuantumAlgorithmError, match="at most"):
        SQD(qh, SqdConfig(n_shots=8, subspace_size=2, max_iters=1, n_electrons=1))


def test_non_statevector_backend_rejected() -> None:
    qh = _toy_h2_like()
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="sqd_uqc",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="uqc"),
        quantum=QuantumSpec.model_validate(
            {
                "algorithm": "sqd",
                "sqd": {"n_shots": 16, "subspace_size": 4, "max_iters": 1, "n_electrons": 1},
                "pauli": {"use_protocol": False},
            }
        ),
    )
    ctx = VariationalRunContext(
        cfg=cfg, hamiltonian=qh, executor=StatevectorHeaExecutor(), seed=0
    )
    with pytest.raises(PipelineError, match="statevector"):
        run_variational_stage(ctx)


@pytest.mark.parametrize(
    "cls",
    [
        CBS,
        QSCI,
        SQD,
        QSEQSCI,
        AdaptQSCI,
        SKQD,
        SqDRIFT,
        HIVQE,
        EWFTrimSQD,
        QBESQD,
        SQDAFQMC,
    ],
)
def test_sqd_variant_smoke_run(cls: type) -> None:
    qh = _toy_h2_like()
    cfg = SqdConfig(
        n_shots=64,
        subspace_size=4,
        max_iters=2,
        hea_depth=1,
        n_electrons=1,
        krylov_dim=3,
        qdrift_steps=4,
        qdrift_replicas=2,
        recovery_iters=1,
        afqmc_walkers=4,
        afqmc_steps=3,
        n_fragments=2,
        seed=1,
    )
    model = cls(qh, config=cfg)
    result = model.build().run(seed=1)
    assert np.isfinite(result.energy)
    assert result.nfev >= 1
    assert all(popcount(b) == 1 for b in result.selected_bitstrings)
    report = model.generate_report()
    assert report["schema"] == "algorithm_sqd_report_v1"
    assert result.meta["dense_prototype"] is True
    assert result.meta["backend_executor_used"] is False
    assert result.meta["execution_mode"] == "dense_statevector"


def test_adapt_qsci_unitary_on_chemistry_pool() -> None:
    op = QubitOperator(((0, "Z"),), 0.5) + QubitOperator(((1, "Z"),), 0.5)
    op += QubitOperator(((2, "Z"),), 0.1) + QubitOperator(((3, "Z"),), 0.1)
    op += QubitOperator(((0, "X"), (1, "X")), -0.5)
    qh = QubitHamiltonian(
        operator=op,
        n_qubits=4,
        fermion_space=FermionSpace(n_spin_orbitals=4, n_electrons=2),
    )
    pool = build_registered_operator_pool("fermionic_uccsd", qh)
    assert len(pool) >= 1
    p_mat = qubit_operator_to_sparse(pool[0], 4)
    u = _unitary_pool_rotation(p_mat, 0.3)
    assert float(np.linalg.norm(u.conj().T @ u - np.eye(u.shape[0]))) < 1e-10
    result = AdaptQSCI(
        qh, SqdConfig(n_shots=32, subspace_size=4, max_iters=2, seed=0)
    ).build().run(seed=0)
    assert np.isfinite(result.energy)
    assert result.meta["pool_rotation"] == "unitary_antihermitian_or_hermitian"


def test_hi_vqe_lite_preserves_particle_number() -> None:
    qh = _toy_h2_like()
    cfg = SqdConfig(n_shots=64, subspace_size=4, max_iters=2, n_electrons=1, seed=0)
    result = HIVQE(qh, config=cfg).build().run(seed=0)
    assert result.meta["method"] == "hi_vqe_lite"
    assert all(popcount(b) == 1 for b in result.selected_bitstrings)


def test_variant_to_class_covers_registry_ids() -> None:
    for algo_id in SQD_ALGO_IDS:
        assert algo_id in VARIANT_TO_CLASS


@pytest.mark.parametrize("algo_id", sorted(CUSTOMER_SQD_ALGORITHM_IDS))
def test_run_variational_stage_customer_sqd_smoke(algo_id: str) -> None:
    qh = _toy_h2_like()
    ctx = VariationalRunContext(
        cfg=_tiny_cfg(
            algorithm=algo_id,
            sqd={"n_shots": 32, "subspace_size": 4, "max_iters": 2, "n_electrons": 1},
            pauli={"use_protocol": False},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
    )
    st = run_variational_stage(ctx)
    assert np.isfinite(st.energy)
    assert st.algo_meta.get("algorithm") == algo_id
    assert st.algorithm_report is not None
    assert st.algorithm_report["schema"] == "algorithm_sqd_report_v1"
    assert st.algorithm_report["dense_prototype"] is True
    assert st.algorithm_report["backend_executor_used"] is False
    assert st.algorithm_report["customer_tier"] == "customer"


@pytest.mark.parametrize("algo_id", sorted(EXPERIMENTAL_SQD_ALGORITHM_IDS))
def test_run_variational_stage_experimental_sqd_smoke(algo_id: str) -> None:
    qh = _toy_h2_like()
    ctx = VariationalRunContext(
        cfg=_tiny_cfg(
            algorithm=algo_id,
            sqd={
                "n_shots": 32,
                "subspace_size": 4,
                "max_iters": 2,
                "n_electrons": 1,
                "allow_experimental": True,
            },
            pauli={"use_protocol": False},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
    )
    st = run_variational_stage(ctx)
    assert st.algorithm_report is not None
    assert st.algorithm_report["customer_tier"] == "experimental"
