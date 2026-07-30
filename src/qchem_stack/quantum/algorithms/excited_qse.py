"""Quantum subspace expansion (QSE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import eigh

from qchem_stack.quantum.algorithms.qse_basis_strategies import (
    UccsdBasisStrategy,
    VqeHeaBasisStrategy,
)
from qchem_stack.quantum.algorithms.qse_solve_helpers import (
    build_basis_from_strategy,
    excitation_energies_dense,
    excitation_energies_pauli_transitions,
    excitation_energies_shot_noise,
    s_condition_number,
)
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class QSEResult:
    excitation_energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class QSE:
    """Quantum subspace expansion: ``arXiv:1603.05681`` Galerkin on a small basis, plus dense spectral reference."""

    _VQE_HEA = VqeHeaBasisStrategy()
    _UCCSD = UccsdBasisStrategy()

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

    def _solve_qse_with_mode(
        self,
        basis: list[np.ndarray],
        *,
        mode: str,
        basis_reference: str | None = None,
        shots_per_matrix_element: int = 4096,
        shots_per_ij_term: int = 512,
        rng: np.random.Generator | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> QSEResult:
        """Solve ``H c = E S c`` on ``basis`` with one of the shared solve backends.

        ``mode`` is ``"dense"`` / ``"shot_noise"`` / ``"pauli_transitions"`` /
        ``"pauli_transitions_qiskit"``. Unifies the per-mode meta-dict construction
        shared by the public ``run_from_*`` wrappers, so the solve variants are
        parametrised by ``mode`` instead of duplicated.
        """
        op = self.hamiltonian.operator
        n = self.hamiltonian.n_qubits
        ref = "arXiv:1603.05681"
        k = len(basis)
        gen = rng if rng is not None else np.random.default_rng(0)
        meta: dict[str, Any]
        if mode == "dense":
            exc, h_sub, s_sub = excitation_energies_dense(op, n, basis)
            meta = {
                "reference": ref,
                "K": k,
                "H_sub_shape": list(h_sub.shape),
                "S_condition_number": s_condition_number(s_sub),
            }
        elif mode == "shot_noise":
            exc, s_sub = excitation_energies_shot_noise(
                op, n, basis, shots_per_matrix_element=shots_per_matrix_element, rng=gen
            )
            meta = {
                "reference": ref,
                "K": k,
                "shot_noise_model": "symmetric_gaussian_on_real_H_matrix",
                "legacy_fast_path": True,
                "shots_per_matrix_element": shots_per_matrix_element,
                "S_condition_number": s_condition_number(s_sub),
            }
        elif mode == "pauli_transitions":
            exc, s_mat, schedule_meta = excitation_energies_pauli_transitions(
                op,
                n,
                basis,
                shots_per_ij_term=shots_per_ij_term,
                shot_mode="pauli_transitions",
                rng=gen,
            )
            meta = {
                "reference": ref,
                "K": k,
                "computable_runtime": "QSEMatricesComputable",
                "shot_noise_model": "grouped_statevector_shot_simulation_per_ij_term",
                "shots_per_ij_term": shots_per_ij_term,
                "S_condition_number": s_condition_number(s_mat),
                "qse_pauli_transition_schedule": schedule_meta,
            }
        elif mode == "pauli_transitions_qiskit":
            exc, _, schedule_meta = excitation_energies_pauli_transitions(
                op,
                n,
                basis,
                shots_per_ij_term=shots_per_ij_term,
                shot_mode="pauli_transitions_qiskit",
            )
            meta = {
                "reference": ref,
                "K": k,
                "computable_runtime": "QSEMatricesComputable",
                "shot_noise_model": "qiskit_histogram_per_ij_term",
                "shots_per_ij_term": shots_per_ij_term,
                "qse_pauli_transition_schedule": schedule_meta,
            }
        else:
            raise ValueError(f"Unknown QSE solve mode: {mode!r}")
        if basis_reference is not None:
            meta["basis_reference"] = basis_reference
        if extra_meta:
            meta.update(extra_meta)
        return QSEResult(excitation_energies=exc, meta=meta)

    def run_from_vqe_hea_basis(
        self,
        angles: np.ndarray,
        depth: int,
        *,
        max_basis: int | None = None,
    ) -> QSEResult:
        """Build orthonormal micro-basis from VQE+Pauli-X bumps; solve ``H c = E S c``."""
        kb = max_basis or self.subspace_dim
        basis = build_basis_from_strategy(
            self._VQE_HEA, angles, self.hamiltonian, max_basis=kb, depth=depth
        )
        return self._solve_qse_with_mode(
            basis,
            mode="dense",
            extra_meta={
                "K_raw": int(self.hamiltonian.n_qubits + 1),
                "linear_dependencies_removed": int(
                    max(0, self.hamiltonian.n_qubits + 1 - len(basis))
                ),
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
        basis = build_basis_from_strategy(
            self._VQE_HEA, angles, self.hamiltonian, max_basis=kb, depth=depth
        )
        return self._solve_qse_with_mode(
            basis,
            mode="shot_noise",
            shots_per_matrix_element=shots_per_matrix_element,
            rng=rng,
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
        basis = build_basis_from_strategy(
            self._VQE_HEA, angles, self.hamiltonian, max_basis=kb, depth=depth
        )
        return self._solve_qse_with_mode(
            basis,
            mode="pauli_transitions",
            shots_per_ij_term=shots_per_ij_term,
            rng=rng,
        )

    def _run_uccsd_variant(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None,
        expansion_pool: str,
        solve_fn: Callable[..., QSEResult],
        **solve_kwargs: Any,
    ) -> QSEResult:
        kb = max_basis or self.subspace_dim
        basis = build_basis_from_strategy(
            self._UCCSD,
            angles,
            self.hamiltonian,
            max_basis=kb,
            prepare_state=prepare_state,
            expansion_pool=expansion_pool,
        )
        return solve_fn(basis=basis, expansion_pool=expansion_pool, **solve_kwargs)

    def run_from_uccsd_basis(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        expansion_pool: str = "fermionic_singles",
    ) -> QSEResult:
        """Build orthonormal micro-basis from UCCSD reference + mapped fermionic singles."""

        def _solve(*, basis: list[np.ndarray], expansion_pool: str, **_kw: Any) -> QSEResult:
            return self._solve_qse_with_mode(
                basis, mode="dense", basis_reference="uccsd_fermionic_singles"
            )

        return self._run_uccsd_variant(
            angles,
            prepare_state,
            max_basis=max_basis,
            expansion_pool=expansion_pool,
            solve_fn=_solve,
        )

    def run_from_uccsd_basis_shot_noise(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        shots_per_matrix_element: int = 4096,
        seed: int = 0,
        expansion_pool: str = "fermionic_singles",
    ) -> QSEResult:
        """Symmetric Gaussian noise on ``real(H_sub)`` for UCCSD micro-basis (placeholder)."""
        rng = np.random.default_rng(seed)

        def _solve(*, basis: list[np.ndarray], expansion_pool: str, **_kw: Any) -> QSEResult:
            return self._solve_qse_with_mode(
                basis,
                mode="shot_noise",
                basis_reference="uccsd_fermionic_singles",
                shots_per_matrix_element=shots_per_matrix_element,
                rng=rng,
            )

        return self._run_uccsd_variant(
            angles,
            prepare_state,
            max_basis=max_basis,
            expansion_pool=expansion_pool,
            solve_fn=_solve,
        )

    def run_from_uccsd_basis_pauli_transitions(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        shots_per_ij_term: int = 512,
        seed: int = 0,
        expansion_pool: str = "fermionic_singles",
    ) -> QSEResult:
        """Fermionic-singles QSE basis with per-(i,j,Pauli-term) transition shot bookkeeping."""
        rng = np.random.default_rng(seed)

        def _solve(*, basis: list[np.ndarray], expansion_pool: str, **_kw: Any) -> QSEResult:
            return self._solve_qse_with_mode(
                basis,
                mode="pauli_transitions",
                basis_reference=f"uccsd_{expansion_pool}",
                shots_per_ij_term=shots_per_ij_term,
                rng=rng,
            )

        return self._run_uccsd_variant(
            angles,
            prepare_state,
            max_basis=max_basis,
            expansion_pool=expansion_pool,
            solve_fn=_solve,
        )

    def run_from_uccsd_basis_pauli_transitions_qiskit(
        self,
        angles: np.ndarray,
        prepare_state: Callable[[np.ndarray], np.ndarray],
        *,
        max_basis: int | None = None,
        shots_per_ij_term: int = 512,
        expansion_pool: str = "fermionic_singles",
    ) -> QSEResult:
        def _solve(*, basis: list[np.ndarray], expansion_pool: str, **_kw: Any) -> QSEResult:
            return self._solve_qse_with_mode(
                basis,
                mode="pauli_transitions_qiskit",
                basis_reference=f"uccsd_{expansion_pool}",
                shots_per_ij_term=shots_per_ij_term,
            )

        return self._run_uccsd_variant(
            angles,
            prepare_state,
            max_basis=max_basis,
            expansion_pool=expansion_pool,
            solve_fn=_solve,
        )
