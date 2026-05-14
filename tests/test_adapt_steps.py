from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE


def test_adapt_records_steps_and_gradient_evals() -> None:
    h_op = (
        QubitOperator(((0, "Z"),), 0.5)
        + QubitOperator(((1, "Z"),), 0.5)
        + QubitOperator(((0, "X"), (1, "X")), 0.1)
    )
    qh = QubitHamiltonian(operator=h_op, n_qubits=2)
    av = FermionicAdaptVQE(qh, max_ops=2, hea_depth=1, executor=StatevectorHeaExecutor())
    r = av.run(seed=0)
    assert "adapt_steps" in r.meta
    assert len(r.meta["adapt_steps"]) >= 1
    assert r.meta["total_gradient_evals"] == sum(
        s["n_gradient_evals"] for s in r.meta["adapt_steps"]
    )
    for s in r.meta["adapt_steps"]:
        assert s["n_gradient_evals"] == s["n_pool_candidates_scanned"]
