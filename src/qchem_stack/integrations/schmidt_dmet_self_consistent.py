"""
Schmidt embedding **outer self-consistency** (engineering DMET-style): iterate AO density → bath → FCI impurity → mix density.

This closes the loop implied by InQuanto’s DMET *workflow* at an **open, falsifiable** level: it is not identical to
closed-source bath optimization, but provides multi-cycle ``repro`` fields and the same driver shape as
:class:`~qchem_stack.integrations.dmet_self_consistent.DMETSelfConsistencyLoop`.

**Algorithm (v1)**:

#. Start from SCF ``D`` in AO.
#. Build :class:`~qchem_stack.chem.embedding.schmidt_production.SchmidtImpurityModel` from ``D``.
#. FCI in impurity space (``μ=0`` during iteration).
#. Mix ``D <- (1-α) D + α · sym(C_imp dm1 C_imp^T)``, renormalize ``Tr(S D) = n_electron``.
#. Repeat until ``max_cycles`` or Frobenius norm of ``(dm1 - γ)`` falls below tolerance,
   with ``γ = C_imp^T S D S C_imp``.

Multi-fragment sweeps are implemented via :meth:`~qchem_stack.integrations.dmet_self_consistent.DMETSelfConsistencyLoop.run_with_sequential_bath_updates`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult
from qchem_stack.chem.embedding.schmidt_production import (
    SchmidtImpurityModel,
    SchmidtProductionError,
    build_schmidt_impurity_integrals,
    fci_impurity_spatial_ground,
)
from qchem_stack.integrations.dmet_self_consistent import (
    DMETBathState,
    DMETContext,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
)


@dataclass
class FCISchmidtImpuritySolver:
    """Solve fragment = FCI on a :class:`SchmidtImpurityModel` (density + bath already fixed in model)."""

    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
        _ = fragment_id
        model = hamiltonian
        if not isinstance(model, SchmidtImpurityModel):
            raise TypeError("FCISchmidtImpuritySolver expects SchmidtImpurityModel")
        e_elec, dm1, _c = fci_impurity_spatial_ground(model, mu=0.0)
        C = model.C_imp_ao
        if C is None:
            raise SchmidtProductionError("impurity model missing C_imp_ao")
        return {
            "energy": float(e_elec + model.constant),
            "fci_electronic_au": float(e_elec),
            "dm1_impurity_spatial": dm1.tolist(),
            "C_imp_ao": C.tolist(),
        }


def _sequential_schmidt_density_mix(
    bath: DMETBathState,
    result: DMETFragmentResult,
    *,
    mixing_alpha: float,
) -> DMETBathState:
    D = np.asarray(bath.meta["D_ao"], dtype=float)
    S = np.asarray(bath.meta["S_ao"], dtype=float)
    nel = int(bath.meta["n_electron"])
    dm1 = np.asarray(result.meta["dm1_impurity_spatial"], dtype=float)
    C = np.asarray(result.meta["C_imp_ao"], dtype=float)
    gamma = C.T @ S @ D @ S @ C
    delta_fro = float(np.linalg.norm(dm1 - gamma))
    cur = float(bath.meta.get("current_sweep_max_delta", 0.0))
    mx = max(cur, delta_fro)
    alpha = float(mixing_alpha)
    d_raw = C @ dm1 @ C.T
    d_sym = 0.5 * (d_raw + d_raw.T)
    d_new = (1.0 - alpha) * D + alpha * d_sym
    tr = float(np.trace(S @ d_new))
    if tr > 1e-14:
        d_new = d_new * (float(nel) / tr)
    return replace(
        bath,
        meta={
            **bath.meta,
            "D_ao": d_new,
            "current_sweep_max_delta": mx,
        },
    )


def run_schmidt_density_feedback_cycles(
    rhf: PySCFRHFResult,
    *,
    fragment_atom_indices: list[int],
    n_bath_orbitals: int,
    max_impurity_spatial_orbitals: int,
    max_cycles: int,
    mixing_alpha: float,
    convergence_tol: float,
) -> tuple[SchmidtImpurityModel, dict[str, Any], np.ndarray]:
    """
    Run outer embedding iterations; return the **last** impurity model, audit dict, and **final AO density** ``D``.

    Raises
    ------
    SchmidtProductionError
        Invalid dimensions or caps.
    """
    if max_cycles < 1:
        raise SchmidtProductionError("max_cycles must be >= 1")
    mf = rhf.mf
    mol = mf.mol
    nel = int(mol.nelectron)
    S = np.asarray(mf.get_ovlp(), dtype=float)
    D = np.asarray(mf.make_rdm1(), dtype=float)

    history: list[dict[str, Any]] = []
    model: SchmidtImpurityModel | None = None
    converged_early = False

    for k in range(max_cycles):
        model = build_schmidt_impurity_integrals(
            rhf,
            fragment_atom_indices=list(fragment_atom_indices),
            n_bath_orbitals=int(n_bath_orbitals),
            max_impurity_spatial_orbitals=int(max_impurity_spatial_orbitals),
            density_ao=D,
        )
        C = model.C_imp_ao
        if C is None:
            raise SchmidtProductionError("impurity model missing C_imp_ao")
        e_elec, dm1, _meta = fci_impurity_spatial_ground(model, mu=0.0)
        gamma = C.T @ S @ D @ S @ C
        delta = dm1 - gamma
        delta_fro = float(np.linalg.norm(delta))
        history.append(
            {
                "cycle": k,
                "fci_electronic_au": e_elec,
                "delta_gamma_frobenius": delta_fro,
                "trace_gamma": float(np.trace(gamma)),
                "trace_dm1_fci": float(np.trace(dm1)),
            }
        )
        if k == max_cycles - 1:
            break
        if delta_fro < float(convergence_tol) and k > 0:
            converged_early = True
            break
        d_raw = C @ dm1 @ C.T
        d_sym = 0.5 * (d_raw + d_raw.T)
        d_new = (1.0 - float(mixing_alpha)) * D + float(mixing_alpha) * d_sym
        tr = float(np.trace(S @ d_new))
        if tr > 1e-14:
            d_new = d_new * (float(nel) / tr)
        D = d_new

    if model is None:
        raise SchmidtProductionError("no impurity model produced")

    report: dict[str, Any] = {
        "schema": "schmidt_dmet_density_feedback_v1",
        "cycles_requested": int(max_cycles),
        "cycles_executed": len(history),
        "converged_early_on_gamma": converged_early,
        "mixing_alpha": float(mixing_alpha),
        "convergence_tol": float(convergence_tol),
        "history": history,
        "caveat": (
            "Density mixing uses a low-rank impurity AO surrogate; not equivalent to full global "
            "DMET correlation potential fitting or multi-fragment global matching."
        ),
    }
    return model, report, D


def run_schmidt_multifragment_density_cycles(
    rhf: PySCFRHFResult,
    *,
    fragment_atom_groups: list[list[int]],
    fragment_labels: list[str] | None,
    primary_fragment_index: int,
    n_bath_orbitals: int,
    max_impurity_spatial_orbitals: int,
    max_cycles: int,
    mixing_alpha: float,
    convergence_tol: float,
) -> tuple[SchmidtImpurityModel, dict[str, Any], np.ndarray]:
    """
    **Multi-fragment** Gauss–Seidel on global ``D``, implemented with
    :class:`~qchem_stack.integrations.dmet_self_consistent.DMETSelfConsistencyLoop`.

    After outer cycles, rebuild the **primary** impurity model from final ``D``.
    """
    if not fragment_atom_groups:
        raise SchmidtProductionError("fragment_atom_groups must be non-empty")
    if any(not g for g in fragment_atom_groups):
        raise SchmidtProductionError("each fragment group must list at least one atom index")
    if primary_fragment_index < 0 or primary_fragment_index >= len(fragment_atom_groups):
        raise SchmidtProductionError("primary_fragment_index out of range")
    if max_cycles < 1:
        raise SchmidtProductionError("max_cycles must be >= 1")

    labs_in = [str(x).strip() for x in (fragment_labels or []) if str(x).strip()]
    if len(labs_in) == len(fragment_atom_groups):
        labs = labs_in
    else:
        labs = [f"fragment_{i}" for i in range(len(fragment_atom_groups))]
    fid_atoms = {labs[i]: list(fragment_atom_groups[i]) for i in range(len(labs))}

    mf = rhf.mf
    mol = mf.mol
    nel = int(mol.nelectron)
    S = np.asarray(mf.get_ovlp(), dtype=float)
    D = np.asarray(mf.make_rdm1(), dtype=float)
    alpha = float(mixing_alpha)
    tol = float(convergence_tol)

    ctx = DMETContext(fragments=list(labs))
    ctx.register_solver(FCISchmidtImpuritySolver())
    loop = DMETSelfConsistencyLoop(ctx, max_cycles=int(max_cycles))

    initial = DMETBathState(
        meta={
            "D_ao": D.copy(),
            "S_ao": S.copy(),
            "n_electron": nel,
            "fragment_atoms": fid_atoms,
            "current_sweep_max_delta": 0.0,
        }
    )

    def build_f(fid: str, bath: DMETBathState) -> SchmidtImpurityModel:
        atoms = bath.meta["fragment_atoms"][fid]
        dloc = np.asarray(bath.meta["D_ao"], dtype=float)
        return build_schmidt_impurity_integrals(
            rhf,
            fragment_atom_indices=list(atoms),
            n_bath_orbitals=int(n_bath_orbitals),
            max_impurity_spatial_orbitals=int(max_impurity_spatial_orbitals),
            density_ao=dloc,
        )

    def upd(bath: DMETBathState, res: DMETFragmentResult) -> DMETBathState:
        return _sequential_schmidt_density_mix(bath, res, mixing_alpha=alpha)

    def conv(_prev: DMETBathState, bath: DMETBathState, k: int) -> bool:
        return k > 0 and float(bath.meta.get("last_sweep_max_delta", 1.0)) < tol

    dmet_rep = loop.run_with_sequential_bath_updates(
        initial_bath=initial,
        build_fragment_hamiltonian=build_f,
        update_bath_sequential=upd,
        is_converged=conv,
    )
    bath_fin = dmet_rep.pop("_final_bath_state")
    D_final = np.asarray(bath_fin.meta["D_ao"], dtype=float)

    dmet_public = {k: v for k, v in dmet_rep.items() if not str(k).startswith("_")}
    primary_atoms = list(fragment_atom_groups[int(primary_fragment_index)])
    final_model = build_schmidt_impurity_integrals(
        rhf,
        fragment_atom_indices=primary_atoms,
        n_bath_orbitals=int(n_bath_orbitals),
        max_impurity_spatial_orbitals=int(max_impurity_spatial_orbitals),
        density_ao=D_final,
    )

    report: dict[str, Any] = {
        "schema": "schmidt_dmet_multifragment_density_feedback_v1",
        "n_fragments": len(fragment_atom_groups),
        "fragment_labels_used": list(labs),
        "primary_fragment_index": int(primary_fragment_index),
        "outer_cycles_requested": int(max_cycles),
        "outer_cycles_executed": int(dmet_public.get("cycles", 0)),
        "converged_early_on_sweep_max_delta": bool(dmet_public.get("converged", False)),
        "mixing_alpha": alpha,
        "convergence_tol": tol,
        "dmet_self_consistency_loop": dmet_public,
        "caveat": (
            "Gauss–Seidel mixing driven by DMETSelfConsistencyLoop.run_with_sequential_bath_updates + FCI. "
            "Not a full global DMET correlation-potential fit."
        ),
    }
    return final_model, report, D_final
