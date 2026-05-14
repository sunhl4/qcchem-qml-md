from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any

import numpy as np

from qchem_stack.chem.solvers.base import (
    ChemIntegralSolver,
    MolecularMeanFieldResult,
    SolverCapabilities,
)


@dataclass(frozen=True)
class SolverAdapterContractReport:
    backend_id: str
    protocol_conformant: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "solver_adapter_contract_report_v1",
            "backend_id": self.backend_id,
            "ok": self.ok,
            "protocol_conformant": self.protocol_conformant,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "notes": list(self.notes),
        }


def validate_solver_adapter_contract(
    solver: Any,
    *,
    run_mean_field: bool = False,
    periodic: bool = False,
    not_implemented_is_error: bool = False,
) -> SolverAdapterContractReport:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    protocol_conformant = isinstance(solver, ChemIntegralSolver)
    if not protocol_conformant:
        errors.append(
            "solver does not conform to ChemIntegralSolver protocol; "
            "required methods/properties missing or incompatible."
        )

    caps = getattr(solver, "capabilities", None)
    if not isinstance(caps, SolverCapabilities):
        errors.append("solver.capabilities must be a SolverCapabilities instance.")
        backend_id = "unknown"
    else:
        backend_id = str(caps.backend_id).strip() or "unknown"
        if backend_id == "unknown":
            errors.append("capabilities.backend_id must be non-empty.")
        if (
            caps.supports_restricted_active_space_qubit_hamiltonian
            and not caps.supports_molecular_scf
        ):
            warnings.append(
                "supports_restricted_active_space_qubit_hamiltonian=True while supports_molecular_scf=False; "
                "ensure your adapter supplies canonical active-space integrals from an external source."
            )

    if not run_mean_field:
        notes.append("mean-field runtime check skipped (set run_mean_field=True to execute).")
        return SolverAdapterContractReport(
            backend_id=backend_id,
            protocol_conformant=protocol_conformant,
            errors=errors,
            warnings=warnings,
            notes=notes,
        )

    try:
        mf = solver.compute_mean_field(periodic=bool(periodic))
    except NotImplementedError as exc:
        msg = f"compute_mean_field raised NotImplementedError: {exc}"
        if not_implemented_is_error:
            errors.append(msg)
        else:
            warnings.append(msg)
        return SolverAdapterContractReport(
            backend_id=backend_id,
            protocol_conformant=protocol_conformant,
            errors=errors,
            warnings=warnings,
            notes=notes,
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"compute_mean_field raised {type(exc).__name__}: {exc}")
        return SolverAdapterContractReport(
            backend_id=backend_id,
            protocol_conformant=protocol_conformant,
            errors=errors,
            warnings=warnings,
            notes=notes,
        )

    if not isinstance(mf, MolecularMeanFieldResult):
        errors.append("compute_mean_field must return MolecularMeanFieldResult.")
        return SolverAdapterContractReport(
            backend_id=backend_id,
            protocol_conformant=protocol_conformant,
            errors=errors,
            warnings=warnings,
            notes=notes,
        )

    if not isfinite(float(mf.e_tot)):
        errors.append("MolecularMeanFieldResult.e_tot must be finite.")
    arr = np.asarray(mf.mo_energy)
    if arr.ndim != 1:
        errors.append("MolecularMeanFieldResult.mo_energy must be a 1D array.")
    elif arr.size < 1:
        errors.append("MolecularMeanFieldResult.mo_energy must not be empty.")
    elif not np.all(np.isfinite(arr)):
        errors.append("MolecularMeanFieldResult.mo_energy must be finite.")
    return SolverAdapterContractReport(
        backend_id=backend_id,
        protocol_conformant=protocol_conformant,
        errors=errors,
        warnings=warnings,
        notes=notes,
    )
