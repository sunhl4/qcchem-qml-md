"""Typed shapes for RDM correction reports (integrations layer)."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class RdmCorrectionKernelStatus(TypedDict, total=False):
    status: str
    reason: NotRequired[str]
    pyscf_entrypoint: NotRequired[str]
    implementation_id: NotRequired[str]


class RdmCorrectionReportV1(TypedDict, total=False):
    schema: str
    method: str
    status: str
    energy_correction_au: float | None
    reference_wavefunction: str
    kernel_class: str
    nevpt2: RdmCorrectionKernelStatus
    pyscf_nevpt2: RdmCorrectionKernelStatus
    psi4_nevpt2: RdmCorrectionKernelStatus
    rdm_bundle_schema: str
    rdm_basis: str
    rdm_source: str
    spin_model: str
    note: str


class RdmCorrectionReadinessV1(TypedDict, total=False):
    schema: str
    requested_method: str
    rdm1_source: str | None
    rdm_basis: str | None
    spin_model: str | None
    reference_wavefunction: str
    kernel_class: str
    nevpt2_status: str
    nevpt2_pyscf_status: str


def rdm_correction_report_v1(**fields: Any) -> RdmCorrectionReportV1:
    """Build a report dict with canonical schema id (caller supplies method/status fields)."""
    from qchem_stack.contracts.schema_ids import RDM_CORRECTION_REPORT_V1

    out: RdmCorrectionReportV1 = {"schema": RDM_CORRECTION_REPORT_V1}
    out.update(fields)  # type: ignore[typeddict-item]
    return out


def rdm_correction_readiness_v1(**fields: Any) -> RdmCorrectionReadinessV1:
    from qchem_stack.contracts.schema_ids import RDM_CORRECTION_READINESS_V1

    out: RdmCorrectionReadinessV1 = {"schema": RDM_CORRECTION_READINESS_V1}
    out.update(fields)  # type: ignore[typeddict-item]
    return out
