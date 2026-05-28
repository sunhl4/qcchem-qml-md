"""Lowdin orthogonalization numerical stability tests."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.bridges.lowdin import build_lowdin_tensors, coalesce_spin_summed_rdm1


def test_lowdin_overlap_produces_identity_metric() -> None:
    s = np.array([[1.0, 0.3], [0.3, 1.0]])
    hcore = np.diag([0.1, 0.2])
    dm = np.eye(2) * 0.5
    low = build_lowdin_tensors(s, hcore, dm)
    metric = low.c_low.T @ s @ low.c_low
    assert np.allclose(metric, np.eye(2), atol=1e-10)


def test_lowdin_rejects_singular_overlap() -> None:
    s = np.array([[1.0, 1.0], [1.0, 1.0]])
    hcore = np.eye(2)
    dm = np.eye(2)
    with pytest.raises(ValueError, match="near singular"):
        build_lowdin_tensors(s, hcore, dm)


def test_coalesce_spin_summed_rdm1_from_tuple() -> None:
    alpha = np.array([[0.4, 0.0], [0.0, 0.1]])
    beta = np.array([[0.3, 0.0], [0.0, 0.2]])
    total = coalesce_spin_summed_rdm1((alpha, beta))
    assert np.allclose(total, alpha + beta)
