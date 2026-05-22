"""Quantum subspace expansion (QSE)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import eigh

from qchem_stack.quantum.qse_transition import (
    build_qse_transition_schedule,
    qse_h_matrix_transition_grouped_pauli_shots,
    solve_qse_ghep,
)
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

from .excited_basis import build_qse_basis_from_uccsd_reference, build_qse_basis_from_vqe_hea

if TYPE_CHECKING:
    from collections.abc import Callable

    from openfermion.ops import QubitOperator

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


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


@dataclass
class QSEResult:
    excitation_energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class QSE:
    """Quantum subspace expansion: ``arXiv:1603.05681`` Galerkin on a small basis, plus dense spectral reference."""

    def __init__(self, hamiltonian: QubitHamiltonian, subspace_dim: int = 4) -> None:
        self.hamiltonian = hamiltonian
        self.subspace_dim = min(subspace_dim, 2**hamiltonian.n_qubits)

    def run_dense_reference(self) -> QSEResult:
        """Full Hilbert diagonalization (tiny systems only): excitation energies from exact spectrum."""
        h = qubit_operator_to_sparse(self.hamiltonian.operator, self.hamiltonian.n_qubits)
        w, _ = eigh(h)
        w = np.sort(np.real(w))
        e0 = float(w[0])
        exc = [float(w[i] - e0) for i in range(1, min(self.subspace_dim, len(w)))]
        return QSEResult(excitation_energies=exc, meta={"method": "full_dense_subspace"})

    def run(self) -> QSEResult:
        return self.run_dense_reference()

    def run_from_vqe_hea_basis(
        self,
        angles: np.ndarray,
        depth: int,
        *,
        max_basis: int | None = None,
    ) -> QSEResult:
        """Build orthonormal micro-basis from VQE+Pauli-X bumps; solve ``H c = E S c``."""
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_vqe_hea(angles, self.hamiltonian.n_qubits, depth, max_basis=kb)
        h_sub, s_sub = qse_matrices_hs(self.hamiltonian.operator, self.hamiltonian.n_qubits, basis)
        evals, _ = eigh(h_sub, s_sub)
        evals = np.sort(np.real(evals))
        e0 = float(evals[0])
        exc = [float(evals[i] - e0) for i in range(1, len(evals))]
        svals = np.linalg.svd(np.real(s_sub), compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "K_raw": int(self.hamiltonian.n_qubits + 1),
                "linear_dependencies_removed": int(
                    max(0, self.hamiltonian.n_qubits + 1 - len(basis))
                ),
                "H_sub_shape": list(h_sub.shape),
                "S_condition_number": cond_s,
            },
        )

    def run_from_vqe_hea_basis_shot_noise(
        self,
        angles: np.ndarray,
        depth: int,
        *,
        max_basis: int | None = None,
        shots_per_matrix_element: int = 4096,
        seed: int = 0,
    ) -> QSEResult:
        """Symmetric Gaussian noise on ``real(H_sub)`` before GHEP (placeholder; not per-Pauli shot budget)."""
        rng = np.random.default_rng(seed)
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_vqe_hea(angles, self.hamiltonian.n_qubits, depth, max_basis=kb)
        h_sub, s_sub = qse_matrices_hs(self.hamiltonian.operator, self.hamiltonian.n_qubits, basis)
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
        svals = np.linalg.svd(s_real, compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "shot_noise_model": "symmetric_gaussian_on_real_H_matrix",
                "shots_per_matrix_element": shots_per_matrix_element,
                "S_condition_number": cond_s,
            },
        )

    def run_from_vqe_hea_basis_pauli_transitions(
        self,
        angles: np.ndarray,
        depth: int,
        *,
        max_basis: int | None = None,
        shots_per_ij_term: int = 512,
        seed: int = 0,
    ) -> QSEResult:
        """Per-(i,j,Pauli-term) grouped statevector shots; ``S`` exact; schedule for parity tables."""
        rng = np.random.default_rng(seed)
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_vqe_hea(angles, self.hamiltonian.n_qubits, depth, max_basis=kb)
        h_sym, s_mat, records = qse_h_matrix_transition_grouped_pauli_shots(
            basis,
            self.hamiltonian.operator,
            self.hamiltonian.n_qubits,
            shots_per_ij_term=shots_per_ij_term,
            rng=rng,
        )
        sched = build_qse_transition_schedule(
            self.hamiltonian.operator,
            len(basis),
            self.hamiltonian.n_qubits,
            shots_per_ij_term=shots_per_ij_term,
            records=records,
        )
        _, exc = solve_qse_ghep(h_sym, s_mat)
        svals = np.linalg.svd(np.real(s_mat), compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "shot_noise_model": "grouped_statevector_shot_simulation_per_ij_term",
                "shots_per_ij_term": shots_per_ij_term,
                "S_condition_number": cond_s,
                "qse_pauli_transition_schedule": {
                    "n_qubits": sched.n_qubits,
                    "subspace_dim": sched.subspace_dim,
                    "n_pauli_terms": sched.n_pauli_terms,
                    "n_transition_tasks": sched.n_transition_tasks,
                    "total_shots_upper_bound": sched.total_shots_budget_upper_bound,
                },
            },
        )

    def run_from_uccsd_basis(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
    ) -> QSEResult:
        """Build orthonormal micro-basis from UCCSD reference + mapped fermionic singles."""
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_uccsd_reference(
            angles,
            self.hamiltonian,
            prepare_state,
            max_basis=kb,
        )
        h_sub, s_sub = qse_matrices_hs(self.hamiltonian.operator, self.hamiltonian.n_qubits, basis)
        evals, _ = eigh(h_sub, s_sub)
        evals = np.sort(np.real(evals))
        e0 = float(evals[0])
        exc = [float(evals[i] - e0) for i in range(1, len(evals))]
        svals = np.linalg.svd(np.real(s_sub), compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "basis_reference": "uccsd_fermionic_singles",
                "K": len(basis),
                "H_sub_shape": list(h_sub.shape),
                "S_condition_number": cond_s,
            },
        )

    def run_from_uccsd_basis_shot_noise(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        shots_per_matrix_element: int = 4096,
        seed: int = 0,
    ) -> QSEResult:
        """Symmetric Gaussian noise on ``real(H_sub)`` for UCCSD micro-basis (placeholder)."""
        rng = np.random.default_rng(seed)
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_uccsd_reference(
            angles,
            self.hamiltonian,
            prepare_state,
            max_basis=kb,
        )
        h_sub, s_sub = qse_matrices_hs(self.hamiltonian.operator, self.hamiltonian.n_qubits, basis)
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
        svals = np.linalg.svd(s_real, compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "basis_reference": "uccsd_fermionic_singles",
                "K": len(basis),
                "shot_noise_model": "symmetric_gaussian_on_real_H_matrix",
                "shots_per_matrix_element": shots_per_matrix_element,
                "S_condition_number": cond_s,
            },
        )

    def run_from_uccsd_basis_pauli_transitions(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        shots_per_ij_term: int = 512,
        seed: int = 0,
    ) -> QSEResult:
        """Fermionic-singles QSE basis with per-(i,j,Pauli-term) transition shot bookkeeping."""
        rng = np.random.default_rng(seed)
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_uccsd_reference(
            angles,
            self.hamiltonian,
            prepare_state,
            max_basis=kb,
        )
        h_sym, s_mat, records = qse_h_matrix_transition_grouped_pauli_shots(
            basis,
            self.hamiltonian.operator,
            self.hamiltonian.n_qubits,
            shots_per_ij_term=shots_per_ij_term,
            rng=rng,
        )
        sched = build_qse_transition_schedule(
            self.hamiltonian.operator,
            len(basis),
            self.hamiltonian.n_qubits,
            shots_per_ij_term=shots_per_ij_term,
            records=records,
        )
        _, exc = solve_qse_ghep(h_sym, s_mat)
        svals = np.linalg.svd(np.real(s_mat), compute_uv=False)
        cond_s = float(svals[0] / max(1e-14, svals[-1])) if svals.size else float("inf")
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "basis_reference": "uccsd_fermionic_singles",
                "K": len(basis),
                "shot_noise_model": "grouped_statevector_shot_simulation_per_ij_term",
                "shots_per_ij_term": shots_per_ij_term,
                "S_condition_number": cond_s,
                "qse_pauli_transition_schedule": {
                    "n_qubits": sched.n_qubits,
                    "subspace_dim": sched.subspace_dim,
                    "n_pauli_terms": sched.n_pauli_terms,
                    "n_transition_tasks": sched.n_transition_tasks,
                    "total_shots_upper_bound": sched.total_shots_budget_upper_bound,
                },
            },
        )
