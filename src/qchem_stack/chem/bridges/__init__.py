"""Classical QC software → qchem_stack interchange public exports.

This package uses lazy attribute loading so importing submodules like
``qchem_stack.chem.bridges.mean_field_reference`` does not eagerly import the full
bridge stack and create circular import chains during test collection.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK_SCHEMA_V1",
    "CANONICAL_CLASSICAL_BRIDGE_META_VERSION",
    "CanonicalActiveSpaceIntegralPack",
    "ClassicalMeanFieldReference",
    "ClassicalChemistrySoftwareBridge",
    "MeanFieldLike",
    "RegistryBackedClassicalBridge",
    "classical_mean_field_via_solver_bridge",
    "merge_canonical_classical_bridge_headers",
    "molecular_system_from_experiment",
    "wrap_mean_field_like",
]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK_SCHEMA_V1": (
        "qchem_stack.chem.bridges.canonical_integral_pack",
        "SCHEMA_V1",
    ),
    "CanonicalActiveSpaceIntegralPack": (
        "qchem_stack.chem.bridges.canonical_integral_pack",
        "CanonicalActiveSpaceIntegralPack",
    ),
    "RegistryBackedClassicalBridge": (
        "qchem_stack.chem.bridges.facade",
        "RegistryBackedClassicalBridge",
    ),
    "classical_mean_field_via_solver_bridge": (
        "qchem_stack.chem.bridges.facade",
        "classical_mean_field_via_solver_bridge",
    ),
    "molecular_system_from_experiment": (
        "qchem_stack.chem.bridges.facade",
        "molecular_system_from_experiment",
    ),
    "CANONICAL_CLASSICAL_BRIDGE_META_VERSION": (
        "qchem_stack.chem.bridges.interchange",
        "CANONICAL_CLASSICAL_BRIDGE_META_VERSION",
    ),
    "merge_canonical_classical_bridge_headers": (
        "qchem_stack.chem.bridges.interchange",
        "merge_canonical_classical_bridge_headers",
    ),
    "MeanFieldLike": ("qchem_stack.chem.bridges.mean_field_like", "MeanFieldLike"),
    "wrap_mean_field_like": ("qchem_stack.chem.bridges.mean_field_like", "wrap_mean_field_like"),
    "ClassicalMeanFieldReference": (
        "qchem_stack.chem.bridges.mean_field_reference",
        "ClassicalMeanFieldReference",
    ),
    "ClassicalChemistrySoftwareBridge": (
        "qchem_stack.chem.bridges.protocol",
        "ClassicalChemistrySoftwareBridge",
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
