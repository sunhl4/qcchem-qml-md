"""PySCF driver result types and mean-field unwrap helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.chem.system import MolecularSystem


@dataclass
class PySCFRHFResult:
    mf: Any
    e_tot: float
    mo_energy: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
    """e.g. ``ddcosmo`` flags — parity with documented vendor PySCF *surface* (not full product parity)."""


def unwrap_pyscf_rhf_for_backend_operations(rhf: PySCFRHFResult) -> PySCFRHFResult:
    """Return a result whose ``mf`` is the raw PySCF object (not a MeanFieldLike wrapper)."""
    mf = rhf.mf
    if hasattr(mf, "raw_handle"):
        raw = mf.raw_handle()
        if raw is not mf:
            return PySCFRHFResult(
                mf=raw,
                e_tot=rhf.e_tot,
                mo_energy=rhf.mo_energy,
                molecular_system=rhf.molecular_system,
                driver_meta=fork_driver_meta(rhf.driver_meta),
            )
    return rhf
