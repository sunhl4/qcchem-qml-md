# pyright: reportUnsupportedDunderAll=false
"""Active-space integral extraction and export (PySCF/Psi4 submodules; lazy registry exports)."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from qchem_stack.chem.integrals.pyscf_active_space import (
    active_space_casci_raw_blocks,
    active_space_integrals,
)
from qchem_stack.chem.integrals.pyscf_lowdin import build_lowdin_system_from_rhf
from qchem_stack.chem.integrals.pyscf_onebody import (
    one_electron_operator_fermion_from_rhf,
    one_electron_operator_pauli_from_rhf,
)

__all__ = [
    "ActiveSpaceIntegralExporter",
    "active_space_casci_raw_blocks",
    "active_space_integrals",
    "build_lowdin_system_from_rhf",
    "get_active_space_integral_exporter",
    "list_active_space_integral_exporters",
    "one_electron_operator_fermion_from_rhf",
    "one_electron_operator_pauli_from_rhf",
    "register_active_space_integral_exporter",
]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "ActiveSpaceIntegralExporter": (
        "qchem_stack.chem.integrals.exporter_protocol",
        "ActiveSpaceIntegralExporter",
    ),
    "get_active_space_integral_exporter": (
        "qchem_stack.chem.integrals.exporter_registry",
        "get_active_space_integral_exporter",
    ),
    "list_active_space_integral_exporters": (
        "qchem_stack.chem.integrals.exporter_registry",
        "list_active_space_integral_exporters",
    ),
    "register_active_space_integral_exporter": (
        "qchem_stack.chem.integrals.exporter_registry",
        "register_active_space_integral_exporter",
    ),
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
