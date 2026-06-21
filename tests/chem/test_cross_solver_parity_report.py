"""Cross-backend HF totals (Psi4 optional via import)."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.solvers.psi4_solver import psi4_hf_total_energy_au
from qchem_stack.integrations.cross_solver_parity import build_cross_solver_parity_report


def test_psi4_energy_probe_reports_missing_optional_backend() -> None:
    _, reason = psi4_hf_total_energy_au(
        symbols=["H"],
        coords_bohr=np.zeros((1, 3)),
        charge=0,
        multiplicity=2,
        basis="sto-3g",
    )
    try:
        import psi4  # noqa: F401
    except ImportError:
        assert reason == "psi4_import_missing"


def test_cross_solver_parity_report_structure() -> None:
    rep = build_cross_solver_parity_report(atol=1e-2)
    assert rep.get("schema") == "cross_solver_hf_parity_v1"
    summary = rep["summary"]
    assert summary["n_cases"] == len(rep["cases"])
    for row in rep["cases"]:
        assert isinstance(row["pyscf_hf_total_au"], float)
        assert np.isfinite(row["pyscf_hf_total_au"])
