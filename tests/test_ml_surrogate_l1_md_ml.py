"""Light-weight physics-aware surrogate smoke (extends ``l1_md_ml`` beyond md_bridge)."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.ml.surrogate import SurrogateEnergyModel

pytestmark = pytest.mark.l1_md_ml


def test_surrogate_ridge_fit_predict_smoke() -> None:
    rng = np.random.default_rng(0)
    X = rng.standard_normal((12, 3))
    y = X[:, 0] * 0.5 + 0.1 * rng.standard_normal(12)
    m = SurrogateEnergyModel()
    m.fit(X, y)
    pred = m.predict(X[:2])
    assert pred.shape == (2,)
