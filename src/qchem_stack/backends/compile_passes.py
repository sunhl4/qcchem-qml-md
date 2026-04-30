from __future__ import annotations

from typing import Any

from qchem_stack.backends.spec import CircuitIR


def apply_pass_bundle(circ: CircuitIR, passes: list[str]) -> CircuitIR:
    """Apply named compiler passes (identity, ``qubit_reuse_hint`` metadata)."""
    out = CircuitIR(n_qubits=circ.n_qubits, operations=list(circ.operations), boxes=list(circ.boxes))
    meta_ops: list[dict[str, Any]] = []
    for name in passes:
        if name == "qubit_reuse_hint":
            meta_ops.append({"name": "ANNOTATION", "qubits": [], "params": {"qubit_reuse": True}})
        elif name == "strip_boxes":
            out.boxes = []
    out.operations = list(out.operations) + meta_ops
    return out
