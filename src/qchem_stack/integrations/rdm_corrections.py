from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np

from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.chem.rdm_bundle import RDMBundle
from qchem_stack.integrations.rdm_corrections_types import (
    RdmCorrectionReadinessV1,
    RdmCorrectionReportV1,
    rdm_correction_readiness_v1,
    rdm_correction_report_v1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def rdm_bundle_from_mean_field(reference: ClassicalMeanFieldReference) -> RDMBundle:
    """Construct a minimal :class:`RDMBundle` from a unified mean-field reference."""
    tag = reference.backend_tag()
    ao = reference.ao_basis_view()
    dm1 = ao.make_rdm1_ao()
    spin_model = "restricted" if str(reference.mf.__class__.__name__) != "UHF" else "unrestricted"
    if tag == "pyscf":
        dm = reference.mf.make_rdm1()  # type: ignore[union-attr]
        if isinstance(dm, (tuple, list)):
            dm1 = np.asarray(dm[0], dtype=float) + np.asarray(dm[1], dtype=float)
            spin_model = "unrestricted"
    rdm_basis = f"spatial_ao_{tag}" if tag else "spatial_ao_unknown"
    rdm_source = f"{tag}_scf_rdm1" if tag else "scf_rdm1"
    return RDMBundle(
        rdm1_spatial=dm1,
        rdm_basis=rdm_basis,
        rdm_source=rdm_source,
        spin_model=spin_model,
        metadata={
            "n_spatial_orbitals": int(dm1.shape[0]),
            "upstream_classical_software_tag": tag,
        },
    )


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


def _mrpt_nevpt2_on_mean_field(
    mf: Any,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> float:
    from pyscf import mcscf, mrpt

    mc = mcscf.CASCI(mf, int(n_active_orbitals), int(n_active_electrons))
    mc.kernel()  # type: ignore[union-attr]
    return float(mrpt.NEVPT(mc).kernel())


def run_nevpt2_casci_correction(
    rhf: ClassicalMeanFieldReference,
    n_active_orbitals: int,
    n_active_electrons: int,
    *,
    cfg: ExperimentConfig,
) -> RdmCorrectionReportV1:
    """NEVPT2 on CASCI reference; PySCF ``mrpt.NEVPT`` (native or shadow-imported MO)."""
    tag = rhf.backend_tag()
    if tag == "pyscf":
        return run_pyscf_nevpt2_casci_correction(rhf, n_active_orbitals, n_active_electrons)
    if tag == "psi4":
        return run_psi4_nevpt2_casci_correction(rhf, n_active_orbitals, n_active_electrons, cfg=cfg)
    return rdm_correction_report_v1(
        method="nevpt2_casci",
        status="failed",
        energy_correction_au=None,
        reference_wavefunction="casci",
        kernel_class="nevpt2_casci",
        nevpt2={"status": "failed", "reason": f"backend_not_supported:{tag}"},
        note=f"nevpt2_casci unsupported for backend {tag!r}.",
    )


def run_psi4_nevpt2_casci_correction(
    rhf: ClassicalMeanFieldReference,
    n_active_orbitals: int,
    n_active_electrons: int,
    *,
    cfg: ExperimentConfig,
) -> RdmCorrectionReportV1:
    """Strongly-contracted NEVPT2 via PySCF ``mrpt.NEVPT`` on MO imported from Psi4."""
    if rhf.backend_tag() != "psi4":
        return _nevpt2_failed_report(
            method="psi4_nevpt2_casci",
            backend_key="psi4_nevpt2",
            reason="backend_not_psi4",
        )
    try:
        mf = build_pyscf_rhf_shadow(cfg, rhf, run_scf_if_needed=False)
        e_nevpt = _mrpt_nevpt2_on_mean_field(mf, n_active_orbitals, n_active_electrons)
        nevpt2 = {
            "status": "ok",
            "pyscf_entrypoint": "mrpt.NEVPT(CASCI(...))",
            "implementation_id": "pyscf_mrpt_on_psi4_imported_mo_v1",
        }
        return rdm_correction_report_v1(
            method="psi4_nevpt2_casci",
            status="ok",
            energy_correction_au=e_nevpt,
            reference_wavefunction="casci",
            kernel_class="pyscf_mrpt_nevpt2",
            nevpt2=dict(nevpt2),
            psi4_nevpt2=dict(nevpt2),
            note=(
                "PySCF mrpt.NEVPT on CASCI built from Psi4-imported MO coefficients; "
                "same PT kernel as pyscf_nevpt2_casci — orbital/integral reference differs."
            ),
        )
    except Exception as e:  # noqa: BLE001
        return _nevpt2_failed_report(
            method="psi4_nevpt2_casci",
            backend_key="psi4_nevpt2",
            reason=str(e),
        )


def run_pyscf_nevpt2_casci_correction(
    rhf: ClassicalMeanFieldReference,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> RdmCorrectionReportV1:
    """
    Strongly-contracted NEVPT2 correlation energy from PySCF ``mrpt.NEVPT`` on a **CASCI** reference.
    """
    ref = rhf
    if ref.backend_tag() != "pyscf":
        return _nevpt2_failed_report(
            method="pyscf_nevpt2_casci",
            backend_key="pyscf_nevpt2",
            reason=f"backend_not_supported:{ref.backend_tag()}",
        )
    mf = ref.mf
    if hasattr(mf, "raw_handle"):
        mf = mf.raw_handle()
    try:
        e_nevpt = _mrpt_nevpt2_on_mean_field(mf, n_active_orbitals, n_active_electrons)
        nevpt2 = {
            "status": "ok",
            "pyscf_entrypoint": "mrpt.NEVPT(CASCI(...))",
            "implementation_id": "pyscf_mrpt_on_native_mf_v1",
        }
        return rdm_correction_report_v1(
            method="pyscf_nevpt2_casci",
            status="ok",
            energy_correction_au=e_nevpt,
            reference_wavefunction="casci",
            kernel_class="pyscf_mrpt_nevpt2",
            nevpt2=dict(nevpt2),
            pyscf_nevpt2=dict(nevpt2),
            note=(
                "PySCF mrpt.NEVPT correlation increment relative to the CASCI reference; "
                "open-stack hook — not vendor-binary equivalent."
            ),
        )
    except Exception as e:  # noqa: BLE001
        return _nevpt2_failed_report(
            method="pyscf_nevpt2_casci",
            backend_key="pyscf_nevpt2",
            reason=str(e),
        )


def _nevpt2_failed_report(
    *,
    method: str,
    backend_key: str,
    reason: str,
) -> RdmCorrectionReportV1:
    block = {"status": "failed", "reason": reason}
    out = rdm_correction_report_v1(
        method=method,
        status="failed",
        energy_correction_au=None,
        reference_wavefunction="casci",
        kernel_class="pyscf_mrpt_nevpt2",
        nevpt2=dict(block),
        note=f"NEVPT2 failed; inspect {backend_key}.reason.",
    )
    out[backend_key] = dict(block)  # type: ignore[literal-required]
    return out


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
