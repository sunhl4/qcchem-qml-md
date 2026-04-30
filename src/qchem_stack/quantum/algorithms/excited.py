from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize
from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_shot_sim import energy_estimate_grouped_shot_simulation
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.qse_transition import (
    build_qse_transition_schedule,
    qse_h_matrix_transition_shots,
    solve_qse_ghep,
)
from qchem_stack.quantum.statevector import hea_state, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


def _gram_schmidt(vectors: list[np.ndarray], *, eps: float = 1e-10) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for v in vectors:
        w = np.asarray(v, dtype=complex).copy()
        for u in out:
            w -= np.vdot(u, w) * u
        nrm = float(np.linalg.norm(w))
        if nrm > eps:
            out.append(w / nrm)
    return out


def _apply_pauli_string(state: np.ndarray, n_qubits: int, qubit: int, letter: str) -> np.ndarray:
    op = QubitOperator(((qubit, letter),), 1.0)
    m = qubit_operator_to_sparse(op, n_qubits)
    return m @ state


def build_qse_basis_from_vqe_hea(
    angles: np.ndarray,
    n_qubits: int,
    depth: int,
    *,
    max_basis: int,
) -> list[np.ndarray]:
    """Microscopic subspace: |psi0>, X_q|psi0> (raw then orthonormalized). McClean-style pool (toy)."""
    g = hea_state(angles, n_qubits, depth)
    g = np.asarray(g, dtype=complex).ravel()
    g = g / (np.linalg.norm(g) + 1e-15)
    raw = [g]
    for q in range(n_qubits):
        raw.append(_apply_pauli_string(g, n_qubits, q, "X"))
    return _gram_schmidt(raw)[:max_basis]


