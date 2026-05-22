"""Load user-provided factories from ``module:attr`` (YAML ``quantum.algorithm_factory``)."""

from __future__ import annotations

import importlib
import os
from collections.abc import Callable
from typing import Any

from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)

VariationalRunner = Callable[[VariationalRunContext], VariationalStageOutcome]

_FACTORY_ALLOW_EXTERNAL_ENV = "QCHEM_QUANTUM_ALGORITHM_FACTORY_ALLOW_EXTERNAL"


def _assert_factory_module_allowed(mod_name: str) -> None:
    if mod_name.startswith("qchem_stack."):
        return
    if os.environ.get(_FACTORY_ALLOW_EXTERNAL_ENV) == "1":
        return
    raise PipelineError(
        f"algorithm_factory module {mod_name!r} is outside the default allowlist "
        f"(must start with 'qchem_stack.'). Set {_FACTORY_ALLOW_EXTERNAL_ENV}=1 to allow external modules."
    )


def validate_factory_import_path(spec: str) -> tuple[str, str]:
    raw = spec.strip()
    if ":" not in raw:
        raise ValueError(
            f"quantum.algorithm_factory must be 'module.path:callable_name', got {spec!r}"
        )
    mod_part, _, attr_part = raw.partition(":")
    mod = mod_part.strip()
    attrs = attr_part.strip()
    if not mod or not attrs:
        raise ValueError(f"Invalid algorithm_factory: {spec!r}")
    return mod, attrs


def _walk_attr(obj: Any, dotted: str) -> Any:
    cur = obj
    for token in dotted.split("."):
        if not token:
            raise ValueError(f"Invalid attribute path {dotted!r}")
        cur = getattr(cur, token)
    return cur


def load_variational_runner_from_factory(spec: str) -> VariationalRunner:
    """Resolve ``spec`` to ``Callable[[VariationalRunContext], VariationalStageOutcome]``.

    Supported YAML targets:

    #. **Plugin class** (no-args constructor) with ``run_variational(self, ctx)``.
    #. **Factory callable** (no args) returning either:

       - a **runner** ``Callable[[VariationalRunContext], VariationalStageOutcome]``, or
       - a **plugin instance** with ``run_variational``.
    """
    mod_name, attr_path = validate_factory_import_path(spec)
    _assert_factory_module_allowed(mod_name)
    try:
        module = importlib.import_module(mod_name)
    except ImportError as exc:
        raise PipelineError(f"algorithm_factory import failed for {spec!r}: {exc}") from exc
    try:
        obj = _walk_attr(module, attr_path)
    except AttributeError as exc:
        raise PipelineError(f"algorithm_factory attribute not found: {spec!r}") from exc

    if isinstance(obj, type):
        try:
            inst = obj()
        except TypeError as exc:
            raise PipelineError(
                f"algorithm_factory class {spec!r} must be constructible with zero arguments"
            ) from exc
        run_m = getattr(inst, "run_variational", None)
        if not callable(run_m):
            raise PipelineError(
                f"algorithm_factory plugin {spec!r} must define run_variational(ctx)"
            )
        return run_m  # type: ignore[return-value]

    if callable(obj):
        try:
            built = obj()
        except TypeError:
            # Might be the runner itself taking ctx — cannot know without calling.
            # Convention: factory must be zero-arg; if this fails, treat ``obj`` as runner.
            try:
                import inspect

                sig = inspect.signature(obj)
                if len(sig.parameters) == 1:
                    return obj  # type: ignore[return-value]
            except (TypeError, ValueError):
                pass
            raise PipelineError(
                f"algorithm_factory {spec!r}: factory callable must accept zero arguments "
                "and return a VariationalRunner"
            ) from None
        except Exception as exc:  # noqa: BLE001
            raise PipelineError(f"algorithm_factory callable {spec!r} raised when invoked") from exc

        if isinstance(built, type):
            raise PipelineError(
                f"algorithm_factory {spec!r}: factory returned a class; return a runner or instance"
            )
        if callable(built):
            return built  # type: ignore[return-value]
        run_m = getattr(built, "run_variational", None)
        if callable(run_m):
            return run_m  # type: ignore[return-value]
        raise PipelineError(
            f"algorithm_factory {spec!r}: factory must return callable(ctx) "
            "or an object with run_variational(ctx)"
        )

    raise PipelineError(f"algorithm_factory {spec!r}: expected class or callable factory")
