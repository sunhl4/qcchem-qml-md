"""Machine-readable mean-field energy decomposition (open-stack ledger stub).

See ``energy_components_v1`` attached by :mod:`qchem_stack.orchestration.pipeline`
after SCF. This is **not** a full QM/MM or fragment double-counting auditor; it provides
explicit nuclei vs mean-field totals to reduce accidental double counting in downstream
reports (see technical analysis §5.5).
"""

from __future__ import annotations

from typing import Any


def build_energy_components_v1(
    *,
    nuclear_repulsion_au: float | None,
    mean_field_total_au: float,
    solvent_model: str,
    solvent_dielectric: float | None,
    energy_accounting_model: str,
) -> dict[str, Any]:
    """Return ``energy_components_v1`` blob for ``run_summary`` / export mirrors."""
    return {
        "schema": "energy_components_v1",
        "nuclear_repulsion_au": float(nuclear_repulsion_au)
        if nuclear_repulsion_au is not None
        else None,
        "mean_field_total_au": float(mean_field_total_au),
        "solvent_model": str(solvent_model),
        "solvent_dielectric": float(solvent_dielectric) if solvent_dielectric is not None else None,
        "embedding_correction_au": None,
        "post_hf_correction_au": None,
        "double_counting_guard": "do_not_add_nuclear_twice_on_top_of_mean_field_total",
        "energy_accounting_model": str(energy_accounting_model),
        "note": (
            "Open-stack partial ledger: QM/MM fragment/MM Coulomb splits and ddCOSMO energy splits "
            "are not fully itemized here; extend schema before product-scale solvent/MM claims."
        ),
    }
