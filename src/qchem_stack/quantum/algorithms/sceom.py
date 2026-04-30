"""SCEOM / q-sc-EOM (Chemical Science D2SC05371C): reference subspace + nested-commutator ``M`` matrix.

Use :func:`run_sceom_nested_commutator` for ``M_{ij}=\\langle\\psi|[S_i^\\dagger,[H,S_j]]|\\psi\\rangle`` with
Pauli toy generators; :func:`run_sceom_reference_subspace` remains a separate numerical anchor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.linalg import eigh

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.excited import qse_matrices_hs
from qchem_stack.quantum.statevector import expectation_qubit_operator, hea_state, qubit_operator_to_sparse


@dataclass
class SCEOMResult:
    """Low-lying energies in a *correlated* subspace spanned by exact eigenvectors (reference only)."""

    energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


def run_sceom_reference_subspace(
    hamiltonian: QubitHamiltonian,
    *,
    subspace_dim: int = 4,
) -> SCEOMResult:
    """Diagonalize full H, take lowest-``subspace_dim`` eigenvectors as correlated basis, then rediagonalize.

    This is **not** the full shot-based ``M`` matrix from `Chem. Sci. D2SC05371C`, but provides a
    **numerical anchor** for small systems until SCEOM matrix protocols are implemented.
    """
    n = hamiltonian.n_qubits
    h_full = qubit_operator_to_sparse(hamiltonian.operator, n)
    w, vecs = eigh(h_full)
    order = np.argsort(np.real(w))
    k = min(subspace_dim, len(order))
    basis = [vecs[:, order[i]].ravel() for i in range(k)]
    h_sub, s_sub = qse_matrices_hs(hamiltonian.operator, n, basis)
    evals, _ = eigh(h_sub, s_sub)
    evals = np.sort(np.real(evals))
    return SCEOMResult(
        energies=[float(x) for x in evals],
        meta={
            "reference": "10.1039/D2SC05371C (SCEOM — here: eigenvector-subspace reference only)",
            "subspace_dim": k,
            "implementation_note": "correlated_basis=lowest_exact_eigenvectors_then_rediagonalize",
        },
    )


def run_sceom_reference_subspace_shot_noise(
    hamiltonian: QubitHamiltonian,
    *,
    subspace_dim: int = 4,
    shots_per_matrix_element: int = 4096,
    seed: int = 0,
) -> SCEOMResult:
    """Same correlated basis as :func:`run_sceom_reference_subspace`, Gaussian noise on ``real(H_sub)`` (placeholder)."""
    rng = np.random.default_rng(seed)
    n = hamiltonian.n_qubits
    h_full = qubit_operator_to_sparse(hamiltonian.operator, n)
    w, vecs = eigh(h_full)
    order = np.argsort(np.real(w))
    k = min(subspace_dim, len(order))
    basis = [vecs[:, order[i]].ravel() for i in range(k)]
    h_sub, s_sub = qse_matrices_hs(hamiltonian.operator, n, basis)
    scale = 1.0 / math.sqrt(max(1, shots_per_matrix_element))
    noise = rng.normal(0.0, scale, np.real(h_sub).shape)
    noise = (noise + noise.T) / 2.0
    h_noisy = np.real(h_sub) + noise
    evals, _ = eigh(h_noisy, np.real(s_sub))
    evals = np.sort(np.real(evals))
    return SCEOMResult(
        energies=[float(x) for x in evals],
        meta={
            "reference": "10.1039/D2SC05371C (SCEOM — shot noise on H_sub only, not true M-matrix)",
            "subspace_dim": k,
            "shot_noise_model": "symmetric_gaussian_on_real_H_sub",
            "shots_per_matrix_element": shots_per_matrix_element,
        },
    )


@dataclass
class SCEOMPlaceholder:
    """Deprecated name — use :func:`run_sceom_reference_subspace`."""

    note: str = "Use run_sceom_reference_subspace(hamiltonian, subspace_dim=...)."


def nested_sceom_q_sc_eom_operator(h: QubitOperator, si: QubitOperator, sj: QubitOperator) -> QubitOperator:
    """``[S_i^\\dagger, [H, S_j]]`` for q-sc-EOM (Chemical Science, D2SC05371C / arXiv:2206.10502)."""
    comm = h * sj - sj * h
    return si * comm - comm * si


def default_sceom_pauli_generators(n_qubits: int, k: int) -> list[QubitOperator]:
    """Toy excitation operators: identity + single-qubit :math:`X_a` (not full fermionic pool)."""
    ops: list[QubitOperator] = [QubitOperator((), 1.0)]
    for q in range(n_qubits):
        if len(ops) >= k:
            break
        ops.append(QubitOperator(((q, "X"),), 1.0))
    while len(ops) < k:
        ops.append(QubitOperator((), 1.0))
    return ops[:k]


def run_sceom_nested_commutator(
    hamiltonian: QubitHamiltonian,
    reference_state: np.ndarray,
    *,
    s_generators: list[QubitOperator] | None = None,
    subspace_dim: int | None = None,
    shots_per_matrix_element: int = 0,
    seed: int = 0,
) -> SCEOMResult:
    """Build ``M_{ij} = \\langle\\psi|[S_i^\\dagger,[H,S_j]]|\\psi\\rangle`` and diagonalize (``V\\approx I`` toy)."""
    n = hamiltonian.n_qubits
    ref = np.asarray(reference_state, dtype=complex).ravel()
    ref = ref / (np.linalg.norm(ref) + 1e-15)
    k_target = subspace_dim or 4
    s_ops = s_generators or default_sceom_pauli_generators(n, k_target)
    k = len(s_ops)
    m_mat = np.zeros((k, k), dtype=float)
    task_meta: list[dict[str, Any]] = []
    for i in range(k):
        for j in range(k):
            op = nested_sceom_q_sc_eom_operator(hamiltonian.operator, s_ops[i], s_ops[j])
            val = expectation_qubit_operator(ref, op, n)
            m_mat[i, j] = float(np.real(val))
            task_meta.append({"i": i, "j": j, "n_operator_terms": len(op.terms)})
    m_mat = (m_mat + m_mat.T) / 2.0
    if shots_per_matrix_element > 0:
        rng = np.random.default_rng(seed)
        scale = 1.0 / math.sqrt(max(1, shots_per_matrix_element))
        nz = rng.normal(0.0, scale, m_mat.shape)
        nz = (nz + nz.T) / 2.0
        m_mat = m_mat + nz
    evals, _ = eigh(m_mat)
    evals = np.sort(np.real(evals))
    return SCEOMResult(
        energies=[float(x) for x in evals],
        meta={
            "reference": "10.1039/D2SC05371C (q-sc-EOM M matrix; nested commutator)",
            "subspace_dim": k,
            "construction": "M_ij=<psi|[Si,[H,Sj]]|psi> with Pauli toy generators",
            "tasking": task_meta[: min(8, len(task_meta))],
            "shot_noise_model": "symmetric_gaussian_on_real_M"
            if shots_per_matrix_element > 0
            else "none",
            "shots_per_matrix_element": shots_per_matrix_element,
        },
    )


def run_sceom_nested_commutator_from_hea(
    hamiltonian: QubitHamiltonian,
    angles: np.ndarray,
    depth: int,
    **kwargs: Any,
) -> SCEOMResult:
    """Reference = HEA state ``|psi(theta)\\rangle`` (same ansatz as pipeline VQE)."""
    ref = hea_state(np.asarray(angles, dtype=float), hamiltonian.n_qubits, depth)
    return run_sceom_nested_commutator(hamiltonian, ref, **kwargs)
