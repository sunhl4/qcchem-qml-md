"""
Production-oriented **Schmidt atomic embedding**: fragment AO span + spectral-derived bath (DMET-shaped).

Delivers closed-shell impurity spatial integrals (:math:`h_1, h_2`), optional chemical-potential / FCI audit,
and a path to :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian` via
:func:`~qchem_stack.chem.hamiltonian.qubit_hamiltonian_from_spatial_chemist_integrals`.

**Scope**: closed-shell **RHF / RKS** reference (validated). ROHF/UHF: explicit error.

This is **not** full analytic bath-fitting DMET from the literature unless you enable
``schmidt_dmet_max_cycles > 1`` (:mod:`qchem_stack.integrations.schmidt_dmet_self_consistent` —
density-fed spectral bath + FCI-driven mixing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.linalg import eigh

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.exceptions import EmbeddingError


class SchmidtProductionError(EmbeddingError):
    """Raised when embedding inputs are invalid or unsafe for the configured caps."""


def _atom_ao_ranges(mol: Any) -> list[tuple[int, int]]:
    sl = mol.aoslice_by_atom()
    ranges: list[tuple[int, int]] = []
    for ia in range(mol.natm):
        row = sl[ia]
        p0, p1 = int(row[2]), int(row[3])
        ranges.append((p0, p1))
    return ranges


def _fragment_ao_indices(mol: Any, atom_indices: list[int]) -> list[int]:
    if not atom_indices:
        raise SchmidtProductionError("fragment_atom_indices must be non-empty.")
    if min(atom_indices) < 0 or max(atom_indices) >= mol.natm:
        raise SchmidtProductionError(
            "atom_indices must be valid 0-based atom indices for mol.natm."
        )
    ranges = _atom_ao_ranges(mol)
    idx: list[int] = []
    for ia in atom_indices:
        p0, p1 = ranges[ia]
        idx.extend(range(p0, p1))
    return sorted(set(idx))


def _orthonormalize_columns(C: np.ndarray, S: np.ndarray) -> np.ndarray:
    M = C.T @ S @ C
    w, v = eigh(M)
    if np.min(w) < 1e-12:
        raise SchmidtProductionError(
            "reduced overlap matrix for column orthonormalization is singular"
        )
    return C @ v @ np.diag(1.0 / np.sqrt(w)) @ v.T


def _s_projector(C: np.ndarray, S: np.ndarray) -> np.ndarray:
    """``P`` such that ``P @ C_frag = C_frag`` (``S``-metric projector onto span(C))."""
    return C @ C.T @ S


@dataclass
class SchmidtImpurityModel:
    """Impurity spatial integrals + bookkeeping for audit / JW."""

    constant: float
    h1: np.ndarray
    h2: np.ndarray
    n_spatial_orbitals: int
    n_alpha_electrons: int
    n_beta_electrons: int
    n_fragment_spatial_orbitals: int
    n_bath_spatial_orbitals: int
    fragment_atom_indices: list[int]
    meta: dict[str, Any] = field(default_factory=dict)
    C_imp_ao: np.ndarray | None = field(default=None, repr=False)
    """AO × impurity MO coefficients (``S``-orthonormal columns); used for density-feedback loops only."""


def build_schmidt_impurity_integrals(
    rhf: ClassicalMeanFieldReference,
    *,
    fragment_atom_indices: list[int],
    n_bath_orbitals: int,
    max_impurity_spatial_orbitals: int = 14,
    density_ao: np.ndarray | None = None,
) -> SchmidtImpurityModel:
    """
    Build closed-shell impurity integrals in a Schmidt-truncated spatial basis.

    Bath vectors: leading generalized eigenvectors of environment ``(D, S)``, then
    ``S``-orthogonalized to the fragment AO span.

    Parameters
    ----------
    density_ao
        Optional AO density for bath env (D,S) and for :math:`\\gamma` embedding in MF;
        default is converged SCF ``mf.make_rdm1()``.
    """
    tag = rhf.backend_tag()
    if tag != "pyscf":
        raise SchmidtProductionError(
            "Schmidt impurity integral builder is currently implemented for backend='pyscf' "
            f"(got backend={tag!r})."
        )
    rhf_pyscf = rhf.as_pyscf_rhf_result()
    mf = rhf_pyscf.mf
    if hasattr(mf, "raw_handle") and callable(getattr(mf, "raw_handle")):
        mf = mf.raw_handle()
    mol = mf.mol
    ref_name = mf.__class__.__name__
    if ref_name not in ("RHF", "RKS"):
        raise SchmidtProductionError(
            f"Schmidt production requires RHF/RKS reference; got {ref_name}. "
            "ROHF/UHF require a follow-on implementation."
        )
    if getattr(mol, "nelectron", 0) % 2 != 0:
        raise SchmidtProductionError(
            "Schmidt production path requires an even electron count (closed shell)."
        )

    nao = int(mol.nao_nr())
    S = np.asarray(mf.get_ovlp(), dtype=float)
    if density_ao is not None:
        D = np.asarray(density_ao, dtype=float)
    else:
        D = np.asarray(mf.make_rdm1(), dtype=float)
    if D.shape != (nao, nao):
        raise SchmidtProductionError("unexpected AO density matrix shape")

    frag_ao = _fragment_ao_indices(mol, fragment_atom_indices)
    env_ao = [i for i in range(nao) if i not in set(frag_ao)]
    if not env_ao or not frag_ao:
        raise SchmidtProductionError("fragment and environment AO sets must both be non-empty")

    raw_frag = np.zeros((nao, len(frag_ao)))
    for col, ao in enumerate(frag_ao):
        raw_frag[ao, col] = 1.0
    C_frag = _orthonormalize_columns(raw_frag, S)

    D_e = D[np.ix_(env_ao, env_ao)]
    S_e = S[np.ix_(env_ao, env_ao)]
    evals, evecs = eigh(D_e, S_e)
    n_bath = int(n_bath_orbitals)
    if n_bath <= 0:
        raise SchmidtProductionError("n_bath_orbitals must be positive")
    take = sorted(range(len(evals)), key=lambda i: float(evals[i]), reverse=True)[:n_bath]
    if len(take) < n_bath:
        raise SchmidtProductionError("not enough environment AOs to build requested bath dimension")
    Cb = evecs[:, take]
    raw_bath = np.zeros((nao, len(take)))
    for r, ao in enumerate(env_ao):
        raw_bath[ao, :] = Cb[r, :]

    P_frag = _s_projector(C_frag, S)
    bath_pre = raw_bath - P_frag @ raw_bath
    C_bath = _orthonormalize_columns(bath_pre, S)

    C_imp = np.hstack([C_frag, C_bath])
    n_imp = C_imp.shape[1]
    cap = int(max_impurity_spatial_orbitals)
    if n_imp > cap:
        raise SchmidtProductionError(
            f"impurity spatial dimension {n_imp} exceeds max_impurity_spatial_orbitals={cap}. "
            "Lower schmidt_n_bath_spatial or raise the cap explicitly."
        )

    metric = C_imp.T @ S @ C_imp
    res = float(np.max(np.abs(metric - np.eye(n_imp))))
    if res > 1e-8:
        raise SchmidtProductionError(
            f"impurity MO block not S-orthonormal within tolerance (residual={res})"
        )

    dm_mo = C_imp.T @ S @ D @ S @ C_imp
    nelec_mo = int(round(float(np.trace(dm_mo))))
    nelec_mo -= nelec_mo % 2
    nelec_mo = max(2, min(nelec_mo, 2 * n_imp))

    h1_ao = np.asarray(mf.get_fock(dm=D), dtype=float)
    h1e = C_imp.T @ h1_ao @ C_imp

    from pyscf import ao2mo

    eri = ao2mo.restore(1, ao2mo.full(mol, C_imp, compact=False), n_imp)

    enuc = float(mol.energy_nuc())
    n_frag_sp = int(C_frag.shape[1])
    n_bath_sp = int(C_bath.shape[1])

    meta: dict[str, Any] = {
        "schema": "schmidt_impurity_integrals_v1",
        "reference": ref_name,
        "nao": nao,
        "n_impurity_spatial": n_imp,
        "n_fragment_spatial": n_frag_sp,
        "n_bath_spatial": n_bath_sp,
        "fragment_atom_indices": list(fragment_atom_indices),
        "fragment_ao_indices": frag_ao,
        "truncated_closed_shell_electrons": nelec_mo,
        "orthonormal_metric_residual": res,
        "density_ao_is_override": bool(density_ao is not None),
        "caveat": (
            "Spectral bath from env (D,S) at supplied/global density; Schmidt-orthogonalized to fragment AOs. "
            "Not a closed-form correlated Schmidt of a CAS wavefunction unless density is iterated "
            "(see schmidt_dmet_self_consistent)."
        ),
    }
    return SchmidtImpurityModel(
        constant=enuc,
        h1=h1e,
        h2=np.asarray(eri, dtype=float),
        n_spatial_orbitals=n_imp,
        n_alpha_electrons=nelec_mo // 2,
        n_beta_electrons=nelec_mo // 2,
        n_fragment_spatial_orbitals=n_frag_sp,
        n_bath_spatial_orbitals=n_bath_sp,
        fragment_atom_indices=list(fragment_atom_indices),
        meta=meta,
        C_imp_ao=np.asarray(C_imp, dtype=float),
    )


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
        "schema": "schmidt_fci_fragment_v1",
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
            "schema": "dmet_mu_bisection_v1",
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
        "schema": "dmet_mu_bisection_v1",
        "status": "converged",
        "mu_au": float(mu_mid),
        "target_fragment_electrons": target,
        "max_iter": int(max_iter),
        "tol": float(tol),
        "fci_at_mu": fci_fin,
    }
