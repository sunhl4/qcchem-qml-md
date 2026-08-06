from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, cast

import numpy as np

from qchem_stack.quantum.algorithms.tolerances import STATE_NORMALIZATION_FLOOR

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


@lru_cache(maxsize=4)
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
    """Convert ``QubitOperator`` to a dense matrix via sparse intermediate.

    Uses ``openfermion.get_sparse_operator`` for efficient sparse construction,
    then converts to dense ``np.ndarray`` for downstream compatibility.
    For sparse Hamiltonians this avoids the O(n_terms * 2^(2n)) cost of
    iterated dense kron products.
    """
    from openfermion import get_sparse_operator

    return np.asarray(get_sparse_operator(h, n_qubits=n_qubits).toarray())


def expectation_qubit_operator(state: np.ndarray, h: QubitOperator, n_qubits: int) -> complex:
    """``<psi|H|psi>`` for normalized ``state``."""
    op = qubit_operator_to_sparse(h, n_qubits)
    return complex(np.vdot(state, op @ state))


def hea_state(
    angles: np.ndarray,
    n_qubits: int,
    depth: int,
    entangler: str = "linear_cnot",
    *,
    initial_state: np.ndarray | None = None,
) -> np.ndarray:
    """Hardware-efficient ansatz: layers of Ry/Rx + CNOT chain.

    When ``initial_state`` is provided it must be length ``2**n_qubits`` and is
    used as the reference (e.g. Hartree–Fock) before HEA unitaries are applied.
    """
    if initial_state is None:
        state = np.zeros(2**n_qubits, dtype=complex)
        state[0] = 1.0
    else:
        state = np.asarray(initial_state, dtype=complex).ravel().copy()
        if state.size != 2**n_qubits:
            raise ValueError(
                f"initial_state length {state.size} != 2**n_qubits ({2**n_qubits})"
            )
        nrm0 = float(np.linalg.norm(state))
        if nrm0 < STATE_NORMALIZATION_FLOOR:
            raise ValueError("initial_state has near-zero norm")
        state = state / nrm0
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
    norm = np.linalg.norm(state)
    return cast("np.ndarray", state / max(norm, STATE_NORMALIZATION_FLOOR))


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
    """CNOT with ``control``/``target`` as **tensor axes** (same indices as ``_apply_one_qubit_unitary``).

    Vectorized tensor-slicing implementation: moves control/target to the first
    two axes, swaps the target slices where control==1, then restores the
    original axis ordering.  This replaces the O(2^n) Python-level loop with
    pure C-level NumPy operations (~100-1000x speedup for 10-20 qubits).
    """
    tensor = state.reshape((2,) * n_qubits)
    t = np.moveaxis(tensor, [control, target], [0, 1])
    r = t.copy()
    r[1, 0] = t[1, 1]
    r[1, 1] = t[1, 0]
    return np.moveaxis(r, [0, 1], [control, target]).reshape(-1)


def apply_excitation_simple(
    state: np.ndarray, i: int, j: int, n_qubits: int, angle: float
) -> np.ndarray:
    """Apply ``exp(i * angle * X_i X_j)`` (toy pool generator for small demos)."""
    from scipy.linalg import expm

    xi = _kron_single(n_qubits, i, "X")
    xj = _kron_single(n_qubits, j, "X")
    u = expm(1j * angle * (xi @ xj))
    return cast("np.ndarray", u @ state)


def _kron_single(n_qubits: int, q: int, p: str) -> np.ndarray:
    mats = [_pauli_char_to_mat("I")] * n_qubits
    mats[q] = _pauli_char_to_mat(p)
    return _kron_n(mats)
