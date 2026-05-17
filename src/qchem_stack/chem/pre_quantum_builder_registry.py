"""Registry for pre-quantum branch builders keyed by :class:`PreQuantumPath`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.pre_quantum_path import PreQuantumPath
from qchem_stack.config import ExperimentConfig

PreQuantumBranchBuilder = Callable[
    [
        ExperimentConfig,
        ClassicalMeanFieldReference,
    ],
    tuple[PreQuantumInput, dict[str, Any] | None],
]

_BUILDERS: dict[PreQuantumPath, Callable[..., tuple[PreQuantumInput, dict[str, Any] | None]]] = {}
_REGISTRY_FROZEN = False


def list_pre_quantum_branch_builders() -> tuple[str, ...]:
    """Stable list of registered pre-quantum branch ids."""
    return tuple(path.value for path in sorted(_BUILDERS, key=lambda p: p.value))


def freeze_pre_quantum_branch_builders() -> None:
    """Disallow further mutation in the current process."""
    global _REGISTRY_FROZEN
    _REGISTRY_FROZEN = True


def _ensure_mutable() -> None:
    if _REGISTRY_FROZEN:
        raise RuntimeError(
            "Pre-quantum branch builder registry is frozen for this process. "
            "Register builders before calling freeze_pre_quantum_branch_builders()."
        )


def register_pre_quantum_branch_builder(
    path: PreQuantumPath,
    builder: Callable[
        [
            ExperimentConfig,
            ClassicalMeanFieldReference,
        ],
        tuple[PreQuantumInput, dict[str, Any] | None],
    ],
    *,
    allow_override: bool = False,
) -> None:
    """Register builder for one :class:`PreQuantumPath` branch."""
    _ensure_mutable()
    if path in _BUILDERS and not allow_override:
        raise ValueError(
            f"Pre-quantum builder for path {path.value!r} is already registered; "
            "pass allow_override=True to replace it explicitly."
        )
    _BUILDERS[path] = builder


def get_pre_quantum_branch_builder(
    path: PreQuantumPath,
) -> Callable[..., tuple[PreQuantumInput, dict[str, Any] | None]]:
    """Resolve builder callable for a path."""
    fn = _BUILDERS.get(path)
    if fn is None:
        known = list_pre_quantum_branch_builders()
        raise RuntimeError(
            f"No pre-quantum branch builder registered for path {path.value!r}. "
            f"Known paths: {known}."
        )
    return fn

