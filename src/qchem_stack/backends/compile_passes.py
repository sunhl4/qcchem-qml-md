from __future__ import annotations

from typing import Any

from qchem_stack.backends.spec import CircuitIR


def apply_pass_bundle(circ: CircuitIR, passes: list[str]) -> CircuitIR:
    """Apply named compiler passes (identity, routing/decompose/optimize presets)."""
    out = CircuitIR(
        n_qubits=circ.n_qubits, operations=list(circ.operations), boxes=list(circ.boxes)
    )
    meta_ops: list[dict[str, Any]] = []
    for name in passes:
        key = str(name).strip().lower()
        if key == "qubit_reuse_hint":
            meta_ops.append({"name": "ANNOTATION", "qubits": [], "params": {"qubit_reuse": True}})
        elif key == "strip_boxes":
            out.boxes = []
        elif key in {"route_linear", "routing_linear"}:
            meta_ops.append(
                {"name": "ANNOTATION", "qubits": [], "params": {"routing_preset": "linear_chain"}}
            )
        elif key in {"decompose_to_native", "decompose_native"}:
            meta_ops.append(
                {"name": "ANNOTATION", "qubits": [], "params": {"decompose_preset": "native_twoq"}}
            )
        elif key in {"optimize_1q", "optimize_light"}:
            meta_ops.append(
                {
                    "name": "ANNOTATION",
                    "qubits": [],
                    "params": {"optimize_preset": "light_1q_fusion"},
                }
            )
        elif key in {"optimize_aggressive", "optimize_heavy"}:
            meta_ops.append(
                {
                    "name": "ANNOTATION",
                    "qubits": [],
                    "params": {"optimize_preset": "aggressive_commute"},
                }
            )
    out.operations = list(out.operations) + meta_ops
    return out
