"""Pauli-string decomposition for UCCSD cluster exponentials (InQuanto-style ``exp(-iθP)`` chains)."""

from __future__ import annotations

from typing import Any, Literal, cast

import numpy as np
from scipy.linalg import expm

from qchem_stack.quantum.statevector import _kron_n, _pauli_char_to_mat

DecompositionMode = Literal["pauli", "unitary"]


def _pauli_string_from_index(idx: int, n_qubits: int) -> str:
    chars = "IXYZ"
    s = ""
    t = idx
    for _ in range(n_qubits):
        s = chars[t & 3] + s
        t >>= 2
    return s


def pauli_matrix(pauli_string: str) -> np.ndarray:
    return _kron_n([_pauli_char_to_mat(c) for c in pauli_string])


def decompose_antihermitian_to_pauli_terms(
    antiherm: np.ndarray,
    n_qubits: int,
    *,
    coeff_tol: float = 1e-12,
) -> list[tuple[str, complex]]:
    """Expand anti-Hermitian ``A`` as ``sum_k c_k P_k`` with Hermitian Pauli strings ``P_k``."""
    dim = 2**n_qubits
    mat = np.asarray(antiherm, dtype=np.complex128)
    if mat.shape != (dim, dim):
        raise ValueError(f"expected ({dim}, {dim}) matrix, got {mat.shape}")
    terms: list[tuple[str, complex]] = []
    for idx in range(4**n_qubits):
        ps = _pauli_string_from_index(idx, n_qubits)
        if ps == "I" * n_qubits:
            continue
        coeff = np.trace(pauli_matrix(ps) @ mat) / dim
        if abs(coeff) > coeff_tol:
            terms.append((ps, complex(coeff)))
    return terms


def _pauli_terms_commute(a: str, b: str) -> bool:
    anticom = 0
    for ca, cb in zip(a, b, strict=True):
        if ca != "I" and cb != "I" and ca != cb:
            anticom += 1
    return anticom % 2 == 0


def cluster_expm_via_pauli_product(
    antiherm: np.ndarray,
    angle: float,
    n_qubits: int,
) -> np.ndarray:
    """``expm(angle * A)`` as ordered product of single-Pauli exponentials (exact for UCCSD JW clusters)."""
    terms = decompose_antihermitian_to_pauli_terms(antiherm, n_qubits)
    dim = 2**n_qubits
    u = np.eye(dim, dtype=np.complex128)
    for ps, coeff in terms:
        u = expm(float(angle) * complex(coeff) * pauli_matrix(ps)) @ u
    return u


def pauli_rotation_angle_from_cluster(angle: float, pauli_coeff: complex) -> float:
    """Map ``expm(angle * coeff * P)`` to ``exp(-i phi/2 * P)`` rotation angle ``phi``."""
    return float(-2.0 * np.imag(float(angle) * complex(pauli_coeff)))


def pauli_rotation_elementary_ops(
    pauli_string: str,
    phi: float,
) -> list[dict[str, Any]]:
    """Decompose ``exp(-i phi/2 P)`` into H/SDG/CX/RZ elementary CircuitIR ops."""
    n = len(pauli_string)
    try:
        return _pauli_rotation_elementary_ops_qiskit(pauli_string, phi, n_qubits=n)
    except Exception:
        return _pauli_rotation_elementary_ops_manual(pauli_string, phi)


def _pauli_rotation_elementary_ops_qiskit(
    pauli_string: str,
    phi: float,
    *,
    n_qubits: int,
) -> list[dict[str, Any]]:
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PauliEvolutionGate
    from qiskit.quantum_info import Pauli

    if abs(float(phi)) < 1e-15:
        return []
    n = int(n_qubits)

    def logical(p: int) -> int:
        return n - 1 - int(p)

    def wire(q: int) -> int:
        return n - 1 - int(q)

    qc = QuantumCircuit(n)
    gate = PauliEvolutionGate(Pauli(pauli_string[::-1]), time=float(phi) / 2.0)
    qc.append(gate, [wire(q) for q in range(n)])
    dec = qc.decompose()
    ops: list[dict[str, Any]] = []
    for inst in dec.data:
        name = inst.operation.name
        phys = [int(q._index) for q in inst.qubits]
        params = getattr(inst.operation, "params", ()) or ()
        if name == "h":
            ops.append({"name": "H", "qubits": [logical(phys[0])], "params": {}})
        elif name == "x":
            ops.append({"name": "X", "qubits": [logical(phys[0])], "params": {}})
        elif name == "cx":
            ops.append({"name": "CX", "qubits": [logical(phys[0]), logical(phys[1])], "params": {}})
        elif name == "rz" and params:
            ops.append(
                {"name": "RZ", "qubits": [logical(phys[0])], "params": {"theta": float(params[0])}}
            )
        elif name == "rx" and params:
            ops.append(
                {"name": "RX", "qubits": [logical(phys[0])], "params": {"theta": float(params[0])}}
            )
        elif name in ("sx", "sxdg", "sdg", "s"):
            if name == "sx":
                ops.append({"name": "SX", "qubits": [logical(phys[0])], "params": {}})
            elif name in ("sxdg", "sx-dg"):
                ops.append({"name": "SXDG", "qubits": [logical(phys[0])], "params": {}})
            elif name == "sdg":
                ops.append({"name": "SDG", "qubits": [logical(phys[0])], "params": {}})
            else:
                ops.append({"name": "S", "qubits": [logical(phys[0])], "params": {}})
        else:
            raise ValueError(f"unsupported PauliEvolution decomposed gate: {name!r}")
    return ops


