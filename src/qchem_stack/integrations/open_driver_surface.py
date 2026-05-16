"""
Open reference **driver / solvent / PBC** surface with parity-matrix-facing labels.

Maps what this repository actually wires through PySCF — not a closed vendor driver clone.
"""

from __future__ import annotations

from typing import Any


def open_driver_coverage_matrix() -> dict[str, Any]:
    """Machine-readable coverage for parity matrices / gap dashboards."""
    return {
        "schema": "open_driver_surface_v1",
        "stack": "qchem_stack.chem.drivers.pyscf_driver",
        "rows": [
            {
                "parity_matrix_row_label": "gas-phase RHF/UHF/ROHF",
                "status": "yes_pyscf",
                "implementation": "PySCFDriver.run_rhf / run_uhf / run_rohf",
            },
            {
                "parity_matrix_row_label": "ddCOSMO / implicit solvent",
                "status": "partial_ddCOSMO",
                "implementation": "ChemistryExtendedSpec.solvent_model == ddcosmo → pyscf.solvent.ddCOSMO",
            },
            {
                "parity_matrix_row_label": "PBC / k-point mesh",
                "status": "partial_kmesh",
                "implementation": (
                    "chemistry_extended.pbc_cell_vectors_bohr + pbc_kpoint_mesh; "
                    "Gamma demo YAML: configs/example_h2_pbc_gamma.yaml"
                ),
            },
            {
                "parity_matrix_row_label": "Full COSMO/PBC feature parity with closed vendor drivers",
                "status": "not_claimed",
                "note": "Use PySCF ecosystem + explicit benchmarks; no vendor binary.",
            },
            {
                "parity_matrix_row_label": "AVAS / full CASSCF product workflows (Fe4N2-style tutorials)",
                "status": "not_claimed",
                "note": "No AVAS driver; CASCI-sized active integrals only where documented (projection path).",
            },
            {
                "parity_matrix_row_label": "CASSCF orbital optimization loop (vendor PySCF extension class surface)",
                "status": "not_claimed",
                "note": "classical_reference_method and matrix rows are documentation hooks unless PySCF CASCI-only path applies.",
            },
        ],
    }
