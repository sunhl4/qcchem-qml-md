"""Pluggable classical solver registry for ``scf.driver``.

Built-ins (`pyscf`/`psi4`) are just registry entries. Downstream orchestration
must resolve backends through :func:`create_solver`, not direct imports.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from importlib.metadata import EntryPoint
from threading import RLock
from types import MappingProxyType
from typing import Literal, cast

from qchem_stack._entry_points import iter_entry_points
from qchem_stack.chem.solvers.base import ChemIntegralSolver, SolverCapabilities
from qchem_stack.config import ExperimentConfig

SolverFactory = Callable[[ExperimentConfig], ChemIntegralSolver]
SolverSource = Literal["builtin", "entrypoint", "runtime"]

ENTRYPOINT_CONFLICT_WARN: Literal["warn"] = "warn"
ENTRYPOINT_CONFLICT_STRICT: Literal["strict"] = "strict"
EntrypointConflictPolicy = Literal["warn", "strict"]


@dataclass(frozen=True)
class SolverRegistrationInfo:
    """Public immutable metadata for a registered solver backend."""

    solver_id: str
    source: SolverSource
    provider: str
    capability_notes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class _SolverRecord:
    factory: SolverFactory
    source: SolverSource
    provider: str


_REGISTRY: dict[str, _SolverRecord] = {}
_BOOTSTRAPPED = False
_BOOTSTRAP_LOCK = RLock()
_ENTRY_POINT_GROUP = "qchem_stack.chem_solvers"
_ENTRYPOINT_CONFLICT_POLICY: EntrypointConflictPolicy = ENTRYPOINT_CONFLICT_WARN


class SolverRegistrationError(ValueError):
    """Raised when a backend registration request is invalid."""


class InvalidSolverIdError(SolverRegistrationError):
    """Raised when a solver id is empty or malformed."""


class UnknownSolverError(ValueError):
    """Raised when ``scf.driver`` cannot be resolved to a registered solver."""


def _factory_provider(factory: SolverFactory) -> str:
    module = getattr(factory, "__module__", "unknown")
    qualname = getattr(factory, "__qualname__", getattr(factory, "__name__", "factory"))
    return f"{module}.{qualname}"


def _normalize_solver_id(name: str) -> str:
    key = name.strip().lower()
    if not key:
        raise InvalidSolverIdError("solver id must be non-empty")
    if any(ch.isspace() for ch in key):
        raise InvalidSolverIdError(f"solver id must not contain whitespace: {name!r}")
    return key


def _register_solver_record(
    solver_id: str,
    factory: SolverFactory,
    *,
    source: SolverSource,
    provider: str,
    overwrite: bool,
) -> None:
    if not callable(factory):
        raise SolverRegistrationError(f"solver {solver_id!r} factory must be callable.")
    current = _REGISTRY.get(solver_id)
    if current is not None and current.factory is factory:
        return
    if current is not None and not overwrite:
        raise SolverRegistrationError(
            f"solver {solver_id!r} already registered from {current.source} ({current.provider}); "
            f"new registration from {source} ({provider}) requires overwrite=True."
        )
    _REGISTRY[solver_id] = _SolverRecord(factory=factory, source=source, provider=provider)


def register_solver(name: str, factory: SolverFactory, *, overwrite: bool = False) -> None:
    """Register a runtime backend factory under a normalized solver id.

    Parameters
    ----------
    name:
        Backend id mapped from ``scf.driver``.
    factory:
        Callable that builds a :class:`ChemIntegralSolver` from :class:`ExperimentConfig`.
    overwrite:
        When ``True``, replace an existing registration under the same id.
    """
    solver_id = _normalize_solver_id(name)
    with _BOOTSTRAP_LOCK:
        _register_solver_record(
            solver_id,
            factory,
            source="runtime",
            provider=_factory_provider(factory),
            overwrite=overwrite,
        )


def registered_solver_ids() -> frozenset[str]:
    _ensure_bootstrap()
    return frozenset(_REGISTRY.keys())


def registered_solvers_detail() -> Mapping[str, SolverRegistrationInfo]:
    """Return per-backend metadata useful for debugging plugin discovery."""
    _ensure_bootstrap()
    with _BOOTSTRAP_LOCK:
        details: dict[str, SolverRegistrationInfo] = {}
        for solver_id, record in sorted(_REGISTRY.items()):
            details[solver_id] = SolverRegistrationInfo(
                solver_id=solver_id,
                source=record.source,
                provider=record.provider,
                capability_notes=_production_capability_notes_for_builtin(solver_id),
            )
    return MappingProxyType(details)


def _production_capability_notes_for_builtin(solver_id: str) -> dict[str, str]:
    """Static capability_notes for built-in production presets (no ExperimentConfig required)."""
    from qchem_stack.chem.integration.presets import (
        capabilities_precomputed_offline,
        capabilities_psi4_production,
        capabilities_pyscf_production,
    )

    factories = {
        "pyscf": capabilities_pyscf_production,
        "psi4": capabilities_psi4_production,
        "precomputed": capabilities_precomputed_offline,
    }
    factory = factories.get(solver_id)
    if factory is None:
        return {}
    return dict(factory().capability_notes)


def static_solver_capabilities_for_driver(driver: str) -> SolverCapabilities | None:
    """Return static capability preset for built-in drivers; ``None`` for plugin-only ids."""
    _ensure_bootstrap()
    from qchem_stack.chem.integration.presets import (
        capabilities_precomputed_offline,
        capabilities_psi4_production,
        capabilities_pyscf_production,
    )

    key = _normalize_solver_id(driver)
    factories: dict[str, Callable[[], SolverCapabilities]] = {
        "pyscf": capabilities_pyscf_production,
        "psi4": capabilities_psi4_production,
        "precomputed": capabilities_precomputed_offline,
    }
    factory = factories.get(key)
    if factory is None:
        return None
    return factory()


def solver_capability_notes_for_config(cfg: ExperimentConfig) -> dict[str, str]:
    """Return ``capability_notes`` for the solver selected by ``cfg.scf.driver``."""
    caps = create_solver(cfg).capabilities
    return dict(caps.capability_notes)


def set_entrypoint_conflict_policy(policy: EntrypointConflictPolicy) -> None:
    """Configure how entry-point id collisions are handled."""
    global _ENTRYPOINT_CONFLICT_POLICY
    with _BOOTSTRAP_LOCK:
        if policy not in (ENTRYPOINT_CONFLICT_WARN, ENTRYPOINT_CONFLICT_STRICT):
            from qchem_stack.exceptions import ConfigurationError

            raise ConfigurationError(
                f"Unknown entrypoint conflict policy {policy!r}; expected 'warn' or 'strict'."
            )
        _ENTRYPOINT_CONFLICT_POLICY = policy


def _resolve_entry_point_factory(value: object, *, source: str) -> SolverFactory:
    if callable(value):
        return cast("SolverFactory", value)
    maybe_ctor = getattr(value, "from_experiment_config", None)
    if callable(maybe_ctor):
        return cast("SolverFactory", maybe_ctor)
    raise SolverRegistrationError(
        f"{source} must resolve to a callable factory or class exposing from_experiment_config(cfg)."
    )


def _iter_solver_entry_points() -> list[EntryPoint]:
    return iter_entry_points(_ENTRY_POINT_GROUP)


def _discover_external_solvers() -> None:
    for ep in _iter_solver_entry_points():
        try:
            factory = _resolve_entry_point_factory(ep.load(), source=f"entry point {ep.value!r}")
            _register_solver_record(
                _normalize_solver_id(ep.name),
                factory,
                source="entrypoint",
                provider=ep.value,
                overwrite=False,
            )
        except SolverRegistrationError as exc:
            if _ENTRYPOINT_CONFLICT_POLICY == ENTRYPOINT_CONFLICT_STRICT:
                raise
            warnings.warn(
                f"Skipping solver entry point {ep.value!r}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
        except Exception as exc:  # pragma: no cover - warning side effect only
            warnings.warn(
                f"Skipping solver entry point {ep.value!r}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )


def _register_builtin_solvers() -> None:
    """Load built-in adapters that ship with qchem_stack."""
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver

    if "pyscf" not in _REGISTRY:
        _register_solver_record(
            "pyscf",
            PySCFIntegralSolver.from_experiment_config,
            source="builtin",
            provider=(
                "qchem_stack.chem.solvers.pyscf_solver:PySCFIntegralSolver.from_experiment_config"
            ),
            overwrite=False,
        )
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver

    if "psi4" not in _REGISTRY:
        _register_solver_record(
            "psi4",
            Psi4IntegralSolver.from_experiment_config,
            source="builtin",
            provider=(
                "qchem_stack.chem.solvers.psi4_solver:Psi4IntegralSolver.from_experiment_config"
            ),
            overwrite=False,
        )
    from qchem_stack.chem.solvers.precomputed_solver import PrecomputedIntegralSolver

    if "precomputed" not in _REGISTRY:
        _register_solver_record(
            "precomputed",
            PrecomputedIntegralSolver.from_experiment_config,
            source="builtin",
            provider=(
                "qchem_stack.chem.solvers.precomputed_solver:"
                "PrecomputedIntegralSolver.from_experiment_config"
            ),
            overwrite=False,
        )
    from qchem_stack.chem.solvers.custom_solver_template import (
        CustomExternalIntegralSolver,
    )

    if "custom_external_template" not in _REGISTRY:
        _register_solver_record(
            "custom_external_template",
            CustomExternalIntegralSolver.from_experiment_config,
            source="builtin",
            provider=(
                "qchem_stack.chem.solvers.custom_solver_template:"
                "CustomExternalIntegralSolver.from_experiment_config"
            ),
            overwrite=False,
        )


def _ensure_bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    with _BOOTSTRAP_LOCK:
        if _BOOTSTRAPPED:
            return
        _register_builtin_solvers()
        _discover_external_solvers()
        _BOOTSTRAPPED = True


def create_solver(cfg: ExperimentConfig) -> ChemIntegralSolver:
    """Instantiate backend from ``scf.driver``."""
    _ensure_bootstrap()
    key = _normalize_solver_id(cfg.scf.driver)
    record = _REGISTRY.get(key)
    if record is None:
        raise UnknownSolverError(
            "Unknown scf.driver="
            f"{cfg.scf.driver!r}. Registered: {sorted(_REGISTRY)}. "
            f"Install/register a backend plugin (entry point group: {_ENTRY_POINT_GROUP!r})."
        )
    return record.factory(cfg)
