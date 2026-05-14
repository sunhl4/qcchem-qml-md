from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.ionstack_executor import IonStackHeaExecutor
from qchem_stack.backends.spec import BackendSpec


def test_factory_statevector_default() -> None:
    spec = BackendSpec(name="x", provider="statevector")
    ex = executor_from_spec(spec)
    assert isinstance(ex, StatevectorHeaExecutor)


def test_ionstack_injected_fn() -> None:
    h = QubitOperator(((0, "Z"),), 1.0)
    spec = BackendSpec(
        name="ion",
        provider="ionstack",
        meta={"expectation_fn": lambda hh, n, a, d: 0.42},
    )
    ex = IonStackHeaExecutor(spec)
    v = ex.expectation_hea(h, 1, np.array([0.0, 0.0]), 1)
    assert v == pytest.approx(0.42)


def test_ionstack_mock_endpoint() -> None:
    spec = BackendSpec(
        name="ion",
        provider="ionstack",
        meta={"ionstack_endpoint": "mock", "mock_energy": -1.23},
    )
    ex = IonStackHeaExecutor(spec)
    assert ex.expectation_hea(QubitOperator((), 0.0), 1, np.zeros(2), 1) == pytest.approx(-1.23)


def test_qiskit_matches_numpy() -> None:
    pytest.importorskip("qiskit")
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.15) + QubitOperator((), 0.05)
    angles = np.linspace(0.1, 0.8, 8)
    spec = BackendSpec(name="q", provider="qiskit", qiskit_mode="statevector")
    q_ex = executor_from_spec(spec)
    n_ex = StatevectorHeaExecutor()
    e_q = q_ex.expectation_hea(h, 2, angles, 2)
    e_n = n_ex.expectation_hea(h, 2, angles, 2)
    assert e_q == pytest.approx(e_n, rel=1e-5, abs=1e-5)


def test_qiskit_expectation_state_matches_numpy() -> None:
    pytest.importorskip("qiskit")
    from qchem_stack.quantum.statevector import hea_state

    h = QubitOperator(((0, "X"), (1, "Y")), 0.08) + QubitOperator((), 0.02)
    st = hea_state(np.array([0.2, -0.3, 0.4, 0.1, 0.0, 0.0, 0.0, 0.0]), 2, 2)
    spec = BackendSpec(name="q", provider="qiskit")
    q_ex = executor_from_spec(spec)
    n_ex = StatevectorHeaExecutor()
    assert q_ex.expectation_state(st, h, 2) == pytest.approx(
        n_ex.expectation_state(st, h, 2), rel=1e-5, abs=1e-5
    )


def test_vqe_qiskit_vs_numpy() -> None:
    pytest.importorskip("qiskit")
    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.quantum.algorithms.vqe import VQE

    op = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(4, 2))
    r_q = VQE(
        qh,
        depth=1,
        executor=executor_from_spec(BackendSpec(name="q", provider="qiskit")),
    ).run(maxiter=80, seed=2)
    r_n = VQE(qh, depth=1).run(maxiter=80, seed=2)
    assert r_q.energy == pytest.approx(r_n.energy, rel=1e-4, abs=1e-4)
