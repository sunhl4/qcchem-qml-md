"""Annotation-only compile pass infrastructure for CircuitIR.

This module provides a mechanism to attach metadata annotations to circuits without
performing actual circuit transformations. The passes here are "no-op" in the sense
that they do not modify the gate sequence, qubit routing, or circuit structure.

**Current passes:**

- ``qubit_reuse_hint``: Annotates that qubits may be reused (no transformation).
- ``strip_boxes``: Removes the ``boxes`` field from CircuitIR (the only actual transformation).
- ``route_linear`` / ``routing_linear``: Annotates linear-chain routing preference.
- ``decompose_to_native`` / ``decompose_native``: Annotates native gate decomposition preference.
- ``optimize_1q`` / ``optimize_light``: Annotates light single-qubit gate fusion preference.
- ``optimize_aggressive`` / ``optimize_heavy``: Annotates aggressive commutation optimization preference.

**Design rationale:**

These annotations are consumed by downstream tooling (e.g., circuit visualizers, resource estimators,
or external compilers) that may apply their own transformation logic. This module provides a
standardized way to express intent without enforcing a specific implementation.

**Future work:**

Actual circuit transformations (e.g., gate decomposition, routing, optimization) should be implemented
as separate modules or integrated with external compilers like pytket.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.backends.spec import CircuitIR


def apply_pass_bundle(circ: CircuitIR, passes: list[str]) -> CircuitIR:
    """Apply named compiler passes (annotation-only, except ``strip_boxes``).

    Most passes attach metadata annotations to the circuit without modifying its structure.
    The only exception is ``strip_boxes``, which clears the ``boxes`` field.

    Args:
        circ: Input circuit IR.
        passes: List of pass names to apply (case-insensitive, whitespace-stripped).

    Returns:
        A new CircuitIR with annotations appended to operations. The original circuit is not modified.

    Note:
        Unknown pass names are silently ignored. This allows forward compatibility with
        passes that may be implemented in future versions or by external tooling.
    """
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
