from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import build_measurement_plan, pauli_terms_commute


def test_xy_anticommute_zi_commute() -> None:
    n = 2
    x0 = ((0, "X"),)
    y0 = ((0, "Y"),)
    z0 = ((0, "Z"),)
    assert not pauli_terms_commute(x0, y0, n)
    assert pauli_terms_commute(x0, ((1, "X"),), n)


def test_greedy_fewer_groups_than_terms() -> None:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.5) + QubitOperator(((0, "Z"),), 0.3) + QubitOperator(((1, "Z"),), 0.2)
    plan = build_measurement_plan(h, 2)
    assert len(plan.groups) == 1


def test_tensor_splits_zz_xx() -> None:
    """Tensor-product bases need two circuits; greedy commuting can merge to one non-synthesizable group."""
    h = QubitOperator(((0, "Z"), (1, "Z")), 1.0) + QubitOperator(((0, "X"), (1, "X")), 1.0)
    tplan = build_measurement_plan(h, 2, grouping="tensor_product")
    gplan = build_measurement_plan(h, 2, grouping="greedy_commuting")
    assert len(tplan.groups) == 2
    assert all(bk is not None for bk in tplan.basis_keys)
    assert len(gplan.groups) == 1
    assert gplan.basis_keys == [None]


def test_recommended_shots_monotone() -> None:
    from qchem_stack.backends.shot_budget import recommended_shots_per_circuit

    h = QubitOperator(((0, "Z"),), 1.0)
    plan = build_measurement_plan(h, 2)
    n1 = recommended_shots_per_circuit(plan, dict(h.terms), 0.2)
    n2 = recommended_shots_per_circuit(plan, dict(h.terms), 0.05)
    assert n2 >= n1
