"""Circuit evaluation oracle for GQE token sequences."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.quantum.algorithms.tolerances import NUMERICAL_TOLERANCE, STATE_NORMALIZATION_FLOOR
from qchem_stack.quantum.statevector import expectation_qubit_operator

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.quantum.algorithms.gqe.types import PoolToken


def default_reference_state(n_qubits: int, n_electrons: int | None = None) -> np.ndarray:
    """Hartree–Fock-like computational-basis reference (lowest orbitals occupied)."""
    dim = 2**n_qubits
    psi = np.zeros(dim, dtype=np.complex128)
    if n_electrons is None:
        psi[0] = 1.0
        return psi
    ne = max(0, min(int(n_electrons), n_qubits))
    # JW: bit i set means spin-orbital i occupied; occupy 0..ne-1.
    idx = 0
    for i in range(ne):
        idx |= 1 << (n_qubits - 1 - i)
    psi[idx] = 1.0
    return psi


def prepare_state_from_sequence(
    sequence: list[int] | np.ndarray,
    unitaries: list[np.ndarray],
    reference: np.ndarray,
) -> np.ndarray:
    """Apply ``U(j_N)...U(j_1)`` (right-to-left generation order = left-to-right apply)."""
    psi = np.asarray(reference, dtype=np.complex128).ravel().copy()
    for j in sequence:
        u = unitaries[int(j)]
        psi = u @ psi
        nrm = float(np.linalg.norm(psi))
        if nrm < NUMERICAL_TOLERANCE:
            raise ValueError("GQE state collapsed to zero norm.")
        psi = psi / max(nrm, STATE_NORMALIZATION_FLOOR)
    return psi


def energy_of_sequence(
    sequence: list[int] | np.ndarray,
    *,
    unitaries: list[np.ndarray],
    reference: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
) -> float:
    psi = prepare_state_from_sequence(sequence, unitaries, reference)
    return float(np.real(expectation_qubit_operator(psi, hamiltonian, n_qubits)))


def prefix_energies(
    sequence: list[int] | np.ndarray,
    *,
    unitaries: list[np.ndarray],
    reference: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
) -> list[float]:
    """Per-prefix energies for SpinGQE WMSE (A7)."""
    psi = np.asarray(reference, dtype=np.complex128).ravel().copy()
    out: list[float] = []
    for j in sequence:
        u = unitaries[int(j)]
        psi = u @ psi
        nrm = float(np.linalg.norm(psi))
        psi = psi / max(nrm, STATE_NORMALIZATION_FLOOR)
        out.append(float(np.real(expectation_qubit_operator(psi, hamiltonian, n_qubits))))
    return out


def qsci_energy_of_sequence(
    sequence: list[int] | np.ndarray,
    *,
    unitaries: list[np.ndarray],
    reference: np.ndarray,
    hamiltonian_matrix: np.ndarray,
    subspace_size: int = 8,
) -> float:
    """QSCI-style reward (A4/A6): diagonalize H in top-|amp| computational basis."""
    psi = prepare_state_from_sequence(sequence, unitaries, reference)
    probs = np.abs(psi) ** 2
    k = max(1, min(int(subspace_size), probs.size))
    idxs = np.argpartition(probs, -k)[-k:]
    idxs = idxs[np.argsort(probs[idxs])[::-1]]
    h_sub = hamiltonian_matrix[np.ix_(idxs, idxs)]
    evals = np.linalg.eigvalsh(np.asarray(h_sub, dtype=np.complex128))
    return float(np.real(evals[0]))


def sequence_qcc_cost(sequence: list[int] | np.ndarray, tokens: list[PoolToken]) -> float:
    return float(sum(tokens[int(j)].qcc_cost for j in sequence))
