"""
Toy **multi-fragment** driver: each fragment receives the **same** global ``QubitHamiltonian``.

This is **not** bath DMET. It exercises :class:`~qchem_stack.chem.embedding.dmet_self_consistent.DMETSelfConsistencyLoop`
wiring with a trivial convergence criterion (one global VQE sweep per fragment per cycle).

Enable only for small active spaces (explicit opt-in via ``EmbeddingSpec``).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.embedding.dmet import DMETContext
from qchem_stack.chem.embedding.dmet_self_consistent import DMETBathState, DMETSelfConsistencyLoop
from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
    QubitHamiltonianFragmentSolverVQE,
)
from qchem_stack.config.quantum_helpers import resolve_vqe_depth, resolve_vqe_maxiter
from qchem_stack.contracts.schema_ids import DMET_UNIFORM_MULTIFRAGMENT_TOY_V1

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def run_uniform_hamiltonian_multifragment_toy(
    cfg: Any,
    fragment_labels: list[str],
    qh: QubitHamiltonian,
    executor: Any,
    *,
    max_cycles: int = 1,
) -> dict[str, Any]:
    """
    Run :class:`DMETSelfConsistencyLoop` with ``build_hamiltonian`` returning ``qh`` for every fragment.

    Parameters
    ----------
    cfg
        :class:`~qchem_stack.config.ExperimentConfig` (for quantum depths / seeds); passed as ``Any`` to limit imports.
    """
    labs = [x for x in fragment_labels if str(x).strip()]
    if len(labs) < 2:
        return {
            "schema": DMET_UNIFORM_MULTIFRAGMENT_TOY_V1,
            "status": "skipped_need_two_or_more_fragments",
            "fragment_labels": labs,
        }

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
    loop = DMETSelfConsistencyLoop(ctx, max_cycles=max(1, int(max_cycles)))

    def build_ham(_fid: str, _bath: DMETBathState) -> QubitHamiltonian:
        return qh

    def update_bath(bath: DMETBathState, _frags) -> DMETBathState:
        k = int(bath.meta.get("toy_cycle", 0)) + 1
        return replace(bath, meta={**bath.meta, "toy_cycle": k})

    def is_converged(_prev: DMETBathState, _bath: DMETBathState, k: int) -> bool:
        return k >= 0

    rep = loop.run_with_hooks(
        initial_bath=DMETBathState(meta={"note": "uniform_hamiltonian_toy"}),
        build_fragment_hamiltonian=build_ham,
        update_bath=update_bath,
        is_converged=is_converged,
    )
    rep["schema"] = "dmet_uniform_multifragment_toy_v1"
    rep["hamiltonian_source_note"] = (
        "Each fragment used the full active-space QubitHamiltonian — non-physical DMET; "
        "for orchestration testing only."
    )
    return rep
