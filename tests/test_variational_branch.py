"""Shared UCCSD variational branch factory."""

from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.variational_branch import (
    build_uccsd_variational_model,
    run_uccsd_vqe_from_config,
)


def _h2_like_qh() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
    return QubitHamiltonian(
        operator=op,
        n_qubits=4,
        fermion_space=FermionSpace(n_spin_orbitals=4, n_electrons=2),
        meta={"fermion_to_qubit_map": "jordan_wigner"},
    )


def test_build_uccsd_variational_model_prepare_state() -> None:
    qh = _h2_like_qh()
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    assert model.n_params >= 1
    assert len(model.param_bounds) == model.n_params
    psi = model.prepare_state(np.zeros(model.n_params, dtype=float))
    assert psi.shape == (16,)
    assert abs(float(np.linalg.norm(psi)) - 1.0) < 1e-10


def test_run_uccsd_vqe_from_config_returns_energy() -> None:
    qh = _h2_like_qh()
    exe = StatevectorHeaExecutor()
    res = run_uccsd_vqe_from_config(qh, exe, maxiter=5, seed=0, trotter_steps=None)
    assert isinstance(float(res.energy), float)
    assert res.angles.ndim == 1
    assert len(res.angles) == int(res.meta["uccsd_n_parameters"])
    assert res.nfev >= 1
