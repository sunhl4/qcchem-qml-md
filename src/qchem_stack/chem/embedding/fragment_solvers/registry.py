"""Resolve DMET impurity solvers by ``plugin_id`` (built-ins + user registration)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qchem_stack.chem.embedding.dmet import FragmentSolverProtocol

SolverFactory = Callable[..., FragmentSolverProtocol]

_BUILTIN: dict[str, SolverFactory] = {}


def register_fragment_solver(solver_id: str, factory: SolverFactory) -> None:
    sid = str(solver_id).strip()
    if not sid:
        raise ValueError("fragment solver id must be non-empty")
    _BUILTIN[sid] = factory


def list_fragment_solver_ids() -> list[str]:
    return sorted(_BUILTIN.keys())


def resolve_fragment_solver(
    solver_id: str | None,
    *,
    use_exact: bool = False,
    exact_max_qubits: int = 14,
    executor: Any = None,
    vqe_depth: int = 1,
    vqe_maxiter: int = 200,
    random_seed: int = 0,
) -> FragmentSolverProtocol:
    """Return a fragment solver instance for DMET embedding stages."""
    from qchem_stack.chem.embedding.dmet import QubitHamiltonianFragmentSolverExact
    from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
        QubitHamiltonianFragmentSolverVQE,
    )

    if use_exact:
        return QubitHamiltonianFragmentSolverExact(max_qubits=int(exact_max_qubits))

    sid = (solver_id or "vqe_default").strip()
    if sid in _BUILTIN:
        return _BUILTIN[sid](
            executor=executor,
            depth=vqe_depth,
            maxiter=vqe_maxiter,
            random_seed=random_seed,
        )
    if sid in {"", "vqe_default", "vqe"}:
        return QubitHamiltonianFragmentSolverVQE(
            depth=int(vqe_depth),
            maxiter=int(vqe_maxiter),
            executor=executor,
            random_seed=int(random_seed),
        )
    raise ValueError(
        f"Unknown fragment solver plugin_id={sid!r}; registered={list_fragment_solver_ids()}"
    )


def _register_builtins() -> None:
    from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
        QubitHamiltonianFragmentSolverVQE,
    )

    register_fragment_solver(
        "vqe_default",
        lambda **kw: QubitHamiltonianFragmentSolverVQE(
            depth=int(kw.get("depth") or kw.get("vqe_depth") or 1),
            maxiter=int(kw.get("maxiter") or kw.get("vqe_maxiter") or 200),
            executor=kw.get("executor"),
            random_seed=int(kw.get("random_seed") or 0),
        ),
    )


_register_builtins()
