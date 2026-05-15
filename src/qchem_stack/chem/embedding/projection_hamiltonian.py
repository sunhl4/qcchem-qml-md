"""
Fragment **Mulliken-weighted** MO selection for projection-mode variational Hamiltonians.

**Literature / practice**: Mulliken gross atomic populations per MO (e.g. ``C_{\\mu j}(SC)_{\\mu j}`` summed over
AOs on chosen atoms) are standard for *locality* screening of molecular orbitals. Integrals use PySCF
:class:`pyscf.mcscf.CASCI` ``get_h1eff`` / ``get_h2eff`` on a **reordered** MO matrix so the active
block matches a contiguous ``[ncore : ncore + ncas]`` slice — the same chemist-notation ``h2`` layout as
:func:`qchem_stack.chem.integrals.pyscf_active_space.active_space_integrals`.

**Epistemic boundary**: this is *not* full many-body projection embedding (environment correlated
wavefunction projected onto an impurity / active space, or bit-wise equivalence to proprietary drivers).
It is a reproducible open-stack choice: **HF MOs → fragment Mulliken ranking → fixed-(N,N_e) CASCI
core Hamiltonian → JW**.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.schmidt_production import _atom_ao_ranges
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import EmbeddingError


def mulliken_mo_populations_on_atoms(
    mf: Any,
    mo: np.ndarray,
    atom_indices: list[int],
) -> np.ndarray:
    """
    For each spatial MO column ``j``, return the Mulliken-like sum over fragment AOs ``\\mu``:

    ``\\sum_{\\mu \\in \\text{frag}} C_{\\mu j} (S C)_{\\mu j}``.
    """
    mol = mf.mol
    if min(atom_indices) < 0 or max(atom_indices) >= mol.natm:
        raise EmbeddingError("atom_indices out of range for mol.natm.")
    S = np.asarray(mf.get_ovlp(), dtype=float)
    mo_r = np.asarray(mo, dtype=float)
    ranges = _atom_ao_ranges(mol)
    frag_mask = np.zeros(mol.nao, dtype=bool)
    for ia in atom_indices:
        p0, p1 = ranges[ia]
        frag_mask[p0:p1] = True
    SC = S @ mo_r
    nmo = mo_r.shape[1]
    w = np.empty(nmo, dtype=float)
    for j in range(nmo):
        w[j] = float(np.sum(mo_r[frag_mask, j] * SC[frag_mask, j]))
    return w


def select_active_mo_indices(
    weights: np.ndarray,
    n_active: int,
    *,
    frozen_mask: np.ndarray,
) -> list[int]:
    """
    Among MOs **not** marked frozen, take indices with largest ``weights``;
    ties broken by ascending MO index (stable, deterministic).
    """
    nmo = int(weights.shape[0])
    if frozen_mask.shape != (nmo,):
        raise EmbeddingError("frozen_mask must have shape (nmo,).")
    candidates = [j for j in range(nmo) if not bool(frozen_mask[j])]
    ranked = sorted(candidates, key=lambda j: (-float(weights[j]), j))
    if len(ranked) < n_active:
        raise EmbeddingError(
            f"Not enough non-frozen orbitals for active space: need {n_active}, have {len(ranked)}."
        )
    return ranked[:n_active]


def molecular_hamiltonian_fragment_mulliken_projection(
    rhf: ClassicalMeanFieldReference,
    cfg: ExperimentConfig,
) -> tuple[QubitHamiltonian, dict[str, Any]]:
    """
    Build :class:`QubitHamiltonian` on the active space defined by Mulliken ranking on
    ``cfg.embedding.projection_fragment_atom_indices``, with (``ncore``, ``ncas``, ``nelecas``)
    matching :class:`ActiveSpaceSpec`.
    """
    tag = rhf.backend_tag()
    if tag != "pyscf":
        raise EmbeddingError(
            "projection.fragment_mulliken_mo is currently implemented on the PySCF backend "
            f"(got backend={tag!r})."
        )
    rhf_pyscf = rhf.as_pyscf_rhf_result()
    if cfg.scf.method != "RHF":
        raise EmbeddingError(
            "projection_quantum_hamiltonian='fragment_mulliken_mo' requires scf.method='RHF' in this stack."
        )
    mf = rhf_pyscf.mf
    mo_coeff = mf.mo_coeff
    if not isinstance(mo_coeff, np.ndarray):
        raise EmbeddingError(
            "fragment_mulliken_mo requires a molecular (non-k-point) real MO coefficient matrix."
        )
    mo = np.asarray(mo_coeff, dtype=float)
    n_mo = int(mo.shape[1])
    ne = int(cfg.active_space.n_active_electrons)
    ncas = int(cfg.active_space.n_active_orbitals)
    if ncas > n_mo or ne > 2 * ncas or ne < 0 or ne % 2 != 0:
        raise EmbeddingError("Invalid active_space electron/orbital count for MO dimensions.")
    from pyscf import ao2mo, mcscf

    cas = mcscf.CASCI(mf, ncas, ne)
    ncore = int(cas.ncore)
    frozen_mask = np.zeros(n_mo, dtype=bool)
    frozen_mask[:ncore] = True

    atom_idx = list(cfg.embedding.projection_fragment_atom_indices)
    weights = mulliken_mo_populations_on_atoms(mf, mo, atom_idx)
    selected = select_active_mo_indices(weights, ncas, frozen_mask=frozen_mask)
    active_sorted = sorted(selected)
    frozen = list(range(ncore))
    used = set(frozen) | set(active_sorted)
    rest = [j for j in range(n_mo) if j not in used]
    perm = frozen + active_sorted + rest
    mo_perm = mo[:, perm]

    h1, e_core = cas.get_h1eff(mo_perm)
    h2 = cas.get_h2eff(mo_perm)
    h1a = np.asarray(h1, dtype=float)
    h2a = np.asarray(h2, dtype=float)
    # Match :func:`active_space_integrals`: ``e_core`` from ``get_h1eff`` already includes
    # nuclear repulsion (and frozen-core energy when applicable).
    if h2a.ndim != 4:
        h2a = np.asarray(ao2mo.restore(1, h2a, ncas), dtype=float)
    constant = float(e_core)

    audit: dict[str, Any] = {
        "schema": "projection_mulliken_mo_audit_v1",
        "integral_source": "pyscf_projection_fragment_mulliken_v1",
        "projection_fragment_atom_indices": list(atom_idx),
        "selected_mo_indices": list(active_sorted),
        "mulliken_weights": [float(weights[j]) for j in active_sorted],
        "ncore": ncore,
        "n_active_orbitals": ncas,
        "n_active_electrons": ne,
        "mo_coeff_permutation": [int(p) for p in perm],
        "reference_energy_rhf_au": float(rhf_pyscf.e_tot),
        "module": "qchem_stack.chem.embedding.projection_hamiltonian",
        "epistemic_bound": (
            "Fragment Mulliken MO screening + CASCI active integrals + user-selected fermion→qubit mapping "
            "(Jordan–Wigner or Bravyi–Kitaev via ``active_space.fermion_qubit_mapping``) — not full projection "
            "embedding nor vendor-closed driver parity."
        ),
    }

    dm = getattr(rhf_pyscf, "driver_meta", None) or {}
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        constant,
        h1a,
        h2a,
        ne,
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
        integral_source="pyscf_projection_fragment_mulliken_v1",
        meta_extra={"projection_mulliken_mo_audit_v1": audit},
        pyscf_driver_meta=dict(dm) if dm else None,
    )
    return qh, audit
