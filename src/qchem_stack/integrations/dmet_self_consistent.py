"""Backward-compatible re-exports; canonical implementation in ``chem.embedding``."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.embedding.dmet import DMETContext, QubitHamiltonianFragmentSolverExact
from qchem_stack.chem.embedding.dmet_self_consistent import (
    DMETBathState,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
    OneShotEmbeddingDriver,
)
from qchem_stack.config.quantum_helpers import resolve_vqe_depth, resolve_vqe_maxiter
from qchem_stack.integrations.dmet_fragment_solvers import QubitHamiltonianFragmentSolverVQE

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig

__all__ = [
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "OneShotEmbeddingDriver",
    "run_dmet_bath_scf_self_consistency_v1",
]


def run_dmet_bath_scf_self_consistency_v1(
    cfg: ExperimentConfig,
    fragment_labels: list[str],
    qh: QubitHamiltonian,
    executor: Any,
    *,
    max_cycles: int,
    energy_tol: float = 1e-5,
) -> dict[str, Any]:
    """
    Bath SCF-style DMET loop v1: shared global impurity Hamiltonian, energy-delta convergence.

    Intended for ``whole_active_system`` demos when ``n_scf_cycles_embedding >= 2``.
    """
    labs = [x for x in fragment_labels if str(x).strip()]
    if len(labs) < 1:
        return {
            "schema": "dmet_self_consistency_v1",
            "status": "skipped_no_fragments",
            "fragment_labels": labs,
        }
    dmet = cfg.embedding.dmet  # type: ignore[union-attr]
    if dmet.fragment_solver.use_exact:
        solver: Any = QubitHamiltonianFragmentSolverExact(
            max_qubits=int(dmet.fragment_solver.exact_max_qubits)
        )
    else:
        solver = QubitHamiltonianFragmentSolverVQE(
            depth=resolve_vqe_depth(cfg),
            maxiter=resolve_vqe_maxiter(cfg),
            executor=executor,
            random_seed=cfg.random_seed,
        )
    ctx = DMETContext(
        fragments=labs,
        solver=solver,
        n_scf_cycles_embedding=cfg.embedding.n_scf_cycles_embedding,
        classical_reference_method=cfg.embedding.classical_reference_method,
    )
    loop = DMETSelfConsistencyLoop(ctx, max_cycles=max(2, int(max_cycles)))

    def build_ham(_fid: str, _bath: DMETBathState) -> QubitHamiltonian:
        return qh

    def update_bath(bath: DMETBathState, frags: list[DMETFragmentResult]) -> DMETBathState:
        energies = [float(f.energy) for f in frags if f.energy is not None]
        e_sum = float(sum(energies)) if energies else 0.0
        prev = bath.meta.get("fragment_energy_sum")
        delta = None if prev is None else abs(e_sum - float(prev))
        meta = {**bath.meta, "fragment_energy_sum": e_sum}
        if delta is not None:
            meta["last_cycle_energy_delta"] = float(delta)
        return replace(bath, meta=meta)

    def is_converged(_prev: DMETBathState, bath: DMETBathState, k: int) -> bool:
        if k < 1:
            return False
        delta = bath.meta.get("last_cycle_energy_delta")
        return delta is not None and float(delta) <= float(energy_tol)

    rep = loop.run_with_hooks(
        initial_bath=DMETBathState(meta={"note": "bath_scf_self_consistency_v1"}),
        build_fragment_hamiltonian=build_ham,
        update_bath=update_bath,
        is_converged=is_converged,
    )
    rep["hamiltonian_source"] = "whole_active_system"
    rep["multifragment_shared_global_hamiltonian"] = len(labs) >= 2
    rep["n_scf_cycles_embedding_yaml"] = cfg.embedding.n_scf_cycles_embedding
    return rep
