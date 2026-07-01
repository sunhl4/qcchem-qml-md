"""Zero-Noise Extrapolation (ZNE) mitigation."""

from __future__ import annotations

from qchem_stack.mitigation.zne_extrapolation import (
    exponential_extrapolation,
    extrapolation_uncertainty,
    linear_extrapolation,
    polynomial_extrapolation,
    richardson_extrapolation,
    select_extrapolation_model,
)
from qchem_stack.mitigation.zne_fold import (
    _zne_scale_energy_linear_stub,
    fold_gates_local,
    fold_unitary_circuit,
)

zne_scale_energy = _zne_scale_energy_linear_stub

__all__ = [
    "exponential_extrapolation",
    "extrapolation_uncertainty",
    "fold_gates_local",
    "fold_unitary_circuit",
    "linear_extrapolation",
    "polynomial_extrapolation",
    "richardson_extrapolation",
    "select_extrapolation_model",
    "zne_scale_energy",
]
