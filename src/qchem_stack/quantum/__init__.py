"""Quantum algorithms and utilities.

This module registers config validators on import to decouple the config
layer from runtime quantum dependencies. Import this module before
constructing :class:`~qchem_stack.config.QuantumSpec` instances.
"""

from __future__ import annotations


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
            if algorithm_factory:
                validate_factory_import_path(algorithm_factory)
                return
            if not is_registered_variational_id(algorithm):
                raise ValueError(
                    f"Unknown quantum.algorithm={algorithm!r}. "
                    "Use a built-in id or set quantum.algorithm_factory to an import path."
                )

        set_algorithm_validator(algorithm_validator)
        set_operator_pool_validator(is_registered_operator_pool_id)
    except ImportError:
        pass


_inject_config_validators()

__all__: list[str] = []
