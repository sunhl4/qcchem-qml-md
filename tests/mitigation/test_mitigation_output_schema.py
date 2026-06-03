"""Mitigation helpers expose stable report-shaped outputs."""

from __future__ import annotations

import pytest

from qchem_stack.mitigation.spam import SPAMCalibration, default_two_qubit_spam_matrix
from qchem_stack.mitigation.zne import linear_extrapolation, zne_scale_energy


def test_spam_calibration_dataclass_fields() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    assert cal.readout_assignment is not None
    assert len(cal.readout_assignment) == 4


def test_zne_scale_energy_returns_finite_float() -> None:
    out = zne_scale_energy(-1.0, 2.0)
    assert isinstance(out, float)
    assert pytest.approx(-1.0 * (1.0 + 0.01 * (2.0 - 1.0))) == out


def test_linear_extrapolation_returns_energy_and_uncertainty() -> None:
    e0, unc = linear_extrapolation([-1.0, -1.01, -1.02], [1.0, 2.0, 3.0])
    assert isinstance(e0, float)
    assert isinstance(unc, float)
