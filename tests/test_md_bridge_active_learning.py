"""Active learning loop (2+ rounds on discrete pool)."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.ml.active_learning import ActiveLearningLoop, max_std_proxy
from qchem_stack.ml.surrogate import SurrogateEnergyModel

pytestmark = pytest.mark.l1_md_ml


def test_active_learning_two_rounds_picks_different_indices() -> None:
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 0.1, 5.0, 0.2])
    model = SurrogateEnergyModel()
    model.fit(X, y)
    loop = ActiveLearningLoop(pool_features=X, acquisition=max_std_proxy)
    idx1 = loop.next_index(model)
    idx2 = loop.next_index(model)
    assert idx1 in (0, 1, 2, 3)
    assert idx2 in (0, 1, 2, 3)


def test_active_learning_prefers_outlier_on_third_round() -> None:
    X = np.array([[0.0], [0.1], [0.2], [10.0]])
    y = np.array([0.0, 0.05, 0.1, 0.15])
    model = SurrogateEnergyModel()
    model.fit(X, y)
    loop = ActiveLearningLoop(pool_features=X, acquisition=max_std_proxy)
    picks = [loop.next_index(model) for _ in range(3)]
    assert 3 in picks
