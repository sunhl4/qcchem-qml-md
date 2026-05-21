"""Active-space integral export for :class:`Psi4IntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.contracts.schema_ids import PSI4_ACTIVE_SPACE_INTEGRALS_V1

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver


def resolve_active_space_spec(kwargs: dict[str, Any]) -> tuple[int, int]:
    ncas_raw = kwargs.get("n_active_orbitals", kwargs.get("ncas"))
    nele_raw = kwargs.get("n_active_electrons", kwargs.get("nelecas"))
    if ncas_raw is None or nele_raw is None:
        raise ValueError(
            "get_integrals requires n_active_orbitals/n_active_electrons (aliases: ncas/nelecas)."
        )
    ncas = int(ncas_raw)
    nelecas = int(nele_raw)
    if ncas <= 0 or nelecas <= 0:
        raise ValueError("n_active_orbitals and n_active_electrons must be positive integers.")
    return ncas, nelecas


def get_active_space_integrals(
    solver: Psi4IntegralSolver,
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    ncas, nelecas = resolve_active_space_spec(kwargs)
    if solver._method not in ("RHF", "ROHF"):
        raise NotImplementedError(
            f"Psi4 get_integrals supports RHF/ROHF only (got method={solver._method!r})."
        )
    mf_res = solver.run_molecular_mean_field()
    wfn = mf_res.mf.raw_handle() if hasattr(mf_res.mf, "raw_handle") else mf_res.mf
    from qchem_stack.chem.integral_convention import (
        spatial_mo_eri_pyscf_to_openfermion_mo_ordering,
    )
    from qchem_stack.chem.integrals.psi4_active_space import active_space_casci_raw_blocks_psi4

    constant, h1, h2, _casci_impl = active_space_casci_raw_blocks_psi4(wfn, ncas, nelecas)
    h2_chemist = np.asarray(h2, dtype=float)
    h2_openfermion = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_chemist)
    return {
        "schema": PSI4_ACTIVE_SPACE_INTEGRALS_V1,
        "backend_id": "psi4",
        "integral_representation": "mo",
        "constant": float(constant),
        "n_active_orbitals": ncas,
        "n_active_electrons": nelecas,
        "h1_spatial_mo": np.asarray(h1, dtype=float),
        "h2_spatial_mo_chemist": h2_chemist,
        "h2_spatial_mo_openfermion": h2_openfermion,
        "openfermion_bridge": "psi4_mo_to_openfermion_v1",
        "scf_energy": float(mf_res.e_tot),
        "psi4_converged": True,
    }
