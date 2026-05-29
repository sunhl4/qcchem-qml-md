"""
DMET **self-consistency loop skeleton**: bath state → fragment solves → global update hooks.

Full numerical DMET (bath fitting, correlation potential) is **not** inlined — inject callables
so the same orchestration matches ``EmbeddingSpec`` / ``repro`` contracts without PySCF lock-in.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import DMET_ONE_SHOT_V1, DMET_SELF_CONSISTENCY_V1

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.embedding.dmet import DMETContext


@dataclass
class DMETBathState:
    """Opaque-ish global embedding state carried between SCF-style cycles."""

    iteration: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class DMETFragmentResult:
    fragment_id: str
    energy: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class DMETSelfConsistencyLoop:
    """
    Generic iterate-until-converged driver (user supplies Hamiltonian builders + bath updates).

    Matches the **public** DMET story: multiple fragments, repeated global updates, ``max_cycles``
    surfaced to ``repro`` / ``EmbeddingSpec.n_scf_cycles_embedding``.
    """

    context: DMETContext
    max_cycles: int = 20

    def run_with_hooks(
        self,
        *,
        initial_bath: DMETBathState,
        build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
        update_bath: Callable[[DMETBathState, list[DMETFragmentResult]], DMETBathState],
        is_converged: Callable[[DMETBathState, DMETBathState, int], bool],
    ) -> dict[str, Any]:
        if self.context.solver is None:
            raise ValueError("DMETContext.solver must be set (FragmentSolverProtocol)")
        bath = replace(initial_bath, iteration=0)
        history: list[dict[str, Any]] = []
        prev_bath: DMETBathState | None = None
        for k in range(self.max_cycles):
            prev_bath = bath
            fragments: list[DMETFragmentResult] = []
            for fid in self.context.fragments:
                ham = build_fragment_hamiltonian(fid, bath)
                sol = self.context.solver.solve(fid, ham)  # type: ignore[union-attr]
                fragments.append(
                    DMETFragmentResult(
                        fragment_id=fid,
                        energy=_coerce_float(sol.get("energy")),
                        meta={key: val for key, val in sol.items() if key != "energy"},
                    )
                )
            bath = update_bath(bath, fragments)
            bath = replace(bath, iteration=k + 1)
            history.append(
                {
                    "cycle": k,
                    "bath_meta": dict(_bath_to_json(bath)["meta"]),
                    "fragment_energies": {f.fragment_id: f.energy for f in fragments},
                }
            )
            if prev_bath is not None and is_converged(prev_bath, bath, k):
                return {
                    "schema": DMET_SELF_CONSISTENCY_V1,
                    "converged": True,
                    "cycles": k + 1,
                    "history": history,
                    "final_bath": _bath_to_json(bath),
                }
        return {
            "schema": DMET_SELF_CONSISTENCY_V1,
            "converged": False,
            "cycles": self.max_cycles,
            "history": history,
            "final_bath": _bath_to_json(bath),
        }

    def run_with_sequential_bath_updates(
        self,
        *,
        initial_bath: DMETBathState,
        build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
        update_bath_sequential: Callable[[DMETBathState, DMETFragmentResult], DMETBathState],
        is_converged: Callable[[DMETBathState, DMETBathState, int], bool],
    ) -> dict[str, Any]:
        """
        One **outer cycle** scans all fragments in order; after **each** fragment solve,
        ``update_bath_sequential`` mutates embedding state (Gauss–Seidel / successive substitution).

        ``is_converged(prev_bath_at_cycle_start, bath_after_full_sweep, cycle_index)`` is evaluated
        after finishing all fragments in a cycle, before incrementing ``iteration``.
        """
        if self.context.solver is None:
            raise ValueError("DMETContext.solver must be set (FragmentSolverProtocol)")
        bath = replace(initial_bath, iteration=0)
        history: list[dict[str, Any]] = []
        for k in range(self.max_cycles):
            bath = replace(
                bath,
                meta={**bath.meta, "current_sweep_max_delta": 0.0},
            )
            prev_at_start = bath
            per_frag: list[dict[str, Any]] = []
            for fid in self.context.fragments:
                ham = build_fragment_hamiltonian(fid, bath)
                sol = self.context.solver.solve(fid, ham)  # type: ignore[union-attr]
                res = DMETFragmentResult(
                    fragment_id=fid,
                    energy=_coerce_float(sol.get("energy")),
                    meta={key: val for key, val in sol.items() if key != "energy"},
                )
                bath = update_bath_sequential(bath, res)
                row: dict[str, Any] = {
                    "fragment_id": fid,
                    "energy": res.energy,
                    "meta_keys": sorted(res.meta.keys()),
                }
                if sol.get("fci_electronic_au") is not None:
                    row["fci_electronic_au"] = sol.get("fci_electronic_au")
                per_frag.append(row)
            lsmd = float(bath.meta.get("current_sweep_max_delta", 0.0))
            bath = replace(
                bath,
                meta={**bath.meta, "last_sweep_max_delta": lsmd},
            )
            bath = replace(bath, iteration=k + 1)
            history.append(
                {
                    "cycle": k,
                    "per_fragment": per_frag,
                    "last_sweep_max_delta": lsmd,
                }
            )
            rep_out: dict[str, Any] = {
                "schema": DMET_SELF_CONSISTENCY_V1,
                "sequential_fragment_updates": True,
                "cycles": k + 1,
                "history": history,
                "final_bath": _bath_to_json(bath),
            }
            rep_out["_final_bath_state"] = bath
            if is_converged(prev_at_start, bath, k):
                rep_out["converged"] = True
                return rep_out
        rep_fail: dict[str, Any] = {
            "schema": DMET_SELF_CONSISTENCY_V1,
            "sequential_fragment_updates": True,
            "converged": False,
            "cycles": self.max_cycles,
            "history": history,
            "final_bath": _bath_to_json(bath),
        }
        rep_fail["_final_bath_state"] = bath
        return rep_fail


class OneShotEmbeddingDriver:
    """Single-pass fragment evaluation (CI / tutorial default when no SCF loop is configured)."""

    @staticmethod
    def run(
        context: DMETContext,
        fragment_hamiltonians: dict[str, Any],
    ) -> dict[str, Any]:
        if context.solver is None:
            raise ValueError("DMETContext.solver must be set")
        results: list[DMETFragmentResult] = []
        for fid in context.fragments:
            ham = fragment_hamiltonians[fid]
            sol = context.solver.solve(fid, ham)
            results.append(
                DMETFragmentResult(
                    fragment_id=fid,
                    energy=_coerce_float(sol.get("energy")),
                    meta={key: val for key, val in sol.items() if key != "energy"},
                )
            )
        rows: list[dict[str, Any]] = []
        for r in results:
            row: dict[str, Any] = {"fragment_id": r.fragment_id, "energy": r.energy}
            row.update(r.meta)
            rows.append(row)
        return {"schema": DMET_ONE_SHOT_V1, "fragments": rows}


def _coerce_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _bath_to_json(b: DMETBathState) -> dict[str, Any]:
    meta = {k: v for k, v in b.meta.items() if k not in ("D_ao", "S_ao", "fragment_atoms")}
    return {
        "iteration": b.iteration,
        "meta": meta,
        "note": "Large arrays (D_ao, S_ao, fragment_atoms) omitted from JSON.",
    }


def pyscf_density_feedback_bath_update(
    bath: DMETBathState,
    fragments: list[DMETFragmentResult],
    *,
    mf_density: Any | None = None,
) -> DMETBathState:
    """Chemical bath update hook: attach PySCF density-matrix metadata for v1 DMET loops."""
    energies = [float(f.energy) for f in fragments if f.energy is not None]
    meta = {
        **bath.meta,
        "fragment_energy_sum": float(sum(energies)) if energies else 0.0,
        "pyscf_density_feedback": mf_density is not None,
        "n_fragments_solved": len(fragments),
    }
    if mf_density is not None:
        meta["density_trace"] = float(getattr(mf_density, "trace", lambda: 0.0)())
    return replace(bath, meta=meta)


__all__ = [
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "OneShotEmbeddingDriver",
    "pyscf_density_feedback_bath_update",
]
