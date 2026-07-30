"""Cross-field validation helpers for :mod:`qchem_stack.config.quantum`."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .quantum import QuantumSpec


# Validator registry: injected by quantum/__init__.py to avoid runtime imports from quantum/
_algorithm_validator: Callable[[str, str | None], None] | None = None


def set_algorithm_validator(validator: Callable[[str, str | None], None]) -> None:
    """Register the algorithm validator (called by quantum/__init__.py)."""
    global _algorithm_validator
    _algorithm_validator = validator


def validate_algorithm_registered_or_factory(spec: QuantumSpec) -> None:
    """Validate that the algorithm is registered or a valid factory path."""
    global _algorithm_validator
    if _algorithm_validator is None:
        with contextlib.suppress(ImportError):
            import qchem_stack.quantum  # noqa: F401
    if _algorithm_validator is None:
        from qchem_stack.exceptions import ConfigurationError

        raise ConfigurationError(
            "quantum algorithm validator not injected. "
            "Import qchem_stack.quantum before constructing QuantumSpec, "
            "or call set_algorithm_validator() manually."
        )
    _algorithm_validator(spec.algorithm, spec.algorithm_factory)


def validate_pauli_shot_mode_mutually_exclusive(spec: QuantumSpec) -> None:
    pauli = spec.pauli
    if pauli.run_sampled and pauli.run_qiskit_shots:
        raise ValueError(
            "Set only one of quantum.pauli.run_sampled (statevector MC) and "
            "quantum.pauli.run_qiskit_shots (Qiskit bitstrings), not both."
        )


def validate_uccsd_trotter_steps(spec: QuantumSpec) -> None:
    trotter_steps = spec.variational.uccsd_trotter_steps
    if trotter_steps is None:
        return
    if spec.variational.ansatz != "uccsd":
        raise ValueError(
            "quantum.variational.uccsd_trotter_steps is only valid when variational.ansatz='uccsd'."
        )
    if int(trotter_steps) < 1:
        raise ValueError("quantum.variational.uccsd_trotter_steps must be >= 1 when set.")


def validate_vqd_penalty_weights_len(spec: QuantumSpec) -> None:
    vqd = spec.excited.vqd
    penalty_weights = vqd.penalty_weights
    if penalty_weights is None:
        return
    expected_len = max(0, int(vqd.n_states) - 1)
    if len(penalty_weights) != expected_len:
        raise ValueError(
            "quantum.excited.vqd.penalty_weights must have length n_states - 1 "
            f"({expected_len}), got {len(penalty_weights)}"
        )


def validate_vqd_max_overlap_warn_nonneg(value: float | None) -> float | None:
    if value is None:
        return None
    normalized = float(value)
    if normalized < 0.0:
        raise ValueError("quantum.excited.vqd.max_overlap_warn must be >= 0 when set")
    return normalized


# Operator pool validator registry: injected by quantum/__init__.py
_operator_pool_validator: Callable[[str], bool] | None = None


def set_operator_pool_validator(validator: Callable[[str], bool]) -> None:
    """Register the operator pool validator (called by quantum/__init__.py)."""
    global _operator_pool_validator
    _operator_pool_validator = validator


def validate_operator_pool_ids(spec: QuantumSpec) -> None:
    """Validate that operator pool IDs are registered."""
    global _operator_pool_validator
    if _operator_pool_validator is None:
        with contextlib.suppress(ImportError):
            import qchem_stack.quantum  # noqa: F401
    if _operator_pool_validator is None:
        from qchem_stack.exceptions import ConfigurationError

        raise ConfigurationError(
            "operator pool validator not injected. "
            "Import qchem_stack.quantum before constructing QuantumSpec, "
            "or call set_operator_pool_validator() manually."
        )
    for field_path, pool_id in (
        ("quantum.adapt.pool_id", spec.adapt.pool_id),
        ("quantum.iqeb.pool_id", spec.iqeb.pool_id),
        ("quantum.iqcc.pool_id", spec.iqcc.pool_id),
    ):
        pid = str(pool_id)
        if not _operator_pool_validator(pid):
            raise ValueError(
                f"Unknown {field_path}={pid!r}. "
                "Use a registered operator pool id (see operator_pool_registry)."
            )
