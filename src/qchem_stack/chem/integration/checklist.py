"""Printable integration checklist for new ``scf.driver`` adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qchem_stack.chem.kernels.catalog import KERNEL_MEAN_FIELD_SCF
from qchem_stack.chem.solvers.adapter_contract import validate_solver_adapter_contract
from qchem_stack.chem.solvers.base import (
    ChemIntegralSolver,
    MolecularMeanFieldResult,
    SolverCapabilities,
)
from qchem_stack.contracts.schema_ids import INTEGRATION_CHECKLIST_REPORT_V1


@dataclass
class IntegrationChecklistReport:
    backend_id: str
    items: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ready_for_smoke(self) -> bool:
        required = [i for i in self.items if i.get("required")]
        return all(i.get("status") == "ok" for i in required)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": INTEGRATION_CHECKLIST_REPORT_V1,
            "backend_id": self.backend_id,
            "ready_for_smoke": self.ready_for_smoke,
            "items": list(self.items),
        }


def _kernel_ids(meta: dict[str, Any]) -> set[str]:
    return {
        str(row.get("kernel_id"))
        for row in (meta.get("kernel_bindings") or [])
        if isinstance(row, dict) and row.get("kernel_id")
    }


def run_integration_checklist(
    solver: ChemIntegralSolver,
    *,
    run_mean_field: bool = False,
) -> IntegrationChecklistReport:
    """Evaluate static checklist items for an adapter (optional SCF runtime)."""
    caps = solver.capabilities
    backend_id = str(caps.backend_id)
    report = IntegrationChecklistReport(backend_id=backend_id)

    def add(
        item_id: str,
        *,
        required: bool,
        status: str,
        detail: str,
    ) -> None:
        report.items.append(
            {
                "id": item_id,
                "required": required,
                "status": status,
                "detail": detail,
            }
        )

    add(
        "capabilities_type",
        required=True,
        status="ok" if isinstance(caps, SolverCapabilities) else "fail",
        detail="solver.capabilities is SolverCapabilities",
    )
    add(
        "backend_id_nonempty",
        required=True,
        status="ok" if backend_id.strip() else "fail",
        detail=f"backend_id={backend_id!r}",
    )
    add(
        "molecular_scf_or_explicit_false",
        required=True,
        status="ok"
        if caps.supports_molecular_scf
        or not caps.supports_restricted_active_space_qubit_hamiltonian
        else "warn",
        detail=(
            "supports_restricted_active_space_qubit_hamiltonian=True "
            "usually needs supports_molecular_scf=True or precomputed integrals"
        ),
    )
    contract = validate_solver_adapter_contract(
        solver, run_mean_field=False, not_implemented_is_error=False
    )
    add(
        "adapter_contract",
        required=True,
        status="ok" if contract.ok else "fail",
        detail="; ".join(contract.errors) or "protocol conformant",
    )

    mf_result: MolecularMeanFieldResult | None = None
    if run_mean_field:
        try:
            mf_result = solver.compute_mean_field(periodic=False)
        except NotImplementedError as exc:
            add(
                "mean_field_runtime",
                required=True,
                status="fail",
                detail=f"compute_mean_field NotImplementedError: {exc}",
            )
        except Exception as exc:  # noqa: BLE001
            add(
                "mean_field_runtime",
                required=True,
                status="fail",
                detail=f"compute_mean_field {type(exc).__name__}: {exc}",
            )
        else:
            add(
                "mean_field_runtime",
                required=True,
                status="ok",
                detail=f"E_tot_au={float(mf_result.e_tot):.10f}",
            )
    else:
        add(
            "mean_field_runtime",
            required=False,
            status="skip",
            detail="set run_mean_field=True to execute SCF",
        )

    if mf_result is not None:
        dm = dict(mf_result.driver_meta or {})
        kids = _kernel_ids(dm)
        add(
            "driver_meta_upstream_tag",
            required=True,
            status="ok" if dm.get("upstream_classical_software_tag") else "fail",
            detail=f"upstream_classical_software_tag={dm.get('upstream_classical_software_tag')!r}",
        )
        add(
            "driver_meta_mean_field_binding",
            required=True,
            status="ok" if KERNEL_MEAN_FIELD_SCF in kids else "fail",
            detail=f"kernel_bindings ids={sorted(kids)}",
        )
        bound = str(dm.get("epistemic_bound") or "")
        if bound:
            add(
                "driver_meta_epistemic_bound",
                required=False,
                status="warn" if backend_id == "psi4" else "info",
                detail=bound[:240] + ("…" if len(bound) > 240 else ""),
            )
    else:
        add(
            "driver_meta_upstream_tag",
            required=False,
            status="skip",
            detail="requires run_mean_field=True",
        )
        add(
            "driver_meta_mean_field_binding",
            required=False,
            status="skip",
            detail="requires run_mean_field=True",
        )

    return report
