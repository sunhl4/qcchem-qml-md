"""Operator-token pool for GQE, backed by the existing registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class GQEOperatorPool:
    """Indexed unitary generators ``U_j = exp(θ_j G_j)`` with per-token angles.

    Generators ``G_j`` follow the OpenFermion / UCCSD convention (anti-Hermitian
    excitation operators). The identity token (if present) is a no-op.
    """

    operators: tuple[QubitOperator, ...]
    matrices: tuple[np.ndarray, ...]
    angles: tuple[float, ...]
    pool_id: str
    n_qubits: int
    default_angle: float = 0.1
    include_identity: bool = True

    @property
    def vocab_size(self) -> int:
        return len(self.operators)

    def __len__(self) -> int:
        return self.vocab_size

    def angle_for(self, index: int) -> float:
        return float(self.angles[int(index)])


def build_gqe_operator_pool(
    hamiltonian: QubitHamiltonian,
    *,
    pool_id: str = "fermionic_uccsd",
    default_angle: float = 0.1,
    angle_grid: tuple[float, ...] | None = None,
    include_identity: bool = True,
) -> GQEOperatorPool:
    """Build a GQE token vocabulary from a registered operator pool.

    Args:
        angle_grid: if set, each generator is replicated once per angle (discrete
            GQE search over amplitudes). Default ``None`` uses ``(default_angle,)``.
        include_identity: prepend a no-op identity token (HF / pad).
    """
    from openfermion.ops import QubitOperator

    base_ops = list(build_registered_operator_pool(pool_id, hamiltonian))
    if not base_ops:
        raise ValueError(f"operator pool {pool_id!r} produced zero generators")
    grid = angle_grid if angle_grid is not None else (float(default_angle),)

    ops: list[QubitOperator] = []
    mats: list[np.ndarray] = []
    angs: list[float] = []
    if include_identity:
        ops.append(QubitOperator())  # identity / empty
        mats.append(
            np.zeros((2**hamiltonian.n_qubits, 2**hamiltonian.n_qubits), dtype=np.complex128)
        )
        angs.append(0.0)

    for ang in grid:
        for op in base_ops:
            ops.append(op)
            mats.append(qubit_operator_to_sparse(op, hamiltonian.n_qubits))
            angs.append(float(ang))

    tag = str(pool_id)
    if angle_grid is not None:
        tag = f"{pool_id}|angles={list(grid)}"
    if include_identity:
        tag = f"{tag}|id"

    return GQEOperatorPool(
        operators=tuple(ops),
        matrices=tuple(mats),
        angles=tuple(angs),
        pool_id=tag,
        n_qubits=int(hamiltonian.n_qubits),
        default_angle=float(default_angle),
        include_identity=bool(include_identity),
    )


def _matrix_nnz(m: object) -> int:
    nnz = getattr(m, "nnz", None)
    if nnz is not None:
        return int(nnz)
    arr = np.asarray(m)
    return int(np.count_nonzero(arr))


def pool_summary(pool: GQEOperatorPool) -> dict[str, object]:
    return {
        "pool_id": pool.pool_id,
        "vocab_size": pool.vocab_size,
        "n_qubits": pool.n_qubits,
        "default_angle": pool.default_angle,
        "include_identity": pool.include_identity,
        "n_unique_angles": len(set(pool.angles)),
        "matrix_nnz": [_matrix_nnz(m) for m in pool.matrices],
    }
