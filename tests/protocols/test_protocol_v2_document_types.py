"""Typed roundtrip checks for protocol v2 JSON documents."""

from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.protocols.protocol_v2_document import (
    PROTOCOL_BLOB_VERSION_V2,
    protocol_from_v2_document,
    protocol_to_v2_document,
)


def test_protocol_v2_roundtrip_minimal() -> None:
    h = QubitOperator((), 0.1) + QubitOperator(((0, "Z"),), 0.05)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=16),
        pass_bundle=CompilerPassBundle(),
        angles=np.zeros(1, dtype=float),
    )
    doc = protocol_to_v2_document(proto)
    assert doc["protocol_blob_version"] == PROTOCOL_BLOB_VERSION_V2
    restored = protocol_from_v2_document(doc)
    assert restored.n_qubits == 2
    assert restored.backend.shots_per_circuit == 16
