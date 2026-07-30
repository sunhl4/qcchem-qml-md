"""Paper operator pool: UCCSD Pauli strings × time grid → e^{i P t} (+ identity).

Nakaji et al. Appendix A.2.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from openfermion.ops import QubitOperator
from scipy.linalg import expm

from qchem_stack.integrations.gqe.native.operator_pool import GQEOperatorPool
from qchem_stack.integrations.gqe.native.paper_spec import PAPER_TIME_GRID
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def _hermitian_pauli_strings(ops: list[QubitOperator]) -> list[QubitOperator]:
    """Unique Hermitian Pauli products appearing in UCCSD generators (coeff → ±1)."""
    seen: dict[tuple[tuple[int, str], ...], float] = {}
    for op in ops:
        for term, coeff in op.terms.items():
            if not term:
                continue
            key = tuple(term)
            c = complex(coeff)
            # Keep the real part of the coefficient on Hermitian Paulis;
            # imaginary-only terms belong to the conjugate partner in anti-Hermitian G.
            mag = float(np.real(c))
            if abs(mag) < 1e-14:
                # If purely imaginary, map i*P → treat P as Hermitian generator piece
                mag = float(np.imag(c))
            if abs(mag) < 1e-14:
                continue
            sign = 1.0 if mag >= 0 else -1.0
            # Prefer first-seen sign; uniqueness by Pauli string
            if key not in seen:
                seen[key] = sign
    out: list[QubitOperator] = []
    for key, sign in sorted(seen.items(), key=lambda kv: str(kv[0])):
        out.append(QubitOperator(key, float(sign)))
    return out


def build_paper_uccsd_pool(
    hamiltonian: QubitHamiltonian,
    *,
    time_grid: tuple[float, ...] | None = None,
    include_identity: bool = True,
    base_pool_id: str = "fermionic_uccsd",
) -> GQEOperatorPool:
    """Build ``G = {e^{i P_j t_j}} ∪ {I}`` with paper time grid.

    Each token stores the **already-exponentiated** unitary matrix; ``angles`` are
    the ``t_j`` values (0 for identity). ``apply_pool_sequence`` multiplies these
    unitaries when ``pool.meta_unitary_ready`` is set via angles=='precomputed'.

    For compatibility with ``apply_pool_sequence`` (which does ``expm(θ G)``), we
    store generators ``G = i P`` so that ``expm(t * G) = e^{i P t}``.
    """
    grid = time_grid if time_grid is not None else PAPER_TIME_GRID
    base = list(build_registered_operator_pool(base_pool_id, hamiltonian))
    if not base:
        raise ValueError(f"base pool {base_pool_id!r} empty")
    paulis = _hermitian_pauli_strings(base)
    if not paulis:
        raise ValueError("no Hermitian Pauli strings extracted from UCCSD pool")

    n = int(hamiltonian.n_qubits)
    ops: list[QubitOperator] = []
    mats: list[np.ndarray] = []
    angs: list[float] = []

    if include_identity:
        ops.append(QubitOperator())
        mats.append(np.zeros((2**n, 2**n), dtype=np.complex128))
        angs.append(0.0)

    for p_op in paulis:
        p_mat = qubit_operator_to_sparse(p_op, n)
        # Generator G = i P  (anti-Hermitian if P Hermitian) → expm(t G) = e^{i P t}
        g_mat = 1j * np.asarray(p_mat, dtype=np.complex128)
        for t in grid:
            ops.append(p_op)
            mats.append(g_mat)
            angs.append(float(t))

    return GQEOperatorPool(
        operators=tuple(ops),
        matrices=tuple(mats),
        angles=tuple(angs),
        pool_id=f"paper_uccsd_pauli|T={len(grid)}|id={include_identity}",
        n_qubits=n,
        default_angle=float(grid[0]) if grid else 0.0,
        include_identity=bool(include_identity),
    )


def verify_paper_unitary(pool: GQEOperatorPool, index: int, *, atol: float = 1e-10) -> bool:
    """Check ``expm(t G)`` is unitary for token ``index``."""
    t = pool.angle_for(index)
    g = pool.matrices[index]
    if abs(t) < 1e-15:
        return True
    u = expm(t * g)
    n = u.shape[0] if u.shape else 1
    return bool(np.allclose(u.conj().T @ u, np.eye(n), atol=atol))
