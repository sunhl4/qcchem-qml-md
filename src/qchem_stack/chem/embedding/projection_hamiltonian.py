"""
Fragment **Mulliken-weighted** MO selection for projection-mode variational Hamiltonians.

Integrals use CASCI-style ``h1eff`` / ``h2eff`` on a **reordered** MO matrix (PySCF or Psi4 backend).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.casci_core_count import casci_ncore_spatial
from qchem_stack.chem.embedding.active_integrals import casci_spatial_integrals_on_mo_coeff
from qchem_stack.chem.embedding.ao_fragment import (
    mulliken_mo_populations_on_atoms as _mulliken_on_ao,
)
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.config.embedding_helpers import require_projection
from qchem_stack.contracts.schema_ids import PROJECTION_MULLIKEN_MO_AUDIT_V1
from qchem_stack.exceptions import EmbeddingError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def mulliken_mo_populations_on_atoms(
    mf: Any,
    mo: np.ndarray,
    atom_indices: list[int],
) -> np.ndarray:
    """Legacy PySCF-mf entry point; prefer :func:`ao_fragment.mulliken_mo_populations_on_atoms`."""
    from qchem_stack.chem.bridges.ao_basis_view import PySCFAOBasisView

    return _mulliken_on_ao(PySCFAOBasisView(_mf=mf), mo, atom_indices)


def select_active_mo_indices(
    weights: np.ndarray,
    n_active: int,
    *,
    frozen_mask: np.ndarray,
) -> list[int]:
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
    tag = rhf.backend_tag()
    if tag not in ("pyscf", "psi4"):
        raise EmbeddingError(
            f"projection.fragment_mulliken_mo requires backend pyscf or psi4 (got backend={tag!r})."
        )
    if cfg.scf.method != "RHF":
        raise EmbeddingError(
            "projection_quantum_hamiltonian='fragment_mulliken_mo' requires scf.method='RHF' in this stack."
        )

    ao = rhf.ao_basis_view()
    mo = np.asarray(ao.mo_coeff_ao(), dtype=float)
    n_mo = int(mo.shape[1])
    ne = int(cfg.active_space.cas.n_electrons)
    ncas = int(cfg.active_space.cas.n_orbitals)
    if ncas > n_mo or ne > 2 * ncas or ne < 0 or ne % 2 != 0:
        raise EmbeddingError("Invalid active_space electron/orbital count for MO dimensions.")

    ncore = casci_ncore_spatial(cfg, n_mo=n_mo, n_active_electrons=ne, n_active_orbitals=ncas)
    frozen_mask = np.zeros(n_mo, dtype=bool)
    frozen_mask[:ncore] = True

    atom_idx = list(require_projection(cfg.embedding).projection.fragment_atom_indices)
    weights = _mulliken_on_ao(ao, mo, atom_idx)
    selected = select_active_mo_indices(weights, ncas, frozen_mask=frozen_mask)
    active_sorted = sorted(selected)
    frozen = list(range(ncore))
    used = set(frozen) | set(active_sorted)
    rest = [j for j in range(n_mo) if j not in used]
    perm = frozen + active_sorted + rest
    mo_perm = mo[:, perm]

    constant, h1a, h2a = casci_spatial_integrals_on_mo_coeff(rhf, cfg, mo_perm)
    integral_source = f"{tag}_projection_fragment_mulliken_v1"

    audit: dict[str, Any] = {
        "schema": PROJECTION_MULLIKEN_MO_AUDIT_V1,
        "integral_source": integral_source,
        "projection_fragment_atom_indices": list(atom_idx),
        "selected_mo_indices": list(active_sorted),
        "mulliken_weights": [float(weights[j]) for j in active_sorted],
        "ncore": ncore,
        "n_active_orbitals": ncas,
        "n_active_electrons": ne,
        "mo_coeff_permutation": [int(p) for p in perm],
        "reference_energy_rhf_au": float(rhf.e_tot),
        "classical_backend": tag,
        "module": "qchem_stack.chem.embedding.projection_hamiltonian",
        "epistemic_bound": (
            "Fragment Mulliken MO screening + CASCI active integrals + user-selected fermion→qubit mapping."
        ),
    }

    dm = dict(rhf.driver_meta or {})
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        constant,
        h1a,
        h2a,
        ne,
        fermion_qubit_mapping=cfg.active_space.mapping.fermion_qubit,
        integral_source=integral_source,
        meta_extra={"projection_mulliken_mo_audit_v1": audit},
        classical_driver_meta=dm if dm else None,
        pyscf_driver_meta=dm if tag == "pyscf" else None,
    )
    return qh, audit
