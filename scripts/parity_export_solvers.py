"""Register optional/template classical solvers for config-only parity export."""

from __future__ import annotations


def register_parity_export_solvers() -> None:
    """Register drivers needed by ``configs/*.yaml`` parity export (no PySCF run)."""
    from qchem_stack.chem.solvers import register_mock_external_solver
    from qchem_stack.chem.solvers.custom_solver_template import (
        register_custom_external_template_solver,
    )

    register_custom_external_template_solver(overwrite=True)
    register_mock_external_solver()
