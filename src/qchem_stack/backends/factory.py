from __future__ import annotations

import warnings
from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from threading import RLock

from qchem_stack.backends.executor_base import (
    HamiltonianExpectationExecutor,
    StatevectorHeaExecutor,
)
from qchem_stack.backends.ionstack_executor import IonStackHeaExecutor
from qchem_stack.backends.qiskit_executor import (
    QiskitPrimitivesHeaExecutor,
    QiskitStatevectorHeaExecutor,
)
from qchem_stack.backends.spec import BackendSpec

BackendFactory = Callable[[BackendSpec], HamiltonianExpectationExecutor]
_ENTRY_POINT_GROUP = "qchem_stack.backends_executors"
_REGISTRY: dict[str, BackendRegistrationRecord] = {}
_BOOTSTRAPPED = False
_BOOTSTRAP_LOCK = RLock()


@dataclass(frozen=True)
class BackendRegistrationRecord:
    provider_id: str
    factory: BackendFactory
    source: str
    origin: str


def _normalize_provider(provider: str) -> str:
    key = str(provider).strip().lower()
    if not key:
        raise ValueError("backend provider must be non-empty.")
    if any(ch.isspace() for ch in key):
        raise ValueError(f"backend provider must not contain whitespace: {provider!r}")
    return key


def register_backend_provider(
    provider: str,
    factory: BackendFactory,
    *,
    overwrite: bool = False,
) -> None:
    key = _normalize_provider(provider)
    if not callable(factory):
        raise ValueError(f"backend provider {provider!r} factory must be callable.")
    with _BOOTSTRAP_LOCK:
        current = _REGISTRY.get(key)
        if current is not None and current.factory is factory:
            return
        if current is not None and not overwrite:
            raise ValueError(
                f"backend provider {provider!r} already registered from {current.source} "
                f"({current.origin}); set overwrite=True to replace it."
            )
        _REGISTRY[key] = BackendRegistrationRecord(
            provider_id=key,
            factory=factory,
            source="runtime",
            origin=f"{getattr(factory, '__module__', '?')}.{getattr(factory, '__name__', 'factory')}",
        )


def registered_backend_provider_ids() -> frozenset[str]:
    _ensure_bootstrap()
    return frozenset(_REGISTRY.keys())


def _register_record(
    provider: str,
    factory: BackendFactory,
    *,
    source: str,
    origin: str,
) -> None:
    _REGISTRY[provider] = BackendRegistrationRecord(
        provider_id=provider,
        factory=factory,
        source=source,
        origin=origin,
    )


def _statevector_factory(_: BackendSpec) -> HamiltonianExpectationExecutor:
    return StatevectorHeaExecutor()


def _qiskit_factory(spec: BackendSpec) -> HamiltonianExpectationExecutor:
    mode = (spec.qiskit_mode or "statevector").lower()
    if mode == "estimator":
        return QiskitPrimitivesHeaExecutor(spec)
    try:
        import qiskit  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "provider='qiskit' requires qiskit. Install: pip install qchem-stack[quantum]"
        ) from e
    return QiskitStatevectorHeaExecutor(spec)


def _ionstack_factory(spec: BackendSpec) -> HamiltonianExpectationExecutor:
    return IonStackHeaExecutor(spec)


def _resolve_entry_point_factory(value: object, *, source: str) -> BackendFactory:
    if callable(value):
        return value  # type: ignore[return-value]
    ctor = getattr(value, "from_backend_spec", None)
    if callable(ctor):
        return ctor  # type: ignore[return-value]
    raise ValueError(
        f"{source} must resolve to a callable factory or class exposing from_backend_spec(spec)."
    )


def _iter_backend_entry_points() -> list[EntryPoint]:
    eps = entry_points()
    if hasattr(eps, "select"):
        selected = list(eps.select(group=_ENTRY_POINT_GROUP))
    else:
        selected = list(eps.get(_ENTRY_POINT_GROUP, []))  # type: ignore[attr-defined]
    return sorted(selected, key=lambda ep: (ep.name.strip().lower(), ep.value))


def _register_builtin_backends() -> None:
    _register_record(
        "statevector", _statevector_factory, source="builtin", origin="statevector_factory"
    )
    _register_record("numpy", _statevector_factory, source="builtin", origin="statevector_factory")
    _register_record("local", _statevector_factory, source="builtin", origin="statevector_factory")
    _register_record("qiskit", _qiskit_factory, source="builtin", origin="qiskit_factory")
    _register_record("ionstack", _ionstack_factory, source="builtin", origin="ionstack_factory")
    _register_record("ion_stack", _ionstack_factory, source="builtin", origin="ionstack_factory")


def _discover_external_backends() -> None:
    for ep in _iter_backend_entry_points():
        try:
            key = _normalize_provider(ep.name)
            if key in _REGISTRY:
                warnings.warn(
                    f"Skipping backend entry point {ep.value!r}: provider {key!r} already registered.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue
            factory = _resolve_entry_point_factory(ep.load(), source=f"entry point {ep.value!r}")
            _register_record(key, factory, source="entrypoint", origin=ep.value)
        except Exception as exc:  # pragma: no cover - warning side effect only
            warnings.warn(
                f"Skipping backend entry point {ep.value!r}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )


def _ensure_bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    with _BOOTSTRAP_LOCK:
        if _BOOTSTRAPPED:
            return
        _register_builtin_backends()
        _discover_external_backends()
        _BOOTSTRAPPED = True


def executor_from_spec(spec: BackendSpec) -> HamiltonianExpectationExecutor:
    """Select simulator / device API from ``BackendSpec``."""
    _ensure_bootstrap()
    provider = _normalize_provider(spec.provider)
    rec = _REGISTRY.get(provider)
    if rec is None:
        raise ValueError(
            f"Unknown backend provider: {spec.provider!r}. "
            f"Registered providers: {sorted(_REGISTRY)}."
        )
    return rec.factory(spec)
