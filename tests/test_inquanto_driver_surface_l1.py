"""L1 phase D (序 18): InQuanto driver alias table stable for parity docs."""

from __future__ import annotations

from qchem_stack.chem.inquanto_driver_surface import (
    INQUANTO_DRIVER_ALIAS_TO_CONFIG,
    PYSCF_MIN_VERSION_RECOMMENDED,
    SUPPORTED_SOLVENT_MODELS,
)
from qchem_stack.integrations.open_driver_surface import open_driver_coverage_matrix


def test_inquanto_alias_map_covers_documented_rows() -> None:
    assert "solvent_ddCOSMO" in INQUANTO_DRIVER_ALIAS_TO_CONFIG
    assert "GeometryPeriodic" in INQUANTO_DRIVER_ALIAS_TO_CONFIG
    assert "PBC" in INQUANTO_DRIVER_ALIAS_TO_CONFIG
    for k, v in INQUANTO_DRIVER_ALIAS_TO_CONFIG.items():
        assert k and v


def test_supported_solvent_models_frozen() -> None:
    assert SUPPORTED_SOLVENT_MODELS <= {"none", "ddcosmo"}


def test_pyscf_min_version_recommended_documented() -> None:
    assert PYSCF_MIN_VERSION_RECOMMENDED
    parts = PYSCF_MIN_VERSION_RECOMMENDED.split(".")
    assert len(parts) >= 1 and parts[0].isdigit()


def test_open_driver_coverage_matrix_documents_avoided_chemistry_rows() -> None:
    m = open_driver_coverage_matrix()
    rows = m.get("rows") or []
    names = {r.get("inquanto_adjacent_name", "") for r in rows if isinstance(r, dict)}
    assert "AVAS / full CASSCF product workflows (Fe4N2-style tutorials)" in names
    assert "CASSCF orbital optimization loop (InQuanto-pyscf class surface)" in names
