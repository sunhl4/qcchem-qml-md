from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


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

    def register_solver(self, solver: FragmentSolverProtocol) -> None:
        self.solver = solver


@dataclass
class VQEFragmentSolverStub:
    """
    InQuanto-adjacent **fragment solver** placeholder: register intent to run VQE on an impurity.

    Replace ``solve`` body with :func:`~qchem_stack.chem.hamiltonian.molecular_hamiltonian_from_pyscf`
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
class QubitHamiltonianFragmentSolverVQE:
    """
    Impurity **VQE** on a supplied :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`.

    Intended for ``EmbeddingSpec.dmet_hamiltonian_source == "whole_active_system"`` (single fragment
    covering the active space). Multi-fragment DMET requires a user-implemented
    ``build_fragment_hamiltonian`` that includes bath / embedding potentials.
    """

    depth: int = 1
    maxiter: int = 200
    executor: Any = None
    random_seed: int = 0

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
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