def _pauli_rotation_elementary_ops_manual(
    pauli_string: str,
    phi: float,
) -> list[dict[str, Any]]:
    support = [q for q, p in enumerate(pauli_string) if p != "I"]
    if not support:
        return []
    if len(support) == 1:
        q = support[0]
        p = pauli_string[q]
        if p == "X":
            return [{"name": "RX", "qubits": [q], "params": {"theta": float(phi)}}]
        if p == "Y":
            return [{"name": "RY", "qubits": [q], "params": {"theta": float(phi)}}]
        return [{"name": "RZ", "qubits": [q], "params": {"theta": float(phi)}}]

    ops: list[dict[str, Any]] = []
    for q in support:
        p = pauli_string[q]
        if p == "X":
            ops.append({"name": "H", "qubits": [q], "params": {}})
        elif p == "Y":
            ops.extend(
                [
                    {"name": "SDG", "qubits": [q], "params": {}},
                    {"name": "H", "qubits": [q], "params": {}},
                ]
            )
    target = support[0]
    for ctrl in support[1:]:
        ops.append({"name": "CX", "qubits": [ctrl, target], "params": {}})
    ops.append({"name": "RZ", "qubits": [target], "params": {"theta": float(phi)}})
    for ctrl in reversed(support[1:]):
        ops.append({"name": "CX", "qubits": [ctrl, target], "params": {}})
    for q in reversed(support):
        p = pauli_string[q]
        if p == "X":
            ops.append({"name": "H", "qubits": [q], "params": {}})
        elif p == "Y":
            ops.extend(
                [
                    {"name": "H", "qubits": [q], "params": {}},
                    {"name": "SDG", "qubits": [q], "params": {}},
                ]
            )
    return ops


def pauli_rotation_ops(
    pauli_string: str,
    phi: float,
    *,
    emit_mode: Literal["elementary", "pauli_rotation"] = "elementary",
) -> list[dict[str, Any]]:
    if emit_mode == "pauli_rotation":
        return [
            {
                "name": "PAULI_ROTATION",
                "qubits": list(range(len(pauli_string))),
                "params": {"pauli_string": pauli_string, "phi": float(phi)},
            }
        ]
    return pauli_rotation_elementary_ops(pauli_string, phi)


def cluster_layer_ops(
    antiherm: np.ndarray,
    angle: float,
    n_qubits: int,
    *,
    emit_mode: Literal["elementary", "pauli_rotation"] = "elementary",
    layer: int = 0,
    generator_index: int = 0,
) -> list[dict[str, Any]]:
    """CircuitIR ops for one cluster exponential ``expm(angle * A)``."""
    terms = decompose_antihermitian_to_pauli_terms(antiherm, n_qubits)
    ops: list[dict[str, Any]] = []
    for ps, coeff in terms:
        phi = pauli_rotation_angle_from_cluster(angle, coeff)
        if abs(phi) < 1e-15:
            continue
        for op in pauli_rotation_ops(ps, phi, emit_mode=emit_mode):
            tagged = dict(op)
            tagged.setdefault("params", {})
            tagged["params"] = dict(tagged["params"])
            tagged["params"]["cluster_layer"] = int(layer)
            tagged["params"]["generator_index"] = int(generator_index)
            ops.append(tagged)
    return ops


def apply_pauli_rotation_statevector(
    state: np.ndarray,
    pauli_string: str,
    phi: float,
) -> np.ndarray:
    """Apply ``exp(-i phi/2 P)`` to ``state``."""
    p = pauli_matrix(pauli_string)
    u = expm(-0.5j * float(phi) * p)
    return cast("np.ndarray", u @ state)


def apply_cluster_expm_statevector(
    state: np.ndarray,
    antiherm: np.ndarray,
    angle: float,
    n_qubits: int,
) -> np.ndarray:
    u = cluster_expm_via_pauli_product(antiherm, angle, n_qubits)
    out = u @ state
    nrm = float(np.linalg.norm(out))
    if nrm < 1e-14:
        raise ValueError("UCCSD Pauli cluster layer collapsed state to zero norm.")
    return cast("np.ndarray", out / nrm)


__all__ = [
    "DecompositionMode",
    "apply_cluster_expm_statevector",
    "apply_pauli_rotation_statevector",
    "cluster_expm_via_pauli_product",
    "cluster_layer_ops",
    "decompose_antihermitian_to_pauli_terms",
    "pauli_rotation_angle_from_cluster",
    "pauli_rotation_elementary_ops",
    "pauli_rotation_ops",
]
