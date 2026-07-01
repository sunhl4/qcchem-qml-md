"""Active-space integral extraction (CASCI path) for :class:`PySCFIntegralSolver`."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering
from qchem_stack.chem.integrals.pyscf_active_space import active_space_casci_raw_blocks
from qchem_stack.chem.solvers._active_space_common import resolve_active_space_spec
from qchem_stack.chem.solvers.pyscf_solver_mf import build_molecular_mf_without_kernel
from qchem_stack.contracts.schema_ids import (
    PYSCF_ACTIVE_SPACE_INTEGRALS_V1,
    PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver


def get_active_space_integrals(
    solver: PySCFIntegralSolver, *args: Any, **kwargs: Any
) -> dict[str, Any]:
    ncas, nelecas = resolve_active_space_spec(kwargs)
    if solver.method not in ("RHF", "ROHF"):
        raise NotImplementedError(
            f"get_integrals currently supports RHF/ROHF only (got method={solver.method!r})."
        )

    run_scf = bool(kwargs.get("run_scf", True))
    mf = build_molecular_mf_without_kernel(solver)
    if run_scf:
        mf.kernel()
    if not getattr(mf, "converged", False):
        from qchem_stack.exceptions import SolverError

        raise SolverError("SCF did not converge; cannot build active-space integrals.")

    driver_meta: dict[str, Any] = {}
    frozen = kwargs.get("frozen_orbitals")
    if frozen is not None:
        if not isinstance(frozen, (list, tuple)):
            raise TypeError("frozen_orbitals must be a list/tuple of orbital indices.")
        driver_meta["active_space_frozen_orbitals"] = sorted(set(int(i) for i in frozen))

    ref = SimpleNamespace(mf=mf, driver_meta=driver_meta)
    constant, h1_real, h2_chemist = active_space_casci_raw_blocks(ref, ncas, nelecas)
    h2_openfermion = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(
        np.asarray(h2_chemist, dtype=float)
    )

    return {
        "schema": PYSCF_ACTIVE_SPACE_INTEGRALS_V1,
        "backend_id": "pyscf",
        "integral_representation": "mo",
        "constant": float(constant),
        "n_active_orbitals": ncas,
        "n_active_electrons": nelecas,
        "h1_spatial_mo": np.asarray(h1_real, dtype=float),
        "h2_spatial_mo_chemist": np.asarray(h2_chemist, dtype=float),
        "h2_spatial_mo_openfermion": h2_openfermion,
        "openfermion_bridge": PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1,
        "scf_energy": float(mf.e_tot),
        "pyscf_converged": bool(getattr(mf, "converged", False)),
    }
