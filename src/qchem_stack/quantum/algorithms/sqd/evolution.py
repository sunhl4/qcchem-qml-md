"""Krylov / qDRIFT time-evolution helpers for SKQD and SqDRIFT."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.linalg import expm

from qchem_stack.quantum.algorithms.tolerances import STATE_NORMALIZATION_FLOOR
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


def trotter_step_state(
    state: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
    dt: float,
) -> np.ndarray:
    """Exact dense ``exp(-i H dt) |psi>`` (toy-scale; name is historical).

    Epistemic bound: not a NISQ Trotter product formula — used by SKQD-lite as
    an exact Krylov power on small systems.
    """
    h = qubit_operator_to_sparse(hamiltonian, n_qubits)
    u = expm(-1j * float(dt) * h)
    out = u @ np.asarray(state, dtype=np.complex128).ravel()
    nrm = float(np.linalg.norm(out))
    return out / max(nrm, STATE_NORMALIZATION_FLOOR)


def krylov_states(
    reference: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
    *,
    krylov_dim: int,
    dt: float,
) -> list[np.ndarray]:
    states = [np.asarray(reference, dtype=np.complex128).ravel()]
    psi = states[0]
    for _ in range(max(0, int(krylov_dim) - 1)):
        psi = trotter_step_state(psi, hamiltonian, n_qubits, dt)
        states.append(psi)
    return states


def pauli_terms_with_weights(
    hamiltonian: QubitOperator,
) -> list[tuple[QubitOperator, float]]:
    from openfermion.ops import QubitOperator as QO

    terms: list[tuple[QubitOperator, float]] = []
    for term, coeff in hamiltonian.terms.items():
        c = complex(coeff)
        w = abs(c)
        if w <= 0.0:
            continue
        terms.append((QO(term, c), w))
    return terms


def qdrift_channel_state(
    state: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
    *,
    time: float,
    n_steps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """One qDRIFT random product approximating ``exp(-i H t)``."""
    terms = pauli_terms_with_weights(hamiltonian)
    if not terms:
        return np.asarray(state, dtype=np.complex128).ravel()
    weights = np.asarray([w for _, w in terms], dtype=float)
    lam = float(weights.sum())
    probs = weights / lam
    tau = float(time) * lam / max(int(n_steps), 1)
    psi = np.asarray(state, dtype=np.complex128).ravel()
    for _ in range(max(1, int(n_steps))):
        idx = int(rng.choice(len(terms), p=probs))
        op, _w = terms[idx]
        mat = qubit_operator_to_sparse(op, n_qubits)
        # Hermitize lightly for numerical stability
        mat = 0.5 * (mat + mat.conj().T)
        psi = expm(-1j * tau * mat) @ psi
        nrm = float(np.linalg.norm(psi))
        psi = psi / max(nrm, STATE_NORMALIZATION_FLOOR)
    return psi
