from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_protocol_build_synthesizes_hea_and_basis_not_pauli_placeholder() -> None:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator((), 0.1)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=32),
        pass_bundle=CompilerPassBundle(),
    )
    proto.build(np.zeros(8), hea_depth=2)
    assert len(proto._logical_circuits) == 1
    ops = proto._logical_circuits[0].operations
    names = [o["name"] for o in ops]
    assert "RY" in names and "CX" in names
    assert "H" not in names
    assert "PAULI_GROUP" not in names
    assert names[-2:] == ["MEASURE", "MEASURE"]


def test_target_stderr_increases_effective_shots_in_counts() -> None:
    h = QubitOperator(((0, "Z"),), 1.0)
    loose = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=100, target_energy_stderr=0.5),
        pass_bundle=CompilerPassBundle(),
    )
    tight = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=100, target_energy_stderr=0.01),
        pass_bundle=CompilerPassBundle(),
    )
    loose.instantiate()
    loose.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
    loose.run()
    tight.instantiate()
    tight.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
    tight.run()
    assert tight._counts["shots_per_circuit_effective"] >= loose._counts["shots_per_circuit_effective"]


def test_pmsv_retention_scales_energy_stderr() -> None:
    h = QubitOperator(((0, "Z"),), 1.0)
    angles = np.array([0.1, 0.2, 0.3, 0.4])
    base = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=100),
        pass_bundle=CompilerPassBundle(),
    )
    base.build(angles, hea_depth=1)
    base.run()
    pmsv = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=100),
        pass_bundle=CompilerPassBundle(),
        pmsv=PMSVConfig(stabilizers=[], retention_rate=0.25),
    )
    pmsv.build(angles, hea_depth=1)
    pmsv.run()
    assert pmsv._counts["pmsv_stderr_scale"] == pytest.approx(2.0)
    assert pmsv._counts["energy_stderr"] == pytest.approx(base._counts["energy_stderr"] * 2.0)
