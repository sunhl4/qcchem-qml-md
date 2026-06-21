"""Canonical classical bridge interchange (solver registry → ``MolecularMeanFieldResult``)."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges import (
    classical_mean_field_via_solver_bridge,
    merge_canonical_classical_bridge_headers,
    molecular_system_from_experiment,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference


def test_merge_canonical_headers_updates_forwarding_fields() -> None:
    base = {"driver_family": "pyscf"}
    m1 = merge_canonical_classical_bridge_headers(
        base, upstream_software_tag="pyscf", periodic_boundary_condition=False
    )
    m2 = merge_canonical_classical_bridge_headers(
        m1, upstream_software_tag="psi4", periodic_boundary_condition=True
    )
    assert m1["canonical_classical_bridge_schema"] == "qchem_classical_mean_field_bridge_v1"
    assert m2["upstream_classical_software_tag"] == "psi4"
    assert m2["classical_problem_periodic_boundary_condition"] is True
    assert m1["driver_family"] == "pyscf"


def test_facade_example_h2() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    mf = classical_mean_field_via_solver_bridge(cfg)
    md = mf.driver_meta
    assert md["canonical_classical_bridge_schema"] == "qchem_classical_mean_field_bridge_v1"
    assert md["upstream_classical_software_tag"] == "pyscf"
    assert md["canonical_classical_stage"] == "mean_field_completed"
    assert hasattr(mf.mf, "total_energy_au")
    assert float(mf.mf.total_energy_au()) == pytest.approx(float(mf.e_tot))


def test_pipeline_run_scf_includes_bridge_headers() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = run_scf_reference(cfg)
    md = rhf.driver_meta
    assert md["canonical_classical_bridge_schema"] == "qchem_classical_mean_field_bridge_v1"
    assert md["upstream_classical_software_tag"] == "pyscf"


def test_molecular_system_geometry_source_cartesian() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    ms = molecular_system_from_experiment(cfg)
    assert ms.meta.get("geometry_source") == "cartesian"


def test_molecular_system_geometry_source_zmatrix() -> None:
    cfg = load_experiment_config(configs_path("example_h2_zmatrix_sto3g.yaml"))
    ms = molecular_system_from_experiment(cfg)
    assert ms.meta.get("geometry_source") == "zmatrix"


def test_registry_bridge_satisfies_protocol() -> None:
    from qchem_stack.chem.bridges import (
        ClassicalChemistrySoftwareBridge,
        RegistryBackedClassicalBridge,
    )

    assert isinstance(RegistryBackedClassicalBridge(), ClassicalChemistrySoftwareBridge)
