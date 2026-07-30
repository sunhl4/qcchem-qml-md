"""Quantum algorithms and utilities.

This module registers config validators on import to decouple the config
layer from runtime quantum dependencies. Import this module before
constructing :class:`~qchem_stack.config.QuantumSpec` instances.

Strict mode
-----------
Set the ``QCHEM_QUANTUM_STRICT`` environment variable to a truthy value
(``1`` / ``true`` / ``yes`` / ``on``) to harden validation for production:

- Custom ``quantum.algorithm_factory`` import paths are **rejected**; only
  built-in registered algorithm ids are accepted.

This is opt-in; tests and local development are unaffected (the variable is
unset). Operator-pool validation already rejects unregistered ids in all
modes. See ``.env.example`` and ``SECURITY.md``.
"""

from __future__ import annotations

import os

_TRUTHY = {"1", "true", "yes", "on"}


def is_quantum_strict() -> bool:
    """Return ``True`` when ``QCHEM_QUANTUM_STRICT`` is set to a truthy value."""
    return os.environ.get("QCHEM_QUANTUM_STRICT", "").strip().lower() in _TRUTHY


def _inject_config_validators() -> None:
    """Register algorithm and operator-pool validators into the config layer."""
    try:
        from qchem_stack.config._quantum_validation import (
            set_algorithm_validator,
            set_operator_pool_validator,
        )
        from qchem_stack.quantum.operator_pool_registry import is_registered_operator_pool_id
        from qchem_stack.quantum.variational_plugins.loader import validate_factory_import_path
        from qchem_stack.quantum.variational_plugins.registry import is_registered_variational_id

        def algorithm_validator(algorithm: str, algorithm_factory: str | None) -> None:
            strict = is_quantum_strict()
            if algorithm_factory:
                if strict:
                    raise ValueError(
                        f"QCHEM_QUANTUM_STRICT=1 disallows custom algorithm_factory="
                        f"{algorithm_factory!r}; use a registered algorithm id "
                        f"(algorithm={algorithm!r})."
                    )
                validate_factory_import_path(algorithm_factory)
                return
            if not is_registered_variational_id(algorithm):
                raise ValueError(
                    f"Unknown quantum.algorithm={algorithm!r}. "
                    "Use a built-in id or set quantum.algorithm_factory to an import path."
                )

        set_algorithm_validator(algorithm_validator)
        # Operator-pool validator contract is bool-returning (the config framework
        # raises on False); strict mode does not change it — unregistered pools
        # are already rejected. The strict hardening targets algorithm_factory.
        set_operator_pool_validator(is_registered_operator_pool_id)
    except ImportError:
        pass


_inject_config_validators()

# NOTE: ``__all__`` is intentionally empty — this is a public-surface contract
# (see ``tests/quantum/test_quantum_public_surface.py``). ``is_quantum_strict``
# is still importable directly via ``from qchem_stack.quantum import is_quantum_strict``;
# it is deliberately not star-exported.
__all__: list[str] = []
