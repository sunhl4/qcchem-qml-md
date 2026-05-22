"""``chem.bridges`` lazy export contract."""

from __future__ import annotations

import importlib
import sys


def _pop_bridge_modules() -> dict[str, object]:
    prefix = "qchem_stack.chem.bridges"
    removed: dict[str, object] = {}
    for key in list(sys.modules):
        if key == prefix or key.startswith(f"{prefix}."):
            removed[key] = sys.modules.pop(key)
    return removed


def test_bridges_package_does_not_eagerly_import_reference_factory() -> None:
    ref_key = "qchem_stack.chem.bridges.reference_factory"
    removed = _pop_bridge_modules()
    try:
        mod = importlib.import_module("qchem_stack.chem.bridges")
        assert ref_key not in sys.modules
        assert "classical_mean_field_reference_from_config" not in mod.__dict__
        _ = mod.fork_driver_meta
        assert ref_key not in sys.modules
        _ = mod.classical_mean_field_reference_from_config
        assert ref_key in sys.modules
    finally:
        for key in list(sys.modules):
            if (
                key == "qchem_stack.chem.bridges" or key.startswith("qchem_stack.chem.bridges.")
            ) and key not in removed:
                del sys.modules[key]
        sys.modules.update(removed)
