from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.jobs.cost import CostEstimate
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.backends.spec import dataframe_circuit_shot, summarize_circuit_shot_rows


def test_protocol_five_stage_and_cost() -> None:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator((), 0.1)
    be = BackendSpec(name="sim", shots_per_circuit=100)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=be,
        pass_bundle=CompilerPassBundle(preoptimize_passes=["qubit_reuse_hint"]),
    )
    proto.instantiate()
    proto.build(np.zeros(8), hea_depth=2)
    proto.compile()
    proto.run()
    e = proto.evaluate()
    assert proto._counts["expectation_source"] == "executor_exact_or_device_mean"
    assert proto._counts["energy_stderr_model"] == "conservative_sum_bound_equal_shots"
    assert proto._counts["n_pauli_terms"] >= 1
    assert proto._counts["n_pauli_groups"] >= 0
    assert proto._counts["pmsv_stderr_scale"] == 1.0
    rows = proto.dataframe_circuit_shot_rows()
    df = dataframe_circuit_shot(rows)
    assert not df.empty
    sm = summarize_circuit_shot_rows(rows)
    assert sm["n_circuits"] == len(rows)
    assert sm["sum_shots"] >= 0
    ce = CostEstimate.from_resource_rows(rows)
    assert ce.estimated_total_shots >= 0
    assert isinstance(e, float)
