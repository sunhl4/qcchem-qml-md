from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.backends.pauli_measure_expand import hea_operations
from qchem_stack.backends.pytket_bridge import (
    circuit_ir_to_pytket,
    enrich_row_with_pytket,
    pytket_circuit_stats,
)
from qchem_stack.backends.spec import BackendSpec, CircuitIR, circuit_resource_row


def test_circuit_ir_hcx_to_pytket_matches_resource_stats() -> None:
    pytest.importorskip("pytket", reason="optional dependency pytket not installed")
    n_q = 2
    depth = 1
    angles = np.zeros(2 * n_q * depth)
    ops = hea_operations(n_q, depth, angles)
    ir = CircuitIR(n_qubits=n_q, operations=ops, boxes=[])
    c, warns = circuit_ir_to_pytket(ir)
    assert not warns
    st = pytket_circuit_stats(c)
    assert st["twoq_count"] == 1
    assert st["depth"] >= 1
    be = BackendSpec(name="s", provider="statevector", shots_per_circuit=1)
    row = circuit_resource_row("t", ir, shots=1, backend=be)
    er = enrich_row_with_pytket(ir, row)
    assert "pytket_depth" in er
    assert er.get("pytket_twoq_count") == st["twoq_count"]


def test_enrich_without_pytket_returns_none_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    import qchem_stack.backends.pytket_bridge as pb

    def boom() -> type:
        raise ImportError("no")

    monkeypatch.setattr(pb, "_require_pytket", boom)
    ir = CircuitIR(n_qubits=1, operations=[], boxes=[])
    row: dict = {"circuit_id": "x"}
    out = enrich_row_with_pytket(ir, row)
    assert out.get("pytket") is None
    assert out["circuit_id"] == "x"
