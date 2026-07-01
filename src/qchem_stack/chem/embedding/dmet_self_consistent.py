"""DMET-style self-consistency loop hooks and one-shot embedding driver."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.embedding.dmet import DMETContext, VQEFragmentSolverStub
from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
    QubitHamiltonianFragmentSolverVQE,
)
from qchem_stack.chem.tolerances import DMET_ENERGY_TOLERANCE
from qchem_stack.config.quantum_helpers import resolve_vqe_depth, resolve_vqe_maxiter
from qchem_stack.contracts.schema_ids import DMET_ONE_SHOT_V1, DMET_SELF_CONSISTENCY_V1

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig


@dataclass
class DMETBathState:
    """Opaque bath state threaded through DMET hook iterations."""

    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class DMETFragmentResult:
    """Per-fragment solve outcome from a DMET cycle."""

    fragment_id: str
    energy: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class DMETSelfConsistencyLoop:
    """Protocol-shaped DMET loop with user-supplied bath update hooks."""

    def __init__(self, ctx: DMETContext, *, max_cycles: int = 10) -> None:
        self.ctx = ctx
        self.max_cycles = max(1, int(max_cycles))

    def _solve_fragments(
        self,
        build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
        bath: DMETBathState,
    ) -> list[DMETFragmentResult]:
        solver = self.ctx.solver or VQEFragmentSolverStub()
        out: list[DMETFragmentResult] = []
        for fid in self.ctx.fragments:
            ham = build_fragment_hamiltonian(fid, bath)
            raw = solver.solve(fid, ham)
            energy = raw.get("energy") if isinstance(raw, dict) else None
            e_float = float(energy) if energy is not None else None
            out.append(
                DMETFragmentResult(
                    fragment_id=fid, energy=e_float, raw=dict(raw) if isinstance(raw, dict) else {}
                )
            )
        return out

    def run_with_hooks(
        self,
        *,
        initial_bath: DMETBathState,
        build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
        update_bath: Callable[[DMETBathState, list[DMETFragmentResult]], DMETBathState],
        is_converged: Callable[[DMETBathState, DMETBathState, int], bool],
    ) -> dict[str, Any]:
        bath = initial_bath
        prev = initial_bath
        history: list[dict[str, Any]] = []
        converged = False
        cycles = 0
        for k in range(self.max_cycles):
            frags = self._solve_fragments(build_fragment_hamiltonian, bath)
            prev = bath
            bath = update_bath(bath, frags)
            history.append(
                {
                    "cycle": k,
                    "per_fragment": [
                        {"fragment_id": f.fragment_id, "energy": f.energy} for f in frags
                    ],
                }
            )
            cycles = k + 1
            if is_converged(prev, bath, k):
                converged = True
                break
        return {
            "schema": DMET_SELF_CONSISTENCY_V1,
            "converged": converged,
            "cycles": cycles,
            "history": history,
            "_final_bath_state": bath,
        }

    def run_with_sequential_bath_updates(
        self,
        *,
        initial_bath: DMETBathState,
        build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
        update_bath_sequential: Callable[[DMETBathState, DMETFragmentResult], DMETBathState],
        is_converged: Callable[[DMETBathState, DMETBathState, int], bool],
    ) -> dict[str, Any]:
        bath = initial_bath
        prev = initial_bath
        history: list[dict[str, Any]] = []
        converged = False
        cycles = 0
        for k in range(self.max_cycles):
            per_fragment: list[dict[str, Any]] = []
            for fid in self.ctx.fragments:
                frags = self._solve_fragments(build_fragment_hamiltonian, bath)
                frag_row = next((f for f in frags if f.fragment_id == fid), None)
                per_fragment.append(
                    {
                        "fragment_id": fid,
                        "energy": frag_row.energy if frag_row else None,
                    }
                )
                if frag_row is not None:
                    bath = update_bath_sequential(bath, frag_row)
            prev = bath
            history.append({"cycle": k, "per_fragment": per_fragment})
            cycles = k + 1
            if is_converged(prev, bath, k):
                converged = True
                break
        return {
            "schema": DMET_SELF_CONSISTENCY_V1,
            "converged": converged,
            "cycles": cycles,
            "sequential_fragment_updates": True,
            "history": history,
            "_final_bath_state": bath,
        }


class OneShotEmbeddingDriver:
    """Single-pass fragment solve ledger (CI / parity traceability)."""

    @staticmethod
    def run(ctx: DMETContext, fragment_hamiltonians: dict[str, Any]) -> dict[str, Any]:
        solver = ctx.solver or VQEFragmentSolverStub()
        rows: list[dict[str, Any]] = []
        for fid in ctx.fragments:
            ham = fragment_hamiltonians.get(fid, {})
            raw = solver.solve(fid, ham)
            rows.append({"fragment_id": fid, **(raw if isinstance(raw, dict) else {})})
        return {"schema": DMET_ONE_SHOT_V1, "fragments": rows}


def run_dmet_bath_scf_self_consistency_v1(
    cfg: ExperimentConfig,
    fragment_labels: list[str],
    qh: QubitHamiltonian,
    executor: Any,
    *,
    max_cycles: int,
    energy_tol: float = DMET_ENERGY_TOLERANCE,
) -> dict[str, Any]:
    """Bath SCF-style DMET loop v1: shared global impurity Hamiltonian, energy-delta convergence."""
    from qchem_stack.chem.embedding.dmet import QubitHamiltonianFragmentSolverExact

    labs = [x for x in fragment_labels if str(x).strip()]
    if len(labs) < 1:
        return {
            "schema": DMET_SELF_CONSISTENCY_V1,
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


__all__ = [
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "OneShotEmbeddingDriver",
    "run_dmet_bath_scf_self_consistency_v1",
]
