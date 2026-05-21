"""Backend-agnostic mean-field reference container used after bridge stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import (
    MeanFieldLike,
    nuclear_repulsion_energy_au,
    wrap_mean_field_like,
)

if TYPE_CHECKING:
    from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult
    from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
    from qchem_stack.chem.system import MolecularSystem


@dataclass
class ClassicalMeanFieldReference:
    """Unified post-bridge mean-field reference (independent from backend class names)."""

    mf: MeanFieldLike
    e_tot: float
    mo_energy: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mean_field_pack(
        cls,
        pack: MolecularMeanFieldResult,
        *,
        molecular_system: MolecularSystem,
    ) -> ClassicalMeanFieldReference:
        mf_like: MeanFieldLike
        if isinstance(pack.mf, MeanFieldLike):
            mf_like = pack.mf
        else:
            mf_like = wrap_mean_field_like(
                backend_tag=str(
                    (pack.driver_meta or {}).get("upstream_classical_software_tag", "")
                ),
                raw_mf=pack.mf,
                e_tot=float(pack.e_tot),
                mo_energy=np.asarray(pack.mo_energy, dtype=float),
            )
        return cls(
            mf=mf_like,
            e_tot=float(pack.e_tot),
            mo_energy=np.asarray(pack.mo_energy, dtype=float),
            molecular_system=molecular_system,
            driver_meta=dict(pack.driver_meta),
        )

    def backend_tag(self) -> str:
        raw = (self.driver_meta or {}).get("upstream_classical_software_tag")
        return str(raw).strip().lower() if raw is not None else ""

    def ao_basis_view(self) -> Any:
        from qchem_stack.chem.bridges.ao_basis_view import ao_basis_view_from_reference

        return ao_basis_view_from_reference(self)

    def as_pyscf_rhf_result(self) -> PySCFRHFResult:
        """Convert to PySCF-specific container for PySCF-only branches."""
        from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult

        mf_handle = self.mf.raw_handle() if hasattr(self.mf, "raw_handle") else self.mf
        return PySCFRHFResult(
            mf=mf_handle,
            e_tot=float(self.e_tot),
            mo_energy=np.asarray(self.mo_energy, dtype=float),
            molecular_system=self.molecular_system,
            driver_meta=dict(self.driver_meta),
        )

    def nuclear_repulsion_au(self) -> float | None:
        return nuclear_repulsion_energy_au(self.mf)
