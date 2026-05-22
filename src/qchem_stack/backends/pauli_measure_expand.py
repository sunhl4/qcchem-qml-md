from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.backends.spec import CircuitIR

if TYPE_CHECKING:
    import numpy as np


def hea_operations(n_qubits: int, depth: int, angles: np.ndarray) -> list[dict[str, Any]]:
    """Same layer order as :func:`qchem_stack.quantum.statevector.hea_state` (tensor axis = qubit index)."""
    n_params = 2 * n_qubits * depth
    if angles.size != n_params:
        raise ValueError(f"expected {n_params} angles, got {angles.size}")
    ops: list[dict[str, Any]] = []
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            ops.append({"name": "RY", "qubits": [q], "params": {"theta": float(angles[k])}})
            k += 1
            ops.append({"name": "RX", "qubits": [q], "params": {"theta": float(angles[k])}})
            k += 1
        for q in range(n_qubits - 1):
            ops.append({"name": "CX", "qubits": [q, q + 1], "params": {}})
    return ops


def basis_change_operations(
    basis_key: tuple[tuple[int, str], ...], n_qubits: int
) -> list[dict[str, Any]]:
    """Map eigenbasis of commuting Paulis to computational Z-readout (single-qubit Cliffords only)."""
    axis: dict[int, str] = {}
    for idx, p in basis_key:
        if p not in ("X", "Y", "Z"):
            raise ValueError(f"Unknown Pauli axis {p!r}")
        axis[int(idx)] = p
    ops: list[dict[str, Any]] = []
    for q in range(n_qubits):
        p = axis.get(q, "I")
        if p in ("I", "Z"):
            continue
        if p == "X":
            ops.append({"name": "H", "qubits": [q], "params": {}})
        else:
            ops.append({"name": "SDG", "qubits": [q], "params": {}})
            ops.append({"name": "H", "qubits": [q], "params": {}})
    return ops


def measure_support_operations(support_qubits: list[int]) -> list[dict[str, Any]]:
    return [{"name": "MEASURE", "qubits": [q], "params": {}} for q in sorted(set(support_qubits))]


def deserialize_basis_key(raw: Any) -> tuple[tuple[int, str], ...] | None:
    if raw is None:
        return None
    if isinstance(raw, tuple):
        return raw  # type: ignore[return-value]
    out: list[tuple[int, str]] = []
    for pair in raw:
        if isinstance(pair, (list, tuple)) and len(pair) == 2:
            out.append((int(pair[0]), str(pair[1])))
        else:
            raise ValueError(f"bad basis_key entry: {pair!r}")
    return tuple(out)


def serialize_basis_key(basis_key: tuple[tuple[int, str], ...] | None) -> Any:
    if basis_key is None:
        return None
    return [[int(i), str(p)] for i, p in basis_key]


def build_synthesized_pauli_shot_circuit(
    n_qubits: int,
    prep_operations: list[dict[str, Any]],
    *,
    basis_key: tuple[tuple[int, str], ...],
    support_qubits: list[int],
    prep_box: str = "HEA",
) -> CircuitIR:
    ops: list[dict[str, Any]] = []
    ops.extend(prep_operations)
    ops.extend(basis_change_operations(basis_key, n_qubits))
    ops.extend(measure_support_operations(support_qubits))
    return CircuitIR(
        n_qubits=n_qubits,
        operations=ops,
        boxes=[prep_box, "PauliBasis", "Measure"],
    )
