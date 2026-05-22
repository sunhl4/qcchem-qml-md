# pyright: reportUnsupportedDunderAll=false
"""L3 shared algorithm kernels (may delegate to PySCF, Psi4 Mints, OpenFermion, …).

See ``docs/execution/multi_backend_integration_philosophy.md`` for the three-layer model.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from qchem_stack.chem.kernels.catalog import (
    KERNEL_AVAS_PROJECTION,
    KERNEL_CASCI_ACTIVE_INTEGRALS,
    KERNEL_MEAN_FIELD_SCF,
    KERNEL_NEVPT2_CASCI,
    KERNEL_QUBIT_FERMION_MAP,
    KernelBinding,
    kernel_binding,
    list_known_kernels,
)

__all__ = [
    "KERNEL_CASCI_ACTIVE_INTEGRALS",
    "KERNEL_AVAS_PROJECTION",
    "KERNEL_MEAN_FIELD_SCF",
    "KERNEL_NEVPT2_CASCI",
    "KERNEL_QUBIT_FERMION_MAP",
    "KernelBinding",
    "build_spin_uccsd_fermion_generators",
    "count_uccsd_excitations",
    "kernel_binding",
    "list_known_kernels",
    "run_nevpt2_casci",
]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "run_nevpt2_casci": ("qchem_stack.chem.kernels.dispatch", "run_nevpt2_casci"),
    "build_spin_uccsd_fermion_generators": (
        "qchem_stack.chem.kernels.spin_ucc",
        "build_spin_uccsd_fermion_generators",
    ),
    "count_uccsd_excitations": (
        "qchem_stack.chem.kernels.spin_ucc",
        "count_uccsd_excitations",
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
