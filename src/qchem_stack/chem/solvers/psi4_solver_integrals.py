"""Active-space integral export for :class:`Psi4IntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.solvers._active_space_common import resolve_active_space_spec
from qchem_stack.contracts.schema_ids import PSI4_ACTIVE_SPACE_INTEGRALS_V1

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver


def _resolve_psi4_wavefunction(
    solver: Psi4IntegralSolver,
    kwargs: dict[str, Any],
) -> tuple[Any, float, MolecularMeanFieldResult | None]:
    wfn = kwargs.get("wfn")
    if wfn is not None:
        scf_energy = kwargs.get("scf_energy")
        if scf_energy is None:
            raise ValueError("get_integrals with wfn= requires scf_energy=.")
        return wfn, float(scf_energy), None

    reference = kwargs.get("reference")
    run_scf = bool(kwargs.get("run_scf", True))
    if not run_scf:
        if reference is not None:
            mf_handle = (
                reference.mf.raw_handle() if hasattr(reference.mf, "raw_handle") else reference.mf
            )
            return mf_handle, float(reference.e_tot), None
        cached = getattr(solver, "_last_molecular_mf_result", None)
        if cached is not None:
            mf_handle = cached.mf.raw_handle() if hasattr(cached.mf, "raw_handle") else cached.mf
            return mf_handle, float(cached.e_tot), cached

    mf_res = solver.run_molecular_mean_field()
    wfn_out = mf_res.mf.raw_handle() if hasattr(mf_res.mf, "raw_handle") else mf_res.mf
    return wfn_out, float(mf_res.e_tot), mf_res


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
    wfn, scf_energy, mf_res = _resolve_psi4_wavefunction(solver, kwargs)
    if mf_res is not None:
        solver._last_molecular_mf_result = mf_res
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
        "scf_energy": float(scf_energy),
        "psi4_converged": True,
    }
