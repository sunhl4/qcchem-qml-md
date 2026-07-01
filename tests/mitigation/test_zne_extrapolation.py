"""Unit tests for ZNE extrapolation models."""

from __future__ import annotations

import pytest

from qchem_stack.mitigation.zne_extrapolation import (
    exponential_extrapolation,
    extrapolation_uncertainty,
    linear_extrapolation,
    polynomial_extrapolation,
    richardson_extrapolation,
    select_extrapolation_model,
)


@pytest.mark.parametrize(
    "scales,energies",
    [
        ([0.0, 0.1, 0.2], [1.0, 2.0, 3.0]),
        ([1.0, 2.0, 3.0], [0.5, 0.4, 0.3]),
        ([0.0, 1.0], [1.0, 2.0]),
    ],
)
def test_linear_extrapolation(scales: list[float], energies: list[float]) -> None:
    energy, err = linear_extrapolation(scales, energies)
    assert isinstance(energy, float)
    assert err >= 0.0


def test_linear_extrapolation_requires_two_points() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        linear_extrapolation([0.0], [1.0])


def test_richardson_extrapolation() -> None:
    energy = richardson_extrapolation([0.1, 0.05, 0.02], [1.0, 2.0, 3.0])
    assert isinstance(energy, float)


@pytest.mark.parametrize(
    "scales,energies",
    [
        ([1.0, 0.95, 0.9], [1.0, 2.0, 3.0]),
        ([0.5, 0.6, 0.7], [10.0, 20.0, 30.0]),
    ],
)
def test_exponential_extrapolation(scales: list[float], energies: list[float]) -> None:
    energy, err = exponential_extrapolation(scales, energies)
    assert isinstance(energy, float)
    assert err >= 0.0


def test_polynomial_extrapolation() -> None:
    energy, err = polynomial_extrapolation([0.0, 0.1, 0.2], [1.0, 1.05, 1.1], order=2)
    assert isinstance(energy, float)
    assert err >= 0.0


@pytest.mark.parametrize(
    "scales,energies",
    [
        ([1.0, 0.95, 0.9], [1.0, 2.0, 3.0]),
        ([0.0, 0.1, 0.2], [0.5, 0.45, 0.4]),
    ],
)
def test_select_extrapolation_model(scales: list[float], energies: list[float]) -> None:
    name, energy, uncertainty = select_extrapolation_model(scales, energies)
    assert name in {"linear", "exponential", "polynomial"}
    assert isinstance(energy, float)
    assert uncertainty >= 0.0


@pytest.mark.parametrize("model", ["linear", "polynomial", "exponential"])
def test_extrapolation_uncertainty(model: str) -> None:
    u = extrapolation_uncertainty([1.0, 1.1, 1.2], [1.0, 2.0, 3.0], model=model)
    assert u >= 0.0


def test_select_extrapolation_model_aic() -> None:
    name, energy, uncertainty = select_extrapolation_model(
        [1.0, 2.0, 3.0], [0.5, 0.4, 0.35], criterion="aic"
    )
    assert name in {"linear", "exponential", "polynomial"}
    assert isinstance(energy, float)
    assert uncertainty >= 0.0


def test_polynomial_extrapolation_exact_fit_has_zero_uncertainty() -> None:
    energy, err = polynomial_extrapolation([1.0, 2.0], [1.0, 1.1], order=1)
    assert isinstance(energy, float)
    assert err == 0.0


def test_polynomial_extrapolation_rejects_high_order() -> None:
    with pytest.raises(ValueError, match="Polynomial order"):
        polynomial_extrapolation([1.0], [1.0], order=1)
