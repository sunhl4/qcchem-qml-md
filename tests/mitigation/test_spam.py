"""Unit tests for SPAM readout correction (``qchem_stack.mitigation.spam``)."""

from __future__ import annotations

import pytest

from qchem_stack.mitigation.spam import (
    SPAMCalibration,
    apply_spam,
    correct_n_qubit_histogram,
    correct_two_qubit_histogram,
    default_two_qubit_spam_matrix,
    propagate_spam_uncertainty,
)


def _identity_2x2() -> list[list[float]]:
    return [[1.0, 0.0], [0.0, 1.0]]


def test_apply_spam_identity_returns_measured() -> None:
    cal = SPAMCalibration(per_qubit_matrices=[_identity_2x2()])
    assert apply_spam(0.7, cal) == pytest.approx(0.7, abs=1e-9)


def test_apply_spam_no_calibration_unchanged() -> None:
    assert apply_spam(0.42, SPAMCalibration()) == pytest.approx(0.42)


def test_apply_spam_clamps_to_unit_interval() -> None:
    # Strong bias toward 1|0) can push inversion outside [0, 1] before clamp.
    cal = SPAMCalibration(
        readout_assignment=[
            [0.1, 0.9],
            [0.9, 0.1],
        ]
    )
    p0 = apply_spam(0.99, cal)
    assert 0.0 <= p0 <= 1.0


def test_apply_spam_singular_matrix_returns_uncorrected() -> None:
    cal = SPAMCalibration(
        per_qubit_matrices=[
            [[1.0, 1.0], [1.0, 1.0]],
        ]
    )
    assert apply_spam(0.5, cal) == pytest.approx(0.5)


def test_apply_spam_wrong_matrix_shape_returns_uncorrected() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    assert apply_spam(0.5, cal) == pytest.approx(0.5)


def test_correct_two_qubit_histogram_toy_matrix() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    probs = correct_two_qubit_histogram({"00": 90, "01": 10, "10": 0, "11": 0}, cal)
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-6)
    assert probs["00"] > probs["01"]


def test_correct_two_qubit_histogram_no_assignment_normalizes_counts() -> None:
    probs = correct_two_qubit_histogram({"00": 30, "11": 70}, SPAMCalibration())
    assert probs["00"] == pytest.approx(0.3, abs=1e-9)
    assert probs["11"] == pytest.approx(0.7, abs=1e-9)


def test_correct_two_qubit_histogram_empty_counts_uniform() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    probs = correct_two_qubit_histogram({}, cal)
    assert all(probs[k] == pytest.approx(0.25, abs=1e-9) for k in ("00", "01", "10", "11"))


def test_correct_two_qubit_histogram_invalid_matrix_shape() -> None:
    cal = SPAMCalibration(readout_assignment=[[1.0, 0.0], [0.0, 1.0]])
    with pytest.raises(ValueError, match="4x4"):
        correct_two_qubit_histogram({"00": 1}, cal)


def test_correct_two_qubit_histogram_tikhonov_regularization() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    probs = correct_two_qubit_histogram(
        {"00": 50, "01": 50, "10": 0, "11": 0},
        cal,
        regularization=1e-3,
    )
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-5)


def test_correct_n_qubit_histogram_per_qubit_tensor_product() -> None:
    cal = SPAMCalibration(
        per_qubit_matrices=[
            [[0.95, 0.05], [0.05, 0.95]],
            [[0.90, 0.10], [0.10, 0.90]],
            [[0.98, 0.02], [0.02, 0.98]],
        ]
    )
    counts = {"000": 100, "001": 0, "010": 0, "011": 0, "100": 0, "101": 0, "110": 0, "111": 0}
    probs = correct_n_qubit_histogram(counts, cal, n_qubits=3)
    assert len(probs) == 8
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-6)
    assert probs["000"] > probs["111"]


def test_correct_n_qubit_histogram_rejects_large_full_matrix() -> None:
    cal = SPAMCalibration()
    with pytest.raises(ValueError, match="Full-matrix SPAM"):
        correct_n_qubit_histogram({"0" * 13: 1}, cal, n_qubits=13)


def test_propagate_spam_uncertainty_without_calibration() -> None:
    counts = {"00": 400, "01": 100, "10": 0, "11": 0}
    errs = propagate_spam_uncertainty(counts, SPAMCalibration(), n_qubits=2)
    assert set(errs) == {"00", "01", "10", "11"}
    assert all(e >= 0.0 for e in errs.values())


def test_propagate_spam_uncertainty_with_calibration() -> None:
    cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
    counts = {"00": 500, "01": 0, "10": 0, "11": 0}
    errs = propagate_spam_uncertainty(counts, cal, n_qubits=2)
    assert errs["00"] >= errs["01"]
