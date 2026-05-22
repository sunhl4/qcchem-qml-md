from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import numpy as np
from openfermion import get_sparse_operator


@runtime_checkable
class FragmentSolverProtocol(Protocol):
    """Hook for classical CCSD / quantum VQE on impurity."""

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]: ...


@dataclass
class DMETContext:
    """Impurity DMET bookkeeping (full solver left to user extensions).

    Falsifiability fields on the pipeline side are also carried on
    :class:`~qchem_stack.config.EmbeddingSpec` and written to ``repro.parity_snapshot``.
    """

    fragments: list[str]
    solver: FragmentSolverProtocol | None = None
    n_scf_cycles_embedding: int | None = None
    classical_reference_method: str | None = None
    bath_spatial_orbitals: int | None = None
    """Schmidt bath count (spatial orbitals) when production embedding is used; else ``None``."""

    def register_solver(self, solver: FragmentSolverProtocol) -> None:
        self.solver = solver


@dataclass
class VQEFragmentSolverStub:
    """
    Vendor-doc-adjacent **fragment solver** placeholder: register intent to run VQE on an impurity.

    Replace ``solve`` body with :func:`~qchem_stack.chem.hamiltonian.molecular_hamiltonian_from_classical_reference`
    on the fragment Hamiltonian + :class:`~qchem_stack.quantum.algorithms.vqe.VQE` for a real DMET loop.
    """

    depth: int = 1

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
        return {
            "fragment_id": fragment_id,
            "solver": "VQEFragmentSolverStub",
            "hea_depth": self.depth,
            "note": "Stub only — supply impurity QubitHamiltonian and call VQE in user code.",
            "hamiltonian_type": type(hamiltonian).__name__,
        }


@dataclass
class QubitHamiltonianFragmentSolverExact:
    """Dense ground-state energy for small-qubit impurity Hamiltonians (numpy ``eigh``)."""

    max_qubits: int = 14

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
        from qchem_stack.chem.hamiltonian import QubitHamiltonian

        if not isinstance(hamiltonian, QubitHamiltonian):
            return VQEFragmentSolverStub(depth=1).solve(fragment_id, hamiltonian)
        n = int(hamiltonian.n_qubits)
        if n > int(self.max_qubits):
            return {
                "fragment_id": fragment_id,
                "solver": "QubitHamiltonianFragmentSolverExact",
                "skipped": True,
                "reason": "n_qubits_exceeds_max_qubits",
                "n_qubits": n,
                "max_qubits": int(self.max_qubits),
                "hamiltonian_fingerprint": (hamiltonian.meta or {}).get("hamiltonian_fingerprint"),
            }
        sm = get_sparse_operator(hamiltonian.operator, n_qubits=n)
        mat = np.asarray(sm.toarray(), dtype=np.complex128)
        herm = (mat + np.conjugate(mat.T)) / 2.0
        w = np.linalg.eigvalsh(np.real(herm))
        e0 = float(np.min(w))
        return {
            "fragment_id": fragment_id,
            "solver": "QubitHamiltonianFragmentSolverExact",
            "energy": e0,
            "n_qubits": n,
            "hamiltonian_fingerprint": (hamiltonian.meta or {}).get("hamiltonian_fingerprint"),
            "note": "Dense ground state — DMET bath fitting not applied (L1 reproducibility slice).",
        }
