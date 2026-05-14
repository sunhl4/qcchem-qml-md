from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.qiskit_pauli_shots import (
    _bit_reverse_n,
    energy_estimate_grouped_qiskit_shots,
    qiskit_bitstring_to_comp_index,
)
from qchem_stack.backends.spec import BackendSpec
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_bit_reverse_roundtrip() -> None:
    for n in (1, 2, 3, 4):
        for k in range(1 << n):
            r = _bit_reverse_n(_bit_reverse_n(k, n), n)
            assert r == (k & ((1 << n) - 1))


def test_qiskit_string_maps_to_of_index_2q() -> None:
    # Wire MSB = phys n-1, int(s,2) = K; OF index = bitrev(K) for this stack (see qiskit_pauli_shots module doc)
    n = 2
    assert qiskit_bitstring_to_comp_index("00", n) == 0
    assert qiskit_bitstring_to_comp_index("10", n) == 1
    assert qiskit_bitstring_to_comp_index("01", n) == 2
    assert qiskit_bitstring_to_comp_index("11", n) == 3


@pytest.mark.parametrize("n_shots", [2000])
def test_qiskit_shots_energy_near_exact(n_shots: int) -> None:
    pytest.importorskip("qiskit")
    pytest.importorskip("qiskit_aer")
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.3) + QubitOperator((), 0.01)
    nq = 2
    d = 1
    angles = np.array([0.1, 0.2, 0.3, 0.4], dtype=float)
    plan = build_measurement_plan(h, nq, grouping="tensor_product")
    e_sh, se, meta = energy_estimate_grouped_qiskit_shots(
        h,
        plan,
        nq,
        d,
        angles,
        n_shots,
        BackendSpec(name="aer", provider="qiskit"),
        np.random.default_rng(42),
    )
    ex = executor_from_spec(BackendSpec(name="q", provider="qiskit"))
    e_ex = ex.expectation_hea(h, nq, angles, d)
    assert abs(e_sh - e_ex) < 0.15, (e_sh, e_ex, se, meta)  # shot noise; wide bound
    assert meta.get("qiskit_counts_per_group")
    assert se >= 0.0
    e_hi, se2, m2 = energy_estimate_grouped_qiskit_shots(
        h,
        plan,
        nq,
        d,
        angles,
        8000,
        BackendSpec(name="aer", provider="qiskit"),
        np.random.default_rng(0),
    )
    assert abs(e_hi - e_ex) < 0.08


def test_pauli_protocol_qiskit_shots_runs() -> None:
    pytest.importorskip("qiskit")
    pytest.importorskip("qiskit_aer")
    h = QubitOperator(((0, "X"),), 0.5) + QubitOperator((), 0.0)
    spec = BackendSpec(name="aer", provider="qiskit", shots_per_circuit=1000, meta={})
    p = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=1,
        backend=spec,
        measurement_grouping="tensor_product",
        run_qiskit_shots=True,
        run_sampled=False,
        record_histograms=True,
    )
    p.build(np.array([0.2, 0.3], dtype=float), hea_depth=1)
    p.compile()
    p.run(executor=None)
    assert p._counts.get("expectation_source") == "qiskit_shot_counts_get_counts"
    assert "qiskit_pauli_shot_meta" in p._counts
    assert p._counts.get("measurement_histogram_rows") is not None
