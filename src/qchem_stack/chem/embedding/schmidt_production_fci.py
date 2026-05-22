"""FCI / chemical-potential helpers for Schmidt production embedding."""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.embedding.schmidt_production_model import (
    SchmidtImpurityModel,
    SchmidtProductionError,
)
from qchem_stack.contracts.schema_ids import DMET_MU_BISECTION_V1, SCHMIDT_FCI_FRAGMENT_V1


def fragment_mulliken_electrons(D: np.ndarray, S: np.ndarray, frag_ao: list[int]) -> float:
    if not frag_ao:
        return 0.0
    Pf = np.zeros((D.shape[0], D.shape[0]))
    for i in frag_ao:
        Pf[i, i] = 1.0
    return float(np.trace(S @ D @ Pf))


def apply_chemical_potential_fragment_block(
    h1: np.ndarray,
    *,
    mu: float,
    n_fragment_spatial_orbitals: int,
) -> np.ndarray:
    """Add ``mu`` to diagonal fragment block (spatial indices ``0 .. n_frag-1``)."""
    h1m = np.array(h1, dtype=float, copy=True)
    n_frag = int(n_fragment_spatial_orbitals)
    for i in range(n_frag):
        h1m[i, i] += float(mu)
    return h1m


def fci_impurity_spatial_ground(
    model: SchmidtImpurityModel,
    *,
    mu: float = 0.0,
) -> tuple[float, np.ndarray, dict[str, Any]]:
    """FCI electronic energy (no constant) + spatial 1-RDM + compact meta."""
    norb = model.n_spatial_orbitals
    ne = model.n_alpha_electrons + model.n_beta_electrons
    if ne % 2 != 0:
        raise SchmidtProductionError("FCI branch requires even electron count in impurity model")
    nocc_a = ne // 2
    h1 = apply_chemical_potential_fragment_block(
        model.h1, mu=mu, n_fragment_spatial_orbitals=model.n_fragment_spatial_orbitals
    )
    from pyscf.fci import direct_spin0

    cisolver = direct_spin0.FCI()
    cisolver.max_cycle = 500
    e0, civec = cisolver.kernel(h1, model.h2, norb, (nocc_a, nocc_a))
    dm1 = np.asarray(direct_spin0.make_rdm1(civec, norb, (nocc_a, nocc_a)), dtype=float)
    n_frag_sp = model.n_fragment_spatial_orbitals
    n_frag_trace = float(np.trace(dm1[:n_frag_sp, :n_frag_sp])) if n_frag_sp > 0 else 0.0
    meta = {
        "mu_on_fragment_diagonal": float(mu),
        "fci_fragment_spatial_trace_1rdm": n_frag_trace,
        "n_spatial_orbitals": int(norb),
        "n_electrons": int(ne),
    }
    return float(e0), dm1, meta


def fci_fragment_ground_state(model: SchmidtImpurityModel, *, mu: float = 0.0) -> dict[str, Any]:
    """FCI on impurity spatial space (exact within truncated basis); for audit / μ calibration."""
    e0, _dm1, compact = fci_impurity_spatial_ground(model, mu=mu)
    n_frag_trace = float(compact["fci_fragment_spatial_trace_1rdm"])
    return {
        "schema": SCHMIDT_FCI_FRAGMENT_V1,
        "energy_total_au": float(e0) + float(model.constant),
        "energy_electronic_au": float(e0),
        "nuc_repulsion_included_in_total": True,
        "constant_au": float(model.constant),
        "mu_on_fragment_diagonal": float(mu),
        "fci_fragment_spatial_trace_1rdm": n_frag_trace,
        "n_spatial_orbitals": int(compact["n_spatial_orbitals"]),
        "n_electrons": int(compact["n_electrons"]),
    }


def bisection_mu_for_fragment_electron_count(
    model: SchmidtImpurityModel,
    *,
    target_fragment_electrons: float,
    mu_lo: float = -80.0,
    mu_hi: float = 80.0,
    max_iter: int = 48,
    tol: float = 5e-3,
) -> tuple[float, dict[str, Any]]:
    """
    Match FCI fragment spatial 1-RDM trace to ``target`` via scalar μ on fragment diagonal.

    Returns ``(mu, report)``. If bracketing fails, ``mu=0.0`` and report explains.
    """

    def n_frag_at_mu(mu: float) -> float:
        h1 = apply_chemical_potential_fragment_block(
            model.h1, mu=mu, n_fragment_spatial_orbitals=model.n_fragment_spatial_orbitals
        )
        from pyscf.fci import direct_spin0

        norb = model.n_spatial_orbitals
        ne = model.n_alpha_electrons + model.n_beta_electrons
        na = ne // 2
        cisolver = direct_spin0.FCI()
        _, civec = cisolver.kernel(h1, model.h2, norb, (na, na))
        dm1 = direct_spin0.make_rdm1(civec, norb, (na, na))
        nfs = model.n_fragment_spatial_orbitals
        return float(np.trace(dm1[:nfs, :nfs])) if nfs > 0 else 0.0

    target = float(target_fragment_electrons)
    span = max(abs(float(mu_hi)), abs(float(mu_lo)), 1.0)
    a, b = -span, span
    fa = n_frag_at_mu(a) - target
    fb = n_frag_at_mu(b) - target
    expand = 0
    while fa * fb > 0 and expand < 24:
        span *= 2.0
        a, b = -span, span
        fa = n_frag_at_mu(a) - target
        fb = n_frag_at_mu(b) - target
        expand += 1

    if fa * fb > 0:
        f0 = fci_fragment_ground_state(model, mu=0.0)
        return 0.0, {
            "schema": DMET_MU_BISECTION_V1,
            "status": "no_bracket",
            "note": "Mu root not bracketed in configured window; using mu=0.",
            "fci_mu_zero": f0,
            "target_fragment_electrons": target,
        }

    mu_mid = 0.0
    for _ in range(int(max_iter)):
        mu_mid = 0.5 * (a + b)
        fm = n_frag_at_mu(mu_mid) - target
        if abs(fm) < tol:
            break
        fa = n_frag_at_mu(a) - target
        if fa * fm <= 0:
            b = mu_mid
        else:
            a = mu_mid

    fci_fin = fci_fragment_ground_state(model, mu=mu_mid)
    return float(mu_mid), {
        "schema": DMET_MU_BISECTION_V1,
        "status": "converged",
        "mu_au": float(mu_mid),
        "target_fragment_electrons": target,
        "max_iter": int(max_iter),
        "tol": float(tol),
        "fci_at_mu": fci_fin,
    }
