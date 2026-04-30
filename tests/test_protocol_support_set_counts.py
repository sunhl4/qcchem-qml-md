"""``protocol_counts`` Pauli support keys after :meth:`PauliAveragingProtocol.run`."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_protocol_counts_hamiltonian_pauli_support() -> None:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator(((0, "X"),), 0.3) + QubitOperator((), 0.1)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=50),
        pass_bundle=CompilerPassBundle(),
    )
    proto.build(np.zeros(4), hea_depth=1)
    proto.compile()
    proto.run()
    pc = proto._counts
    assert "hamiltonian_pauli_strings" in pc
    assert "hamiltonian_pauli_term_records" in pc
    assert pc["pauli_support_truncated"] is False
    assert pc["n_hamiltonian_pauli_terms"] == len(pc["hamiltonian_pauli_strings"])
    assert set(pc["hamiltonian_pauli_strings"]) == {"Z0 Z1", "X0"}
    assert pc["pauli_group_ids"]
    assert len(pc["pauli_group_ids"]) == pc["n_measurement_circuits"]


def test_pmsv_report_triad_fields() -> None:
    h = QubitOperator("Z0", 1.0)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=1,
        backend=BackendSpec(name="sim", shots_per_circuit=10),
        pmsv=PMSVConfig(stabilizers=["Z0"], retention_rate=0.81),
    )
    proto.build(np.zeros(2), hea_depth=1)
    proto.run(noise_rng=np.random.default_rng(42))
    rep = proto._counts.get("pmsv_report")
    assert isinstance(rep, dict)
    assert rep["discard_fraction"] == pytest.approx(0.19)
    assert rep["effective_kept_shots_fraction"] == pytest.approx(0.81)
    assert "stderr_inflation_from_postselection" in rep


def test_pauli_support_max_terms_truncates() -> None:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator(((0, "X"),), 0.3) + QubitOperator((), 0.1)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=50),
        pass_bundle=CompilerPassBundle(),
        pauli_support_max_terms=1,
    )
    proto.build(np.zeros(4), hea_depth=1)
    proto.compile()
    proto.run()
    pc = proto._counts
    assert pc["pauli_support_truncated"] is True
    assert pc["n_hamiltonian_pauli_terms_full"] == 2
    assert len(pc["hamiltonian_pauli_strings"]) == 1
    assert len(pc["hamiltonian_pauli_term_records"]) == 1
