"""L3 RDM extraction and NEVPT2/CASCI correction kernels (chem layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.chem.rdm_bundle import RDMBundle
from qchem_stack.contracts.schema_ids import RDM_CORRECTION_REPORT_V1

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def _rdm_correction_report_v1(**fields: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"schema": RDM_CORRECTION_REPORT_V1}
    out.update(fields)
    return out


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
) -> dict[str, Any]:
    """NEVPT2 on CASCI reference; PySCF ``mrpt.NEVPT`` (native or shadow-imported MO)."""
    tag = rhf.backend_tag()
    if tag == "pyscf":
        return run_pyscf_nevpt2_casci_correction(rhf, n_active_orbitals, n_active_electrons)
    if tag == "psi4":
        return run_psi4_nevpt2_casci_correction(rhf, n_active_orbitals, n_active_electrons, cfg=cfg)
    return _rdm_correction_report_v1(
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
) -> dict[str, Any]:
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
        return _rdm_correction_report_v1(
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
) -> dict[str, Any]:
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
        return _rdm_correction_report_v1(
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
) -> dict[str, Any]:
    block = {"status": "failed", "reason": reason}
    out = _rdm_correction_report_v1(
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
