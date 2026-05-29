"""Backend-dispatched CASCI-style active integrals on a permuted MO basis."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.config.active_space_helpers import resolve_n_electrons, resolve_n_orbitals

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def casci_spatial_integrals_on_mo_coeff(
    reference: ClassicalMeanFieldReference,
    cfg: ExperimentConfig,
    mo_perm: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return ``(constant, h1_active, h2_chemist)`` for permuted MO coefficients."""
    tag = reference.backend_tag()
    ncas = resolve_n_orbitals(cfg.active_space)
    nelec = resolve_n_electrons(cfg.active_space)

    if tag == "pyscf":
        from pyscf import ao2mo, mcscf

        from qchem_stack.chem.pyscf_typing import as_pyscf_cas, as_pyscf_mf

        pr = reference.as_pyscf_rhf_result()
        mf_p = as_pyscf_mf(pr.mf)
        cas = as_pyscf_cas(mcscf.CASCI(mf_p, ncas, nelec))
        h1, e_core = cas.get_h1eff(mo_perm)
        h2 = cas.get_h2eff(mo_perm)
        h1a = np.asarray(h1, dtype=float)
        h2a = np.asarray(h2, dtype=float)
        if h2a.ndim != 4:
            h2a = np.asarray(ao2mo.restore(1, h2a, ncas), dtype=float)
        return float(e_core), h1a, h2a

    if tag == "psi4":
        from qchem_stack.chem.pyscf_typing import as_pyscf_mf

        wfn = as_pyscf_mf(reference.mf)
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_set_ca

        ca_backup = np.asarray(wfn.Ca(), dtype=float).copy()
        try:
            psi4_set_ca(wfn, mo_perm)
            from qchem_stack.chem.integrals.psi4_active_space import (
                active_space_casci_raw_blocks_psi4,
            )

            constant, h1, h2, _impl = active_space_casci_raw_blocks_psi4(wfn, ncas, nelec)
            return float(constant), np.asarray(h1, dtype=float), np.asarray(h2, dtype=float)
        finally:
            psi4_set_ca(wfn, ca_backup)

    raise ValueError(f"casci_spatial_integrals unsupported for backend {tag!r}.")
