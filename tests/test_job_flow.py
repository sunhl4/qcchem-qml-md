from __future__ import annotations

import tempfile

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.config import NexusAnalogSpec
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_launch_process_retrieve() -> None:
    with tempfile.TemporaryDirectory() as d:
        store = SqliteJobStore(f"{d}/jobs.sqlite")
        h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.0)
        na = NexusAnalogSpec(enabled=True, project_label="async_parity", unit_per_shot=0.5)
        proto = PauliAveragingProtocol(
            hamiltonian=h,
            n_qubits=1,
            backend=BackendSpec(name="sim", shots_per_circuit=10),
            pass_bundle=CompilerPassBundle(),
            nexus_analog=na,
        )
        proto.instantiate()
        proto.build(np.array([0.1, 0.2]), hea_depth=1)
        handle = proto.launch(store)
        assert handle.protocol_hash is not None and len(handle.protocol_hash) == 32
        PauliAveragingProtocol.process_job(store, handle.job_id)
        out = proto.retrieve(store, handle)
        assert out.get("status") == "DONE"
        assert "expectation" in out
        bill = out.get("nexus_analog_billing")
        assert isinstance(bill, dict)
        assert bill.get("project_label") == "async_parity"
