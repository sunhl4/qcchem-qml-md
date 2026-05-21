"""Executable algorithm registry (YAML ``quantum.algorithm`` materialization surface).

Built-in entries are **synchronized from** :mod:`~qchem_stack.quantum.variational_plugins.registry`
so pipeline plug-ins and ``build_registered_algorithm`` stay aligned. Call
:func:`sync_algorithm_registry_from_variational` after :func:`~qchem_stack.quantum.variational_plugins.registry.register_variational_plugin`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

AlgorithmFactory = Callable[..., Any]


@dataclass(frozen=True)
class AlgorithmRegistryEntry:
    summary: str
    implementation: str
    factory: AlgorithmFactory
    capabilities: dict[str, bool] = field(default_factory=dict)
    result_schema: str = "algorithm_report_v1"


# Populated by sync_algorithm_registry_from_variational(); includes only plug-ins with factories.
ALGORITHM_REGISTRY: dict[str, AlgorithmRegistryEntry] = {}


def sync_algorithm_registry_from_variational() -> None:
    """Rebuild :data:`ALGORITHM_REGISTRY` from registered variational plug-ins (materialization path)."""

    from qchem_stack.quantum.variational_plugins.registry import (
        get_variational_plugin_record,
        list_registered_variational_ids,
    )

    ALGORITHM_REGISTRY.clear()
    for pid in list_registered_variational_ids():
        rec = get_variational_plugin_record(pid)
        if rec is None or rec.optional_model_factory is None:
            continue
        impl = rec.materialization_implementation or rec.implementation
        ALGORITHM_REGISTRY[pid] = AlgorithmRegistryEntry(
            summary=rec.summary,
            implementation=impl,
            factory=rec.optional_model_factory,
            capabilities=dict(rec.capabilities),
            result_schema=rec.materialization_result_schema,
        )


sync_algorithm_registry_from_variational()


def list_registered_algorithm_ids() -> tuple[str, ...]:
    return tuple(sorted(ALGORITHM_REGISTRY.keys()))


def algorithm_registry_export() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, entry in ALGORITHM_REGISTRY.items():
        out[key] = {
            "summary": entry.summary,
            "implementation": entry.implementation,
            "capabilities": dict(entry.capabilities),
            "result_schema": entry.result_schema,
        }
    return out


def build_registered_algorithm(
    algorithm_id: str, hamiltonian: QubitHamiltonian, **kwargs: Any
) -> Any:
    try:
        entry = ALGORITHM_REGISTRY[algorithm_id]
    except KeyError as exc:
        raise ValueError(f"Unknown algorithm id: {algorithm_id!r}") from exc
    return entry.factory(hamiltonian, **kwargs)