def _overlap_squared_swap_test(
    phi: np.ndarray,
    psi: np.ndarray,
    shots: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Swap-test statistic: ``P(ancilla=0)=(1+|\\langle\\phi|\\psi\\rangle|^2)/2``; return estimate of ``|\\langle\\phi|\\psi\\rangle|^2``."""
    ovl = np.vdot(phi, psi)
    p0 = 0.5 * (1.0 + abs(ovl) ** 2)
    p0 = float(min(1.0, max(0.0, np.real(p0))))
    if shots <= 0:
        return float(abs(ovl) ** 2), 0.0
    k = int(rng.binomial(shots, p0))
    phat = k / shots
    est = 2.0 * phat - 1.0
    stderr = 2.0 * math.sqrt(p0 * (1.0 - p0) / shots)
    return float(est), float(stderr)


def _vqd_three_protocol_channels(
    prev_states: list[np.ndarray],
    g_new: np.ndarray,
    h_op: QubitOperator,
    n_qubits: int,
    penalty_weight: float,
    *,
    shots_objective: int,
    shots_overlap: int,
    shots_weight: int,
    rng: np.random.Generator,
    pauli_grouping: str = "tensor_product",
) -> dict[str, Any]:
    """InQuanto-style three channels: Hamiltonian expectation, overlap(s), deflation weight (product)."""
    g_new = np.asarray(g_new, dtype=complex).ravel()
    g_new = g_new / (np.linalg.norm(g_new) + 1e-15)
    h_dense = qubit_operator_to_sparse(h_op, n_qubits)
    e_ex = float(np.real(np.vdot(g_new, h_dense @ g_new)))
    obj: dict[str, Any] = {
        "energy_exact": e_ex,
        "shots_budget_objective": int(max(0, shots_objective)),
    }
    if shots_objective > 0:
        plan = build_measurement_plan(h_op, n_qubits, grouping=pauli_grouping)  # type: ignore[arg-type]
        m, se, _ = energy_estimate_grouped_shot_simulation(
            g_new, h_op, plan, n_qubits, shots_objective, rng
        )
        obj["energy_shot_mean"] = float(m)
        obj["energy_shot_stderr"] = float(se)
    overlap_ex = float(sum(abs(np.vdot(s, g_new)) ** 2 for s in prev_states))
    ov: dict[str, Any] = {
        "overlap_squared_sum_exact": overlap_ex,
        "shots_per_pair": int(max(0, shots_overlap)),
    }
    if shots_overlap > 0 and prev_states:
        est_sum = 0.0
        se_sq = 0.0
        for s in prev_states:
            e2, se2 = _overlap_squared_swap_test(s, g_new, shots_overlap, rng)
            est_sum += e2
            se_sq += se2 * se2
        ov["overlap_squared_sum_shot_mean"] = float(est_sum)
        ov["overlap_squared_sum_shot_stderr"] = float(math.sqrt(se_sq))
    w_ex = penalty_weight * overlap_ex
    wt: dict[str, Any] = {
        "penalty_weight": penalty_weight,
        "weight_exact": float(w_ex),
        "shots_budget_weight": int(max(0, shots_weight)),
    }
    if (
        shots_weight > 0
        and shots_overlap > 0
        and prev_states
        and "overlap_squared_sum_shot_mean" in ov
    ):
        wt["weight_shot_mean"] = float(penalty_weight * ov["overlap_squared_sum_shot_mean"])
        wt["weight_shot_stderr"] = float(
            penalty_weight * ov["overlap_squared_sum_shot_stderr"]
        )
    return {"objective": obj, "overlap": ov, "weight": wt}


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
class VQDResult:
    energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class VQD:
    """Sequential deflation (Higgott et al., `Quantum 3, 156 (2019)`) with optional three-channel reporting.

    Optimization still uses a **single** classical objective (energy + overlap penalty). After each
    level, :func:`_vqd_three_protocol_channels` reports objective / overlap / weight statistics
    analogous to InQuanto's three ``Protocol`` slots (shot budgets optional).
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        n_states: int = 2,
        depth: int = 1,
        penalty_weight: float = 5.0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        self.hamiltonian = hamiltonian
        self.n_states = n_states
        self.depth = depth
        self.penalty_weight = penalty_weight
        self._executor = executor

    def run(
        self,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        *,
        shots_objective: int = 0,
        shots_overlap: int = 0,
        shots_weight: int = 0,
        pauli_grouping: str = "tensor_product",
        ground_angles: np.ndarray | None = None,
        ground_energy: float | None = None,
    ) -> VQDResult:
        """Run VQD. If ``ground_angles`` is set (e.g. from pipeline VQE/ADAPT), skip an inner VQE for level 0."""
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        exe = executor or self._executor or StatevectorHeaExecutor()
        rng = np.random.default_rng(seed + 1)
        n_hea = 2 * self.hamiltonian.n_qubits * self.depth
        reused_ground = ground_angles is not None
        if reused_ground:
            ga = np.asarray(ground_angles, dtype=float).ravel()
            g0 = hea_state(ga, self.hamiltonian.n_qubits, self.depth)
            e0 = (
                float(ground_energy)
                if ground_energy is not None
                else float(
                    exe.expectation_state(
                        g0, self.hamiltonian.operator, self.hamiltonian.n_qubits
                    )
                )
            )
            energies = [e0]
            v0_angles = ga
        else:
            v0 = VQE(self.hamiltonian, depth=self.depth, executor=exe).run(seed=seed)
            g0 = hea_state(v0.angles, self.hamiltonian.n_qubits, self.depth)
            energies = [v0.energy]
            v0_angles = np.asarray(v0.angles, dtype=float)

        if self.n_states < 2:
            return VQDResult(
                energies=energies,
                meta={
                    "reference": "Quantum 3, 156 (2019) — collapsed single-objective deflation",
                    "reused_pipeline_ground": reused_ground,
                },
            )

        prev_states: list[np.ndarray] = [g0 / (np.linalg.norm(g0) + 1e-15)]
        g0n = prev_states[0]
        vqd_channels: list[dict[str, Any]] = [
            {
                "level": 0,
                "energy_exact": float(energies[0]),
                "overlap_squared_sum": 0.0,
                "channel_note": "ground_VQE_only",
                "three_protocol": _vqd_three_protocol_channels(
                    [],
                    g0n,
                    self.hamiltonian.operator,
                    self.hamiltonian.n_qubits,
                    self.penalty_weight,
                    shots_objective=shots_objective,
                    shots_overlap=0,
                    shots_weight=0,
                    rng=rng,
                    pauli_grouping=pauli_grouping,
                ),
            }
        ]

        for level in range(1, self.n_states):
            if level == 1 and reused_ground and len(v0_angles) == n_hea:
                x0 = np.asarray(v0_angles, dtype=float).copy()
            else:
                x0 = rng.uniform(-np.pi, np.pi, size=n_hea)

            def objective(x: np.ndarray, states: list[np.ndarray] = prev_states) -> float:
                g = hea_state(x, self.hamiltonian.n_qubits, self.depth)
                g = g / (np.linalg.norm(g) + 1e-15)
                ov_sum = sum(abs(np.vdot(s, g)) ** 2 for s in states)
                e = exe.expectation_state(g, self.hamiltonian.operator, self.hamiltonian.n_qubits)
                return e + self.penalty_weight * ov_sum

            r = minimize(objective, x0, method="COBYLA", options={"maxiter": 150})
            g_new = hea_state(np.asarray(r.x), self.hamiltonian.n_qubits, self.depth)
            g_new = g_new / (np.linalg.norm(g_new) + 1e-15)
            e_new = exe.expectation_state(g_new, self.hamiltonian.operator, self.hamiltonian.n_qubits)
            energies.append(float(e_new))
            ov_pre = float(sum(abs(np.vdot(s, g_new)) ** 2 for s in prev_states))
            tp = _vqd_three_protocol_channels(
                prev_states,
                g_new,
                self.hamiltonian.operator,
                self.hamiltonian.n_qubits,
                self.penalty_weight,
                shots_objective=shots_objective,
                shots_overlap=shots_overlap,
                shots_weight=shots_weight,
                rng=rng,
                pauli_grouping=pauli_grouping,
            )
            vqd_channels.append(
                {
                    "level": level,
                    "energy_exact": float(e_new),
                    "overlap_squared_sum": ov_pre,
                    "orthogonal_weight": self.penalty_weight,
                    "channel_note": "objective_plus_overlap_penalty_collapsed_statevector",
                    "three_protocol": tp,
                }
            )
            prev_states.append(g_new)

        return VQDResult(
            energies=energies,
            meta={
                "orthogonal_weight": self.penalty_weight,
                "reference": "Quantum 3, 156 (2019)",
                "vqd_channels": vqd_channels,
                "implementation_note": "three_protocol_reporting_objective_overlap_weight",
                "shots_objective": shots_objective,
                "shots_overlap": shots_overlap,
                "shots_weight": shots_weight,
                "reused_pipeline_ground": reused_ground,
            },
        )


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
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "H_sub_shape": list(h_sub.shape),
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
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "shot_noise_model": "symmetric_gaussian_on_real_H_matrix",
                "shots_per_matrix_element": shots_per_matrix_element,
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
        """Per-(i,j,Pauli-term) complex Gaussian noise; ``S`` exact; schedule for parity tables."""
        rng = np.random.default_rng(seed)
        kb = max_basis or self.subspace_dim
        basis = build_qse_basis_from_vqe_hea(angles, self.hamiltonian.n_qubits, depth, max_basis=kb)
        h_sym, s_mat, records = qse_h_matrix_transition_shots(
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
        return QSEResult(
            excitation_energies=exc,
            meta={
                "reference": "arXiv:1603.05681",
                "K": len(basis),
                "shot_noise_model": "independent_complex_gaussian_per_ij_term",
                "shots_per_ij_term": shots_per_ij_term,
                "qse_pauli_transition_schedule": {
                    "n_qubits": sched.n_qubits,
                    "subspace_dim": sched.subspace_dim,
                    "n_pauli_terms": sched.n_pauli_terms,
                    "n_transition_tasks": sched.n_transition_tasks,
                    "total_shots_upper_bound": sched.total_shots_budget_upper_bound,
                },
            },
        )
