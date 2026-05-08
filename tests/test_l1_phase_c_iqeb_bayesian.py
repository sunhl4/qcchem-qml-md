"""L1 phase C (序 9, 14): IQEB outer loop + Bayesian QPE stub (no PySCF)."""

from __future__ import annotations

import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.qpe_qec_demo import BayesianQPEStub
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE


def test_iqeb_outer_loop_meta_and_selected_strings() -> None:
    op = (
        QubitOperator(((0, "Z"),), 0.4)
        + QubitOperator(((1, "Z"),), 0.3)
        + QubitOperator(((0, "Z"), (1, "Z")), 0.1)
        + QubitOperator((), 0.05)
    )
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(2, 2))
    res = IQEBVQE(qh, max_rounds=2).run(depth=1, seed=7)
    assert res.meta.get("rounds") == 2
    assert res.energy == pytest.approx(res.vqe.energy)
    assert len(res.selected_pauli_strings) == 1


def test_bayesian_qpe_stub_estimate_returns_map_dict() -> None:
    stub = BayesianQPEStub(grid_points=64)
    out = stub.estimate([(0.0, 0.5), (1.0, 1.0)])
    assert isinstance(out, dict)
    assert out.get("schema") == "bayesian_qpe_stub_map_v1"
    phase = float(out["map_phase"])
    assert -3.15 <= phase <= 3.15
