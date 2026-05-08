from __future__ import annotations

from typing import Any, Literal

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.rdm_bundle import RDMBundle


def rdm_bundle_from_mean_field(reference: ClassicalMeanFieldReference) -> RDMBundle:
    """Construct a minimal :class:`RDMBundle` from a unified mean-field reference."""
    dm = reference.mf.make_rdm1()
    if isinstance(dm, (tuple, list)):
        dm1 = np.asarray(dm[0], dtype=float) + np.asarray(dm[1], dtype=float)
        spin_model = "unrestricted"
    else:
        dm1 = np.asarray(dm, dtype=float)
        spin_model = "restricted"
    return RDMBundle(
        rdm1_spatial=dm1,
        rdm_basis="spatial_ao_pyscf",
        rdm_source="pyscf_scf_rdm1",
        spin_model=spin_model,
        metadata={
            "n_spatial_orbitals": int(dm1.shape[0]),
            "upstream_classical_software_tag": reference.backend_tag(),
        },
    )


def run_rdm_correction(
    method: Literal["stub_nevpt2", "stub_ac0"],
    bundle: RDMBundle,
) -> dict[str, Any]:
    """
    Open-stack placeholder for RDM-driven correction workflows (Phase C stubs).

    Emits :class:`RDMBundle`-linked metadata plus **readiness** fields consumed by
    :func:`build_rdm_correction_readiness`.
    """
    if method not in ("stub_nevpt2", "stub_ac0"):
        raise ValueError(f"Unsupported stub RDM correction method: {method!r}")
    return {
        "schema": "rdm_correction_report_v1",
        "method": method,
        "status": "stub",
        "energy_correction_au": 0.0,
        "reference_wavefunction": "scf_rhf",
        "kernel_class": "placeholder_stub",
        "pyscf_nevpt2": {"status": "not_run", "reason": "stub_method"},
        "rdm_bundle_schema": str(bundle.metadata.get("schema") or "rdm_bundle_v2"),
        "rdm_basis": bundle.rdm_basis,
        "rdm_source": bundle.rdm_source,
        "spin_model": bundle.spin_model,
        "note": (
            "Open-stack placeholder only: pipeline wiring and reproducibility fields are available, "
            "but NEVPT2/AC0 numerical kernels are not implemented in this method."
        ),
    }


def run_pyscf_nevpt2_casci_correction(
    rhf: ClassicalMeanFieldReference,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> dict[str, Any]:
    """
    Strongly-contracted NEVPT2 correlation energy from PySCF ``mrpt.NEVPT`` on a **CASCI** reference.

    This is an **open-stack numerical hook** (Phase 3): not claimed equivalent to InQuanto-closed
    ``inquanto-pyscf`` kernels or AC0-style workflows.
    """
    ref = rhf
    if ref.backend_tag() != "pyscf":
        return {
            "schema": "rdm_correction_report_v1",
            "method": "pyscf_nevpt2_casci",
            "status": "failed",
            "energy_correction_au": None,
            "reference_wavefunction": "casci",
            "kernel_class": "pyscf_mrpt_nevpt2",
            "pyscf_nevpt2": {"status": "failed", "reason": f"backend_not_supported:{ref.backend_tag()}"},
            "note": "pyscf_nevpt2_casci requires upstream_classical_software_tag='pyscf'.",
        }
    mf = ref.mf
    try:
        from pyscf import mcscf, mrpt

        mc = mcscf.CASCI(mf, int(n_active_orbitals), int(n_active_electrons))
        mc.kernel()
        e_nevpt = float(mrpt.NEVPT(mc).kernel())
        return {
            "schema": "rdm_correction_report_v1",
            "method": "pyscf_nevpt2_casci",
            "status": "ok",
            "energy_correction_au": e_nevpt,
            "reference_wavefunction": "casci",
            "kernel_class": "pyscf_mrpt_nevpt2",
            "pyscf_nevpt2": {"status": "ok", "pyscf_entrypoint": "mrpt.NEVPT(CASCI(...))"},
            "note": (
                "PySCF mrpt.NEVPT correlation increment relative to the CASCI reference; "
                "open-stack hook — not InQuanto-binary equivalent."
            ),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "schema": "rdm_correction_report_v1",
            "method": "pyscf_nevpt2_casci",
            "status": "failed",
            "energy_correction_au": None,
            "reference_wavefunction": "casci",
            "kernel_class": "pyscf_mrpt_nevpt2",
            "pyscf_nevpt2": {"status": "failed", "reason": str(e)},
            "note": "PySCF mrpt.NEVPT failed; inspect pyscf_nevpt2.reason.",
        }


def build_rdm_correction_readiness(
    *,
    requested_method: str,
    correction_report: dict[str, Any],
    bundle_meta: dict[str, Any],
) -> dict[str, Any]:
    """
    Parity-oriented readiness blob (Phase 3): wires requested method, RDM source, and kernel status.

    Attached at pipeline top-level as ``rdm_correction_readiness`` and mirrored into ``run_summary``.
    """
    pn = correction_report.get("pyscf_nevpt2")
    nevpt_status = "not_applicable"
    if isinstance(pn, dict) and pn.get("status") is not None:
        nevpt_status = str(pn["status"])
    elif requested_method in ("stub_nevpt2", "stub_ac0"):
        nevpt_status = "not_run"
    return {
        "schema": "rdm_correction_readiness_v1",
        "requested_method": requested_method,
        "rdm1_source": bundle_meta.get("rdm_source") or bundle_meta.get("source"),
        "rdm_basis": bundle_meta.get("rdm_basis"),
        "spin_model": bundle_meta.get("spin_model"),
        "reference_wavefunction": str(correction_report.get("reference_wavefunction") or "scf_rhf"),
        "kernel_class": str(correction_report.get("kernel_class") or "unknown"),
        "nevpt2_pyscf_status": nevpt_status,
    }
