"""QSE basis construction strategies (Strategy Pattern)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import numpy as np  # noqa: TC002

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@runtime_checkable
class QSEBasisStrategy(Protocol):
    """Protocol for building orthonormal QSE micro-bases."""

    def build(
        self,
        angles: np.ndarray,
        hamiltonian: QubitHamiltonian,
        *,
        max_basis: int,
        **kwargs: Any,
    ) -> list[np.ndarray]:
        """Return an orthonormal basis of size <= max_basis."""
        ...


class VqeHeaBasisStrategy:
    """Build QSE basis from VQE+HEA reference + Pauli-X bumps."""

    def build(
        self,
        angles: np.ndarray,
        hamiltonian: QubitHamiltonian,
        *,
        max_basis: int,
        **kwargs: Any,
    ) -> list[np.ndarray]:
        from qchem_stack.quantum.algorithms.excited_basis import build_qse_basis_from_vqe_hea

        depth = int(kwargs["depth"])
        return build_qse_basis_from_vqe_hea(
            angles, hamiltonian.n_qubits, depth, max_basis=max_basis
        )


class UccsdBasisStrategy:
    """Build QSE basis from UCCSD reference + mapped fermionic singles/doubles."""

    def build(
        self,
        angles: np.ndarray,
        hamiltonian: QubitHamiltonian,
        *,
        max_basis: int,
        **kwargs: Any,
    ) -> list[np.ndarray]:
        from qchem_stack.quantum.algorithms.excited_basis import (
            build_qse_basis_from_uccsd_reference,
        )

        prepare_state: Callable[[np.ndarray], np.ndarray] = kwargs["prepare_state"]
        expansion_pool = str(kwargs.get("expansion_pool", "fermionic_singles"))
        return build_qse_basis_from_uccsd_reference(
            angles,
            hamiltonian,
            prepare_state,
            max_basis=max_basis,
            expansion_pool=expansion_pool,
        )
