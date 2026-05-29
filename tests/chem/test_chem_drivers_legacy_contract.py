"""Legacy ``drivers/`` package contract (deprecation + re-exports)."""

from __future__ import annotations

import importlib
import warnings

import pytest


def test_drivers_package_does_not_eagerly_import_pyscf_driver() -> None:
    import sys

    importlib.invalidate_caches()
    mod_key = "qchem_stack.chem.drivers.pyscf_driver"
    had = mod_key in sys.modules
    try:
        if mod_key in sys.modules:
            del sys.modules[mod_key]
        mod = importlib.import_module("qchem_stack.chem.drivers")
        assert mod_key not in sys.modules
        _ = mod.PySCFRHFResult
        assert mod_key not in sys.modules
    finally:
        if not had and mod_key in sys.modules:
            del sys.modules[mod_key]


def test_drivers_all_importable() -> None:
    mod = importlib.import_module("qchem_stack.chem.drivers")
    missing: list[str] = []
    for name in mod.__all__:
        try:
            getattr(mod, name)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{name}: {exc}")
    assert not missing, "failed chem.drivers.__all__ imports:\n" + "\n".join(missing)


def test_pyscf_rhf_result_reexport_matches_types_module() -> None:
    from qchem_stack.chem.drivers import PySCFRHFResult as LegacyPySCFRHFResult
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult

    assert LegacyPySCFRHFResult is PySCFRHFResult


@pytest.mark.pyscf
def test_pyscf_driver_deprecation_warning() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.drivers import PySCFDriver
    from qchem_stack.config import ExperimentConfig

    cfg = ExperimentConfig.from_yaml_dict(
        {
            "schema_version": "2",
            "experiment_id": "driver_deprecation",
            "random_seed": 1,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "embedding": {"mode": "none"},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        PySCFDriver.from_config(cfg)
    assert any(
        issubclass(w.category, DeprecationWarning) and "PySCFDriver" in str(w.message)
        for w in caught
    )


@pytest.mark.pyscf
def test_factory_path_matches_solver_path_energy() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.reference_factory import (
        classical_mean_field_reference_from_config,
    )
    from qchem_stack.chem.solvers import create_solver
    from qchem_stack.config import ExperimentConfig

    cfg = ExperimentConfig.from_yaml_dict(
        {
            "schema_version": "2",
            "experiment_id": "factory_solver_energy",
            "random_seed": 1,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "embedding": {"mode": "none"},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    ref = classical_mean_field_reference_from_config(cfg)
    solver = create_solver(cfg)
    solver.set_physical_data(cfg)
    mf = solver.compute_mean_field(periodic=False)
    assert float(ref.e_tot) == pytest.approx(float(mf.e_tot), abs=1e-10)
