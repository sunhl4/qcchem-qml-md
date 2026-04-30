from __future__ import annotations

import tempfile

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.jobs.worker import drain_one_queued
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_drain_one_queued_runs_job() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/jobs.sqlite"
        store = SqliteJobStore(path)
        h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.0)
        proto = PauliAveragingProtocol(
            hamiltonian=h,
            n_qubits=1,
            backend=BackendSpec(name="sim", shots_per_circuit=8),
            pass_bundle=CompilerPassBundle(),
        )
        proto.instantiate()
        proto.build(np.array([0.1, 0.2]), hea_depth=1)
        handle = proto.launch(store)
        assert drain_one_queued(store, PauliAveragingProtocol.process_job)
        out = store.result(handle.job_id)
        assert out["status"] == "DONE"
        assert out["job_kind"] == "pauli_protocol"
        assert "expectation" in out
