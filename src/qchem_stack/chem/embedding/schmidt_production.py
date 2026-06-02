"""
Production-oriented **Schmidt atomic embedding**: fragment AO span + spectral-derived bath (DMET-shaped).

Delivers closed-shell impurity spatial integrals (:math:`h_1, h_2`), optional chemical-potential / FCI audit,
and a path to :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian` via
:func:`~qchem_stack.chem.hamiltonian.qubit_hamiltonian_from_spatial_chemist_integrals`.

**Scope**: closed-shell **RHF / RKS** reference (validated). ROHF/UHF: explicit error.

This is **not** full analytic bath-fitting DMET from the literature unless you enable
``embedding.dmet.schmidt.dmet_max_cycles > 1`` (:mod:`qchem_stack.chem.embedding.schmidt_dmet_self_consistent` —
density-fed spectral bath + FCI-driven mixing).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy.linalg import eigh

from qchem_stack.chem.bridges.ao_basis_view import require_ao_basis_view
from qchem_stack.chem.embedding.ao_fragment import fragment_ao_indices
from qchem_stack.chem.embedding.impurity_eri import impurity_eri_chemist
from qchem_stack.chem.embedding.schmidt_production_model import (
    SchmidtImpurityModel,
    SchmidtProductionError,
)
from qchem_stack.contracts.schema_ids import (
    SCHMIDT_IMPURITY_INTEGRALS_V1,
)
from qchem_stack.quantum.algorithms.tolerances import (
    SCHMIDT_ORTHONORMALITY_TOLERANCE,
    SCHMIDT_SINGULARITY_TOLERANCE,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


def _atom_ao_ranges(mol: Any) -> list[tuple[int, int]]:
    """PySCF ``mol`` helper retained for tests importing this symbol."""
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
    if np.min(w) < SCHMIDT_SINGULARITY_TOLERANCE:
        raise SchmidtProductionError(
            "reduced overlap matrix for column orthonormalization is singular"
        )
    return cast("np.ndarray", C @ v @ np.diag(1.0 / np.sqrt(w)) @ v.T)


def _s_projector(C: np.ndarray, S: np.ndarray) -> np.ndarray:
    """``P`` such that ``P @ C_frag = C_frag`` (``S``-metric projector onto span(C))."""
    return cast("np.ndarray", C @ C.T @ S)


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
    basis = require_ao_basis_view(
        rhf,
        context="Schmidt impurity integral builder",
        error_cls=SchmidtProductionError,
    )
    ref_name = basis.reference_class_name()
    if ref_name not in ("RHF", "RKS"):
        raise SchmidtProductionError(
            f"Schmidt production requires RHF/RKS reference; got {ref_name}. "
            "ROHF/UHF require a follow-on implementation."
        )

    nao = int(basis.nao)
    S = basis.overlap_ao()
    D = np.asarray(density_ao, dtype=float) if density_ao is not None else basis.make_rdm1_ao()
    if D.shape != (nao, nao):
        raise SchmidtProductionError("unexpected AO density matrix shape")

    frag_ao = fragment_ao_indices(basis, fragment_atom_indices)
    env_ao = [i for i in range(nao) if i not in set(frag_ao)]
    if not env_ao or not frag_ao:
        raise SchmidtProductionError("fragment and environment AO sets must both be non-empty")

    raw_frag = np.zeros((nao, len(frag_ao)))
    for col, ao_idx in enumerate(frag_ao):
        raw_frag[ao_idx, col] = 1.0
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
    for r, ao_idx in enumerate(env_ao):
        raw_bath[ao_idx, :] = Cb[r, :]

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
    if res > SCHMIDT_ORTHONORMALITY_TOLERANCE:
        raise SchmidtProductionError(
            f"impurity MO block not S-orthonormal within tolerance (residual={res})"
        )

    dm_mo = C_imp.T @ S @ D @ S @ C_imp
    nelec_mo = int(round(float(np.trace(dm_mo))))
    nelec_mo -= nelec_mo % 2
    nelec_mo = max(2, min(nelec_mo, 2 * n_imp))

    h1_ao = basis.fock_ao(density_ao=D)
    h1e = C_imp.T @ h1_ao @ C_imp

    eri = impurity_eri_chemist(basis, C_imp, molecular_system=rhf.molecular_system)

    enuc = float(basis.energy_nuc_au())
    n_frag_sp = int(C_frag.shape[1])
    n_bath_sp = int(C_bath.shape[1])

    meta: dict[str, Any] = {
        "schema": SCHMIDT_IMPURITY_INTEGRALS_V1,
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


from qchem_stack.chem.embedding.schmidt_production_fci import (
    apply_chemical_potential_fragment_block,
    bisection_mu_for_fragment_electron_count,
    fci_fragment_ground_state,
    fci_impurity_spatial_ground,
    fragment_mulliken_electrons,
)

__all__ = [
    "SchmidtImpurityModel",
    "SchmidtProductionError",
    "apply_chemical_potential_fragment_block",
    "bisection_mu_for_fragment_electron_count",
    "build_schmidt_impurity_integrals",
    "fci_fragment_ground_state",
    "fci_impurity_spatial_ground",
    "fragment_mulliken_electrons",
]
