"""
Open reference **driver / solvent / PBC** surface with parity-matrix-facing labels.

Maps what this repository actually wires through PySCF — not a closed vendor driver clone.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import OPEN_DRIVER_SURFACE_V1


def open_driver_coverage_matrix() -> dict[str, Any]:
    """Machine-readable coverage for parity matrices / gap dashboards."""
    return {
        "schema": OPEN_DRIVER_SURFACE_V1,
        "stack": "qchem_stack.chem.drivers.pyscf_driver",
        "rows": [
            {
                "parity_matrix_row_label": "gas-phase RHF/UHF/ROHF",
                "status": "yes_pyscf",
                "implementation": (
                    "create_solver(cfg).compute_mean_field / "
                    "classical_mean_field_reference_from_config"
                ),
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
                "parity_matrix_row_label": "AVAS active-space projection (PySCF mcscf.avas)",
                "status": "partial_pyscf",
                "implementation": (
                    "active_space.strategy=avas + chemistry_extended.avas_ao_labels; "
                    "SolverCapabilities.supports_avas_active_space_projection"
                ),
            },
            {
                "parity_matrix_row_label": "CASSCF orbital optimization audit / feed (PySCF mcscf.CASSCF)",
                "status": "partial_pyscf",
                "implementation": (
                    "chemistry_extended.casscf_orbital_optimization_audit / "
                    "casscf_orbital_optimization_for_integrals on molecular RHF"
                ),
            },
            {
                "parity_matrix_row_label": "Psi4 restricted active-space CASCI integrals → qubit Hamiltonian",
                "status": "yes_psi4",
                "implementation": (
                    "scf.driver=psi4 + CanonicalActiveSpaceIntegralPack via "
                    "chem.integrals.psi4_active_space_exporter (RHF, small active spaces)"
                ),
            },
        ],
    }
