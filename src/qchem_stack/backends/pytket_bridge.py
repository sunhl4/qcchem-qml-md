"""Optional export of :class:`~qchem_stack.backends.spec.CircuitIR` to pytket for TKET-native depth / 2Q stats.

Install: ``pip install qchem-stack[pytket]`` (or ``pip install pytket``).
"""

from __future__ import annotations

from typing import Any, Tuple, cast

from qchem_stack.backends.spec import CircuitIR


def _require_pytket() -> type:
    try:
        import pytket  # noqa: F401
    except ImportError as e:  # pragma: no cover - covered by optional test
        raise ImportError(
            "pytket is required for this function. Install with: pip install qchem-stack[pytket]"
        ) from e
    from pytket.circuit import Circuit  # type: ignore[import-untyped]

    return cast(type, Circuit)


def circuit_ir_to_pytket(ir: CircuitIR) -> Tuple[Any, list[str]]:
    """Build a pytket :class:`~pytket.circuit.Circuit` from supported :class:`CircuitIR` ops.

    Supported names: ``RY``, ``RX``, ``CX``, ``CNOT``, ``H``, ``SDG``, ``MEASURE``.
    ``PAULI_GROUP`` placeholder ops and compile ``ANNOTATION`` meta-ops are skipped (see warnings).

    Returns:
        ``(circuit, warnings)`` where ``warnings`` lists skipped op types.
    """
    Circuit = _require_pytket()
    warnings: list[str] = []
    ops = list(ir.operations)
    n_meas = sum(1 for o in ops if o.get("name") == "MEASURE")
    c = Circuit(ir.n_qubits, n_meas) if n_meas else Circuit(ir.n_qubits)
    mi = 0
    for op in ops:
        name = str(op.get("name", ""))
        qs = list(op.get("qubits", []))
        p = op.get("params") or {}
        if name in ("PAULI_GROUP", "ANNOTATION"):
            warnings.append(name)
            continue
        if name == "RY":
            c.Ry(float(p["theta"]), qs[0])
        elif name == "RX":
            c.Rx(float(p["theta"]), qs[0])
        elif name in ("CX", "CNOT"):
            c.CX(qs[0], qs[1])
        elif name == "H":
            c.H(qs[0])
        elif name == "SDG":
            c.Sdg(qs[0])
        elif name == "MEASURE":
            c.Measure(qs[0], mi)
            mi += 1
        else:
            raise ValueError(
                f"pytket_bridge: unsupported CircuitIR op {name!r} "
                f"(extend qchem_stack.backends.pytket_bridge if needed)"
            )
    return c, warnings


def pytket_circuit_stats(circuit: Any) -> dict[str, Any]:
    """Depth, 2Q depth, and two-qubit gate count from a pytket :class:`~pytket.circuit.Circuit`."""
    _require_pytket()
    ng = circuit.n_gates
    n_gates = int(ng() if callable(ng) else ng)
    return {
        "depth": int(circuit.depth()),
        "depth_2q": int(circuit.depth_2q()),
        "twoq_count": int(circuit.n_2qb_gates()),
        "n_qubits": int(circuit.n_qubits),
        "n_gates": n_gates,
    }


def enrich_row_with_pytket(ir: CircuitIR, base_row: dict[str, Any]) -> dict[str, Any]:
    """Copy ``base_row`` and add ``pytket_*`` metrics when pytket is installed; else set ``pytket: None``."""
    out = dict(base_row)
    try:
        c, warns = circuit_ir_to_pytket(ir)
        st = pytket_circuit_stats(c)
        out["pytket_depth"] = st["depth"]
        out["pytket_depth_2q"] = st["depth_2q"]
        out["pytket_twoq_count"] = st["twoq_count"]
        out["pytket_n_gates"] = st["n_gates"]
        if warns:
            out["pytket_skipped_ops"] = warns
    except ImportError:
        out["pytket"] = None
    return out
