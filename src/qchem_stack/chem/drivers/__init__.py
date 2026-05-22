# pyright: reportUnsupportedDunderAll=false
"""Legacy PySCF driver exports (deprecated).

Prefer :mod:`qchem_stack.chem.solvers`, :mod:`qchem_stack.chem.bridges.reference_factory`,
and :mod:`qchem_stack.chem.molecular_problem_build`. AO/Löwdin views:
:mod:`qchem_stack.chem.systems.pyscf_factory`.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult

__all__ = ["PySCFDriver", "PySCFRHFResult"]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "PySCFDriver": ("qchem_stack.chem.drivers.pyscf_driver", "PySCFDriver"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_ATTRS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
