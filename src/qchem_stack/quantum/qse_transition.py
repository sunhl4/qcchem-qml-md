"""QSE matrix elements ``\\langle \\phi_i | c_P P | \\phi_j \\rangle`` and shot bookkeeping.

Each off-diagonal ``H_{ij}`` is a sum over Hamiltonian Pauli terms; ``S_{ij}`` uses exact overlap
(identity / inner product) for numerical stability.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from openfermion.ops import QubitOperator
from scipy.linalg import eigh

from qchem_stack.quantum.statevector import qubit_operator_to_sparse


def transition_pauli_amplitude(
    phi_left: np.ndarray,
    phi_right: np.ndarray,
    pauli_term: tuple[tuple[int, str], ...],
    n_qubits: int,
) -> complex:
    """``\\langle \\phi_{\\mathrm{left}} | P | \\phi_{\\mathrm{right}} \\rangle`` for a single Pauli word."""
    if len(pauli_term) == 0:
        return np.vdot(phi_left, phi_right)
    op = qubit_operator_to_sparse(QubitOperator(pauli_term, 1.0), n_qubits)
    return np.vdot(phi_left, op @ phi_right)


def hamiltonian_transition_amplitude(
    phi_left: np.ndarray,
    phi_right: np.ndarray,
    h: QubitOperator,
    n_qubits: int,
) -> complex:
    """``\\langle \\phi_l | H | \\phi_r \\rangle``."""
    acc = 0j
    for term, c in h.terms.items():
        if len(term) == 0:
            acc += complex(c) * np.vdot(phi_left, phi_right)
        else:
            acc += complex(c) * transition_pauli_amplitude(phi_left, phi_right, term, n_qubits)
    return acc


def qse_h_s_matrices_exact(
    basis: list[np.ndarray],
    h: QubitOperator,
    n_qubits: int,
) -> tuple[np.ndarray, np.ndarray]:
    k = len(basis)
    h_mat = np.zeros((k, k), dtype=complex)
    s_mat = np.zeros((k, k), dtype=complex)
    for i in range(k):
        for j in range(k):
            s_mat[i, j] = np.vdot(basis[i], basis[j])
            h_mat[i, j] = hamiltonian_transition_amplitude(basis[i], basis[j], h, n_qubits)
    return h_mat, s_mat


def qse_h_matrix_transition_shots(
    basis: list[np.ndarray],
    h: QubitOperator,
    n_qubits: int,
    *,
    shots_per_ij_term: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """Independent Gaussian noise on each (i,j, Pauli-term) contribution; then Hermitian symmetrize ``H``."""
    k = len(basis)
    s_mat = np.zeros((k, k), dtype=complex)
    for i in range(k):
        for j in range(k):
            s_mat[i, j] = np.vdot(basis[i], basis[j])
    h_acc = np.zeros((k, k), dtype=complex)
    records: list[dict[str, Any]] = []
    scale_base = 1.0 / math.sqrt(max(1, shots_per_ij_term))
    for i in range(k):
        for j in range(k):
            for term, c in h.terms.items():
                c = complex(c)
                if len(term) == 0:
                    h_acc[i, j] += c * s_mat[i, j]
                    continue
                mu = transition_pauli_amplitude(basis[i], basis[j], term, n_qubits)
                val = c * mu
                sig = abs(c) * scale_base
                noise_r = rng.normal(0.0, sig)
                noise_i = rng.normal(0.0, sig)
                h_acc[i, j] += val + noise_r + 1j * noise_i
                records.append(
                    {
                        "i": i,
                        "j": j,
                        "pauli_term": str(term),
                        "shots_budget": shots_per_ij_term,
                        "noise_model": "independent_complex_gaussian_per_term",
                    }
                )
    h_sym = (h_acc + np.conj(h_acc.T)) / 2.0
    return h_sym, s_mat, records


@dataclass
class QSEPauliTransitionSchedule:
    """Serializable schedule for QSE Pauli transition tasks (parity / resource tables)."""

    n_qubits: int
    subspace_dim: int
    n_pauli_terms: int
    n_transition_tasks: int
    shots_per_ij_term: int
    grouping_note: str = "no_cross_transition_grouping_independent_terms"
    records: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_shots_budget_upper_bound(self) -> int:
        return self.n_transition_tasks * self.shots_per_ij_term


def build_qse_transition_schedule(
    h: QubitOperator,
    k: int,
    n_qubits: int,
    *,
    shots_per_ij_term: int,
    records: list[dict[str, Any]],
) -> QSEPauliTransitionSchedule:
    n_terms = len([t for t in h.terms if len(t) > 0])
    n_tasks = len(records)
    return QSEPauliTransitionSchedule(
        n_qubits=n_qubits,
        subspace_dim=k,
        n_pauli_terms=n_terms,
        n_transition_tasks=n_tasks,
        shots_per_ij_term=shots_per_ij_term,
        records=records,
    )


def solve_qse_ghep(h_mat: np.ndarray, s_mat: np.ndarray) -> tuple[np.ndarray, list[float]]:
    evals, _ = eigh(np.real(h_mat), np.real(s_mat))
    evals = np.sort(np.real(evals))
    e0 = float(evals[0])
    exc = [float(evals[t] - e0) for t in range(1, len(evals))]
    return evals, exc
