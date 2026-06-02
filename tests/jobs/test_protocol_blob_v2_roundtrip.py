"""Protocol job blob v2 JSON round-trip (no pickle)."""

from __future__ import annotations

import os
import tempfile

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.jobs.worker import drain_one_queued
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.protocols.protocol_v2_document import (
    PROTOCOL_BLOB_VERSION_V2,
    protocol_from_v2_document,
    protocol_to_v2_document,
    protocol_v2_dumps,
    protocol_v2_loads,
)
from qchem_stack.protocols.secure_serialization import secure_dumps_protocol, secure_loads_protocol


def _minimal_protocol() -> PauliAveragingProtocol:
    h = QubitOperator((), 0.1) + QubitOperator(((0, "Z"),), 0.05)
    return PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=16),
        pass_bundle=CompilerPassBundle(),
    )


def test_protocol_v2_document_roundtrip() -> None:
    proto = _minimal_protocol()
    doc = protocol_to_v2_document(proto)
    assert doc["protocol_blob_version"] == PROTOCOL_BLOB_VERSION_V2
    loaded = protocol_from_v2_document(doc)
    assert loaded.n_qubits == proto.n_qubits
    assert loaded.backend.shots_per_circuit == proto.backend.shots_per_circuit


def test_protocol_v2_json_bytes_roundtrip() -> None:
    proto = _minimal_protocol()
    loaded = protocol_v2_loads(protocol_v2_dumps(proto))
    assert loaded.n_qubits == proto.n_qubits


def test_secure_dumps_v2_when_env_enabled() -> None:
    proto = _minimal_protocol()
    os.environ["QCHEM_PROTOCOL_BLOB_V2"] = "1"
    try:
        blob = secure_dumps_protocol(proto)
        loaded = secure_loads_protocol(blob)
        assert loaded.n_qubits == proto.n_qubits
    finally:
        del os.environ["QCHEM_PROTOCOL_BLOB_V2"]


def test_worker_drains_v2_signed_blob() -> None:
    proto = _minimal_protocol()
    proto.instantiate()
    proto.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
    os.environ["QCHEM_PROTOCOL_BLOB_V2"] = "1"
    try:
        with tempfile.TemporaryDirectory() as d:
            store = SqliteJobStore(f"{d}/jobs.sqlite")
            handle = proto.launch(store)
            assert drain_one_queued(store, PauliAveragingProtocol.process_job)
            out = store.result(handle.job_id)
            assert out["status"] == "DONE"
            assert "expectation" in out
    finally:
        del os.environ["QCHEM_PROTOCOL_BLOB_V2"]
