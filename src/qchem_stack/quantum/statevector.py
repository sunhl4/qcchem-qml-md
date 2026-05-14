from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator


def _pauli_char_to_mat(c: str) -> np.ndarray:
    if c == "I":
        return np.eye(2, dtype=complex)
    if c == "X":
        return np.array([[0, 1], [1, 0]], dtype=complex)
    if c == "Y":
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    if c == "Z":
        return np.array([[1, 0], [0, -1]], dtype=complex)
    raise ValueError(c)


def _kron_n(mats: list[np.ndarray]) -> np.ndarray:
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out


def qubit_operator_to_sparse(h: QubitOperator, n_qubits: int) -> np.ndarray:
    """Dense matrix (warning: 2^n)."""
    dim = 2**n_qubits
    acc = np.zeros((dim, dim), dtype=complex)
    for term, coeff in h.terms.items():
        if len(term) == 0:
            acc += float(np.real(coeff)) * np.eye(dim, dtype=complex)
            continue
        mats = ["I"] * n_qubits
        for idx, p in term:
            mats[idx] = p
        acc += coeff * _kron_n([_pauli_char_to_mat(c) for c in mats])
    return acc


def expectation_qubit_operator(state: np.ndarray, h: QubitOperator, n_qubits: int) -> complex:
    """``<psi|H|psi>`` for normalized ``state``."""
    op = qubit_operator_to_sparse(h, n_qubits)
    return np.vdot(state, op @ state)


def hea_state(
    angles: np.ndarray,
    n_qubits: int,
    depth: int,
    entangler: str = "linear_cnot",
) -> np.ndarray:
    """Hardware-efficient ansatz: layers of Ry/Rx + CNOT chain."""
    state = np.zeros(2**n_qubits, dtype=complex)
    state[0] = 1.0
    n_params = 2 * n_qubits * depth
    if angles.size != n_params:
        raise ValueError(f"expected {n_params} angles, got {angles.size}")
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            th = angles[k]
            k += 1
            ry_m = np.array(
                [[np.cos(th / 2), -np.sin(th / 2)], [np.sin(th / 2), np.cos(th / 2)]],
                dtype=complex,
            )
            state = _apply_one_qubit_unitary(state, ry_m, q, n_qubits)
            th2 = angles[k]
            k += 1
            rx_m = np.array(
                [
                    [np.cos(th2 / 2), -1j * np.sin(th2 / 2)],
                    [-1j * np.sin(th2 / 2), np.cos(th2 / 2)],
                ],
                dtype=complex,
            )
            state = _apply_one_qubit_unitary(state, rx_m, q, n_qubits)
        if entangler == "linear_cnot":
            for q in range(n_qubits - 1):
                state = _apply_cnot(state, q, q + 1, n_qubits)
    return state / np.linalg.norm(state)


def _apply_one_qubit_unitary(
    state: np.ndarray, u2: np.ndarray, target: int, n_qubits: int
) -> np.ndarray:
    dim = 2**n_qubits
    st = state.reshape((2,) * n_qubits)
    st = np.moveaxis(st, target, 0)
    new = np.tensordot(u2, st, axes=(1, 0))
    new = np.moveaxis(new, 0, target)
    return new.reshape(dim)


def _apply_cnot(state: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    """CNOT with ``control``/``target`` as **tensor axes** (same indices as ``_apply_one_qubit_unitary``)."""
    dim = 2**n_qubits
    out = np.zeros_like(state)
    shape = (2,) * n_qubits
    for i in range(dim):
        idx = list(np.unravel_index(i, shape))
        if idx[control] == 1:
            idx[target] ^= 1
        j = int(np.ravel_multi_index(idx, shape))
        out[j] += state[i]
    return out


def apply_excitation_simple(
    state: np.ndarray, i: int, j: int, n_qubits: int, angle: float
) -> np.ndarray:
    """Apply ``exp(i * angle * X_i X_j)`` (toy pool generator for small demos)."""
    from scipy.linalg import expm

    xi = _kron_single(n_qubits, i, "X")
    xj = _kron_single(n_qubits, j, "X")
    u = expm(1j * angle * (xi @ xj))
    return u @ state


def _kron_single(n_qubits: int, q: int, p: str) -> np.ndarray:
    mats = [_pauli_char_to_mat("I")] * n_qubits
    mats[q] = _pauli_char_to_mat(p)
    return _kron_n(mats)
