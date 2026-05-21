"""Optional integral cross-checks (audit only; does not replace qubit Hamiltonians)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.contracts.schema_ids import INTEGRAL_CROSSCHECK_CASCI_V1

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def run_integral_crosscheck_casci_v1(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    primary_pack: CanonicalActiveSpaceIntegralPack,
) -> dict[str, Any]:
    """Compare primary active-space integrals to a PySCF CASCI shadow (max abs element deltas)."""
    tag = reference.backend_tag()
    if tag == "pyscf":
        return {
            "schema": INTEGRAL_CROSSCHECK_CASCI_V1,
            "status": "skipped",
            "reason": "primary_backend_is_pyscf",
        }
    na = int(cfg.active_space.cas.n_orbitals)
    ne = int(cfg.active_space.cas.n_electrons)
    try:
        shadow_ref = ClassicalMeanFieldReference(
            mf=build_pyscf_rhf_shadow(cfg, reference, run_scf_if_needed=False),
            e_tot=float(reference.e_tot),
            mo_energy=np.asarray(reference.mo_energy, dtype=float),
            molecular_system=reference.molecular_system,
            driver_meta={
                "upstream_classical_software_tag": "pyscf",
                "integral_crosscheck_role": "shadow_reference",
            },
        )
        shadow_pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
            shadow_ref,
            n_active_orbitals=na,
            n_active_electrons=ne,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "schema": INTEGRAL_CROSSCHECK_CASCI_V1,
            "status": "failed",
            "reason": str(exc),
        }

    pc = primary_pack.compact
    sc = shadow_pack.compact
    h1_delta = float(np.max(np.abs(np.asarray(pc.h1_active_mo) - np.asarray(sc.h1_active_mo))))
    h2_delta = float(
        np.max(np.abs(np.asarray(pc.eri_active_mo_compact) - np.asarray(sc.eri_active_mo_compact)))
    )
    const_delta = float(abs(float(pc.constant) - float(sc.constant)))
    return {
        "schema": INTEGRAL_CROSSCHECK_CASCI_V1,
        "status": "ok",
        "primary_backend": tag,
        "shadow_backend": "pyscf",
        "max_abs_constant_delta_au": const_delta,
        "max_abs_h1_delta_au": h1_delta,
        "max_abs_h2_delta_au": h2_delta,
        "primary_storage_schema": pc.storage_schema,
        "shadow_storage_schema": sc.storage_schema,
    }


def maybe_attach_integral_crosscheck(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    primary_pack: CanonicalActiveSpaceIntegralPack | None,
) -> None:
    """Run configured cross-check and store results on ``reference.driver_meta``."""
    mode = str(cfg.chemistry_extended.post_hf.integral_crosscheck or "none")
    if mode == "none" or primary_pack is None:
        return
    if mode == "pyscf_casci":
        report = run_integral_crosscheck_casci_v1(cfg, reference, primary_pack=primary_pack)
        reference.driver_meta["integral_crosscheck_casci_v1"] = report
        return
    reference.driver_meta["integral_crosscheck_casci_v1"] = {
        "schema": INTEGRAL_CROSSCHECK_CASCI_V1,
        "status": "failed",
        "reason": f"unknown_integral_crosscheck:{mode}",
    }
