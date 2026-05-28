"""Shared QSE matrix construction and GHEP solve paths."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import numpy as np  # noqa: TC002
from openfermion.ops import QubitOperator  # noqa: TC002
from scipy.linalg import eigh

from qchem_stack.quantum.qse_transition import (
    build_qse_transition_schedule,
    solve_qse_ghep,
)
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.quantum.algorithms.qse_basis_strategies import QSEBasisStrategy


def qse_matrices_hs(
    h_op: QubitOperator,
    n_qubits: int,
    basis: list[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    """Hermitian H_ij = <phi_i|H|phi_j>, S_ij = <phi_i|phi_j> (``arXiv:1603.05681`` Galerkin)."""
    h_mat = qubit_operator_to_sparse(h_op, n_qubits)
    k = len(basis)
    h_sub = np.zeros((k, k), dtype=complex)
    s_sub = np.zeros((k, k), dtype=complex)
    for i in range(k):
        for j in range(k):
            s_sub[i, j] = np.vdot(basis[i], basis[j])
            h_sub[i, j] = np.vdot(basis[i], h_mat @ basis[j])
    return h_sub, s_sub


def qse_h_s_via_computable(
    basis: list[np.ndarray],
    h_op: QubitOperator,
    n_qubits: int,
    *,
    shot_mode: str,
    shots_per_ij_term: int,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, list[Any]]:
    from qchem_stack.protocols.computables.base import EvaluationContext
    from qchem_stack.protocols.computables.qse_matrices import QSEMatricesComputable

    comp = QSEMatricesComputable(
        name="qse_h_s",
        hamiltonian=h_op,
        n_qubits=n_qubits,
        basis=basis,
        shot_mode=str(shot_mode),
        shots_per_ij_term=int(shots_per_ij_term),
    )
    ctx = EvaluationContext(angles=np.zeros(0, dtype=float), rng=rng)
    out = comp.evaluate(ctx)
    records = out.meta.get("transition_records") or []
    return out.value["H"], out.value["S"], list(records)


def s_condition_number(s_mat: np.ndarray) -> float:
    svals = np.linalg.svd(np.real(s_mat), compute_uv=False)
    return float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")


def excitation_energies_dense(
    h_op: QubitOperator,
    n_qubits: int,
    basis: list[np.ndarray],
) -> tuple[list[float], np.ndarray, np.ndarray]:
    h_sub, s_sub = qse_matrices_hs(h_op, n_qubits, basis)
    evals, _ = eigh(h_sub, s_sub)
    evals = np.sort(np.real(evals))
    e0 = float(evals[0])
    exc = [float(evals[i] - e0) for i in range(1, len(evals))]
    return exc, h_sub, s_sub


def excitation_energies_shot_noise(
    h_op: QubitOperator,
    n_qubits: int,
    basis: list[np.ndarray],
    *,
    shots_per_matrix_element: int,
    rng: np.random.Generator,
) -> tuple[list[float], np.ndarray]:
    h_sub, s_sub = qse_matrices_hs(h_op, n_qubits, basis)
    h_real = np.real(h_sub)
    scale = 1.0 / math.sqrt(max(1, shots_per_matrix_element))
    noise = rng.normal(0.0, scale, h_real.shape)
    noise = (noise + noise.T) / 2.0
    h_noisy = h_real + noise
    s_real = np.real(s_sub)
    evals, _ = eigh(h_noisy, s_real)
    evals = np.sort(np.real(evals))
    e0 = float(evals[0])
    exc = [float(evals[i] - e0) for i in range(1, len(evals))]
    return exc, s_sub


def excitation_energies_pauli_transitions(
    h_op: QubitOperator,
    n_qubits: int,
    basis: list[np.ndarray],
    *,
    shots_per_ij_term: int,
    shot_mode: str,
    rng: np.random.Generator | None = None,
) -> tuple[list[float], np.ndarray, dict[str, Any]]:
    h_sym, s_mat, records = qse_h_s_via_computable(
        basis,
        h_op,
        n_qubits,
        shot_mode=shot_mode,
        shots_per_ij_term=shots_per_ij_term,
        rng=rng,
    )
    sched = build_qse_transition_schedule(
        h_op,
        len(basis),
        n_qubits,
        shots_per_ij_term=shots_per_ij_term,
        records=records,
    )
    _, exc = solve_qse_ghep(h_sym, s_mat)
    schedule_meta = {
        "n_qubits": sched.n_qubits,
        "subspace_dim": sched.subspace_dim,
        "n_pauli_terms": sched.n_pauli_terms,
        "n_transition_tasks": sched.n_transition_tasks,
        "total_shots_upper_bound": sched.total_shots_budget_upper_bound,
    }
    return exc, s_mat, schedule_meta


def build_basis_from_strategy(
    strategy: QSEBasisStrategy,
    angles: np.ndarray,
    hamiltonian: Any,
    *,
    max_basis: int,
    **kwargs: Any,
) -> list[np.ndarray]:
    return strategy.build(angles, hamiltonian, max_basis=max_basis, **kwargs)
