"""Registry for pre-quantum branch builders keyed by :class:`PreQuantumPath`."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.exceptions import PreQuantumCapabilityError

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
    from qchem_stack.chem.pre_quantum_path import PreQuantumPath
    from qchem_stack.config import ExperimentConfig


@dataclass(frozen=True)
class PreQuantumBuildRequest:
    """Typed context passed to pre-quantum branch builders."""

    cfg: ExperimentConfig
    reference: ClassicalMeanFieldReference
    cfg_path: Path | None = None
    cache: RunBuildCache | None = None
    profile: Any | None = None
    backend_caps: Any | None = None


PreQuantumBranchBuilder = Callable[
    [PreQuantumBuildRequest],
    tuple[PreQuantumInput, dict[str, Any] | None],  # noqa: UP045
]

_BUILDERS: dict[PreQuantumPath, PreQuantumBranchBuilder] = {}
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
        raise PreQuantumCapabilityError(
            "Pre-quantum branch builder registry is frozen for this process. "
            "Register builders before calling freeze_pre_quantum_branch_builders()."
        )


def register_pre_quantum_branch_builder(
    path: PreQuantumPath,
    builder: PreQuantumBranchBuilder,
    *,
    allow_override: bool = False,
) -> None:
    """Register builder for one :class:`PreQuantumPath` branch."""
    _ensure_mutable()
    if path in _BUILDERS and not allow_override:
        raise PreQuantumCapabilityError(
            f"Pre-quantum builder for path {path.value!r} is already registered; "
            "pass allow_override=True to replace it explicitly."
        )
    _BUILDERS[path] = builder


def get_pre_quantum_branch_builder(
    path: PreQuantumPath,
) -> PreQuantumBranchBuilder:
    """Resolve builder callable for a path."""
    fn = _BUILDERS.get(path)
    if fn is None:
        known = list_pre_quantum_branch_builders()
        raise PreQuantumCapabilityError(
            f"No pre-quantum branch builder registered for path {path.value!r}. "
            f"Known paths: {known}."
        )
    return fn
