"""Build PySCF RHF objects aligned with a unified :class:`ClassicalMeanFieldReference`.

Used when PySCF-only algorithms (AVAS, ``mrpt.NEVPT``, ``ao2mo``) must run on orbitals
from PySCF **or** Psi4 without repeating an SCF in PySCF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.ao_basis_view import ao_basis_view_from_reference
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def build_pyscf_rhf_shadow(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    run_scf_if_needed: bool = False,
) -> Any:
    """Return a PySCF ``scf.RHF`` mean-field object consistent with ``reference``.

    Parameters
    ----------
    run_scf_if_needed
        When ``True``, call ``mf.kernel()`` (PySCF SCF). Default ``False``: import
        MO coefficients (and energy) from the unified reference only.
    """
    from qchem_stack.chem.solvers.pyscf_solver import require_pyscf

    gto, scf = require_pyscf()
    ao = ao_basis_view_from_reference(reference)
    sys = cfg.molecule
    atom = [
        (sym, tuple(map(float, row)))
        for sym, row in zip(sys.symbols, sys.coordinates_in_bohr(), strict=True)
    ]
    mol = gto.M(
        atom=atom,
        basis=sys.basis,
        charge=sys.charge,
        spin=int(sys.multiplicity) - 1,
        unit="Bohr",
    )
    mf = scf.RHF(mol)
    mo_ref = np.asarray(ao.mo_coeff_ao(), dtype=float)
    if mo_ref.shape[0] != mol.nao_nr():
        raise PipelineError(
            f"PySCF shadow reference: AO dimension mismatch (nao_pyscf={mol.nao_nr()}, "
            f"reference={mo_ref.shape[0]})."
        )
    if run_scf_if_needed:
        mf.kernel()
        if not getattr(mf, "converged", False):
            raise PipelineError("PySCF shadow SCF did not converge.")
    else:
        mf.mo_coeff = mo_ref
        mf.mo_occ = _occupied_mask_closed_shell(mol, int(sys.multiplicity))
        mf.converged = True
        mo_e = getattr(reference, "mo_energy", None)
        if mo_e is not None and len(np.asarray(mo_e).ravel()) == mf.mo_coeff.shape[1]:
            mf.mo_energy = np.asarray(mo_e, dtype=float).ravel()
        else:
            from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
                _mo_energy_from_fock,
            )

            mf.mo_energy = _mo_energy_from_fock(mf)
    mf.e_tot = float(reference.e_tot)
    return mf


def _occupied_mask_closed_shell(mol: Any, multiplicity: int) -> np.ndarray:
    """Doubly occupied spatial orbitals for closed-shell ``multiplicity=1``."""
    if multiplicity != 1:
        raise PipelineError(
            "PySCF shadow occupied mask without SCF supports multiplicity=1 (closed shell) only."
        )
    nao = int(mol.nao_nr())
    nelec = int(mol.nelectron)
    if nelec % 2 != 0:
        raise PipelineError("PySCF shadow RHF requires even electron count.")
    nocc = nelec // 2
    if nocc > nao:
        raise PipelineError(f"PySCF shadow: nocc={nocc} exceeds nao={nao}.")
    occ = np.zeros(nao, dtype=float)
    occ[:nocc] = 2.0
    return occ
