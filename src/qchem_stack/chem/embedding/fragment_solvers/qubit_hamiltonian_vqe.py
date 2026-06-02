"""QubitHamiltonian impurity VQE solver for DMET-style embedding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QubitHamiltonianFragmentSolverVQE:
    """
    Impurity **VQE** on a supplied :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`.

    Intended for ``embedding.dmet.hamiltonian_source == "whole_active_system"`` (single fragment
    covering the active space). Multi-fragment DMET requires a user-implemented
    ``build_fragment_hamiltonian`` that includes bath / embedding potentials.
    """

    depth: int = 1
    maxiter: int = 200
    executor: Any = None
    random_seed: int = 0

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
        from qchem_stack.chem.embedding.dmet import VQEFragmentSolverStub
        from qchem_stack.chem.hamiltonian import QubitHamiltonian
        from qchem_stack.quantum.algorithms.vqe import VQE

        if not isinstance(hamiltonian, QubitHamiltonian):
            return VQEFragmentSolverStub(depth=self.depth).solve(fragment_id, hamiltonian)
        if self.executor is None:
            raise ValueError("QubitHamiltonianFragmentSolverVQE requires a non-null executor")
        vr = VQE(hamiltonian, depth=self.depth, executor=self.executor).run(
            maxiter=self.maxiter,
            seed=self.random_seed,
        )
        return {
            "fragment_id": fragment_id,
            "solver": "QubitHamiltonianFragmentSolverVQE",
            "energy": float(vr.energy),
            "nfev": vr.nfev,
            "hea_depth": self.depth,
            "vqe_maxiter_used": self.maxiter,
            "hamiltonian_fingerprint": (hamiltonian.meta or {}).get("hamiltonian_fingerprint"),
            "note": (
                "Single-fragment impurity VQE on the given QubitHamiltonian. "
                "For whole_active_system demo, energy should match a fresh global VQE at same depth/seed."
            ),
        }
