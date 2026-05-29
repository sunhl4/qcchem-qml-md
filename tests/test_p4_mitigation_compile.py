"""Richardson ZNE extrapolation and SPAM 2-qubit calibration."""

from __future__ import annotations

import pytest

from qchem_stack.mitigation.spam import (
    SPAMCalibration,
    correct_two_qubit_histogram,
    default_two_qubit_spam_matrix,
)
from qchem_stack.mitigation.zne import richardson_extrapolation, zne_scale_energy


def test_richardson_extrapolation_linear_noise() -> None:
    scales = [1.0, 2.0, 3.0]
    base = -1.0
    energies = [zne_scale_energy(base, s) for s in scales]
    ex = richardson_extrapolation(energies, scales, order=1)
    assert ex == pytest.approx(base, abs=0.05)


def test_spam_two_qubit_histogram_inversion() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    probs = correct_two_qubit_histogram({"00": 90, "01": 10, "10": 0, "11": 0}, cal)
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-6)
    assert probs["00"] > probs["01"]
