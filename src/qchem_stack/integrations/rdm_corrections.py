"""RDM correction orchestration glue; numerical kernels live in ``chem.kernels.rdm_corrections``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from qchem_stack.chem.kernels.rdm_corrections import (
    rdm_bundle_from_mean_field,
    run_nevpt2_casci_correction,
    run_psi4_nevpt2_casci_correction,
    run_pyscf_nevpt2_casci_correction,
)
from qchem_stack.integrations.rdm_corrections_types import (
    RdmCorrectionReadinessV1,
    RdmCorrectionReportV1,
    rdm_correction_readiness_v1,
    rdm_correction_report_v1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.rdm_bundle import RDMBundle

__all__ = [
    "build_rdm_correction_readiness",
    "rdm_bundle_from_mean_field",
    "run_nevpt2_casci_correction",
    "run_psi4_nevpt2_casci_correction",
    "run_pyscf_nevpt2_casci_correction",
    "run_rdm_correction",
]


def run_rdm_correction(
    method: Literal["stub_nevpt2", "stub_ac0"],
    bundle: RDMBundle,
) -> RdmCorrectionReportV1:
    """
    Open-stack placeholder for RDM-driven correction workflows (Phase C stubs).

    Emits :class:`RDMBundle`-linked metadata plus **readiness** fields consumed by
    :func:`build_rdm_correction_readiness`.
    """
    if method not in ("stub_nevpt2", "stub_ac0"):
        raise ValueError(f"Unsupported stub RDM correction method: {method!r}")
    return rdm_correction_report_v1(
        method=method,
        status="stub",
        energy_correction_au=0.0,
        reference_wavefunction="scf_rhf",
        kernel_class="placeholder_stub",
        nevpt2={"status": "not_run", "reason": "stub_method"},
        pyscf_nevpt2={"status": "not_run", "reason": "stub_method"},
        rdm_bundle_schema=str(bundle.metadata.get("schema") or "rdm_bundle_v2"),
        rdm_basis=bundle.rdm_basis,
        rdm_source=bundle.rdm_source,
        spin_model=bundle.spin_model,
        note=(
            "Open-stack placeholder only: pipeline wiring and reproducibility fields are available, "
            "but NEVPT2/AC0 numerical kernels are not implemented in this method."
        ),
    )


def build_rdm_correction_readiness(
    *,
    requested_method: str,
    correction_report: RdmCorrectionReportV1 | dict[str, Any],
    bundle_meta: dict[str, Any],
) -> RdmCorrectionReadinessV1:
    """
    Parity-oriented readiness blob (Phase 3): wires requested method, RDM source, and kernel status.
    """
    report = cast("RdmCorrectionReportV1", correction_report)
    nevpt_status = _nevpt2_status_from_report(report)
    return rdm_correction_readiness_v1(
        requested_method=requested_method,
        rdm1_source=bundle_meta.get("rdm_source") or bundle_meta.get("source"),
        rdm_basis=bundle_meta.get("rdm_basis"),
        spin_model=bundle_meta.get("spin_model"),
        reference_wavefunction=str(report.get("reference_wavefunction") or "scf_rhf"),
        kernel_class=str(report.get("kernel_class") or "unknown"),
        nevpt2_status=nevpt_status,
        nevpt2_pyscf_status=nevpt_status,
    )


def _nevpt2_status_from_report(correction_report: RdmCorrectionReportV1) -> str:
    for key in ("nevpt2", "pyscf_nevpt2", "psi4_nevpt2"):
        block = correction_report.get(key)
        if isinstance(block, dict) and block.get("status") is not None:
            return str(block["status"])
    if correction_report.get("requested_method") in ("stub_nevpt2", "stub_ac0"):
        return "not_run"
    return "not_applicable"
