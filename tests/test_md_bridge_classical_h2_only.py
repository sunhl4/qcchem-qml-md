"""MD bridge classical H2 path without QML-FF installed."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.md_bridge.classical_h2_ff import ClassicalH2MorseModel


def test_classical_h2_ff_energy_forces_finite() -> None:
    pytest.importorskip("jax")
    model = ClassicalH2MorseModel()
    pos = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float)
    species = np.array([0, 0], dtype=np.int32)
    e, f = model.compute_energy_and_forces(pos, species)
    assert np.isfinite(float(e))
    assert np.asarray(f).shape == (2, 3)
