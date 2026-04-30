"""
Open reference: **driver / solvent / PBC** surface vs InQuanto marketing names.

Maps what this repository actually calls in PySCF — not a closed-source driver clone.
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
                "inquanto_adjacent_name": "gas-phase RHF/UHF/ROHF",
                "status": "yes_pyscf",
                "implementation": "PySCFDriver.run_rhf / run_uhf / run_rohf",
            },
            {
                "inquanto_adjacent_name": "ddCOSMO / implicit solvent",
                "status": "partial_ddCOSMO",
                "implementation": "ChemistryExtendedSpec.solvent_model == ddcosmo → pyscf.solvent.ddCOSMO",
            },
            {
                "inquanto_adjacent_name": "PBC / k-point mesh",
                "status": "partial_kmesh",
                "implementation": "chemistry_extended.pbc_cell_vectors_bohr + pbc_kpoint_mesh",
            },
            {
                "inquanto_adjacent_name": "Full COSMO/PBC feature parity with InQuanto drivers",
                "status": "not_claimed",
                "note": "Use PySCF ecosystem + explicit benchmarks; no vendor binary.",
            },
        ],
    }
