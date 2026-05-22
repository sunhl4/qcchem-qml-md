"""``chem.bridges`` lazy export contract."""

from __future__ import annotations

import importlib
import sys


def test_bridges_package_does_not_eagerly_import_reference_factory() -> None:
    importlib.invalidate_caches()
    mod_key = "qchem_stack.chem.bridges.reference_factory"
    had = mod_key in sys.modules
    try:
        if mod_key in sys.modules:
            del sys.modules[mod_key]
        mod = importlib.import_module("qchem_stack.chem.bridges")
        assert mod_key not in sys.modules
        _ = mod.fork_driver_meta
        assert mod_key not in sys.modules
        _ = mod.classical_mean_field_reference_from_config
        assert mod_key in sys.modules
    finally:
        if not had and mod_key in sys.modules:
            del sys.modules[mod_key]
