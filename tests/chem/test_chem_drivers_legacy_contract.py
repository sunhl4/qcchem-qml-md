"""Legacy ``drivers/`` package contract after PySCFDriver removal."""

from __future__ import annotations

import importlib


def test_drivers_package_exports_pyscf_rhf_result() -> None:
    mod = importlib.import_module("qchem_stack.chem.drivers")
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult

    assert mod.PySCFRHFResult is PySCFRHFResult


def test_drivers_all_importable() -> None:
    mod = importlib.import_module("qchem_stack.chem.drivers")
    missing: list[str] = []
    for name in mod.__all__:
        try:
            getattr(mod, name)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{name}: {exc}")
    assert not missing, "failed chem.drivers.__all__ imports:\n" + "\n".join(missing)
