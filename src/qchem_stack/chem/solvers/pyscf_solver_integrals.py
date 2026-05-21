"""Active-space integral extraction (CASCI path) for :class:`PySCFIntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.pyscf_typing import as_pyscf_cas, as_real_array, max_abs_imag
from qchem_stack.chem.solvers.pyscf_solver_mf import build_molecular_mf_without_kernel
from qchem_stack.contracts.schema_ids import PYSCF_ACTIVE_SPACE_INTEGRALS_V1

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver


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


def configure_cas_frozen_orbitals(cas: Any, frozen: Any) -> None:
    if frozen is None:
        return
    if not isinstance(frozen, (list, tuple)):
        raise TypeError("frozen_orbitals must be a list/tuple of orbital indices.")
    cas.frozen = sorted(set(int(i) for i in frozen))


def ensure_real_tensor(arr: object, *, label: str, tol: float = 1e-7) -> np.ndarray:
    if max_abs_imag(arr, tol=tol) > tol:
        raise ValueError(f"{label} have non-trivial imaginary part.")
    return as_real_array(arr)


def restore_eri_to_rank4(ao2mo_mod: Any, h2: np.ndarray, ncas: int) -> np.ndarray:
    h2a = np.asarray(h2)
    if h2a.ndim == 4:
        return h2a
    h2_restore_input = h2a
    if max_abs_imag(h2_restore_input) > 1e-7:
        raise ValueError("Active-space integrals have non-trivial imaginary part.")
    h2_restore_input = as_real_array(h2_restore_input)
    return np.asarray(ao2mo_mod.restore(1, h2_restore_input, ncas))


def get_active_space_integrals(
    solver: PySCFIntegralSolver, *args: Any, **kwargs: Any
) -> dict[str, Any]:
    from pyscf import ao2mo, mcscf

    from qchem_stack.chem.integral_convention import (
        spatial_mo_eri_pyscf_to_openfermion_mo_ordering,
    )

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
        raise RuntimeError("SCF did not converge; cannot build active-space integrals.")
    mo = np.asarray(mf.mo_coeff, dtype=float)
    cas = as_pyscf_cas(mcscf.CASCI(mf, ncas, nelecas))
    configure_cas_frozen_orbitals(cas, kwargs.get("frozen_orbitals"))
    h1, e_core = cas.get_h1eff(mo)
    h2 = cas.get_h2eff(mo)
    h1a = np.asarray(h1)
    h2a = restore_eri_to_rank4(ao2mo, np.asarray(h2), ncas)
    h1_real = ensure_real_tensor(h1a, label="Active-space one-electron integrals")
    h2_chemist = ensure_real_tensor(h2a, label="Active-space two-electron integrals")
    h2_openfermion = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_chemist)

    return {
        "schema": PYSCF_ACTIVE_SPACE_INTEGRALS_V1,
        "backend_id": "pyscf",
        "integral_representation": "mo",
        "constant": float(e_core),
        "n_active_orbitals": ncas,
        "n_active_electrons": nelecas,
        "h1_spatial_mo": h1_real,
        "h2_spatial_mo_chemist": h2_chemist,
        "h2_spatial_mo_openfermion": h2_openfermion,
        "openfermion_bridge": "pyscf_tangelo_openfermion_v1",
        "scf_energy": float(mf.e_tot),
        "pyscf_converged": bool(getattr(mf, "converged", False)),
    }
