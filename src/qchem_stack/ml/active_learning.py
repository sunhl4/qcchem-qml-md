from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.ml.surrogate import SurrogateEnergyModel


@dataclass
class ActiveLearningLoop:
    """Pick next geometry index by max predicted uncertainty (toy on discrete pool)."""

    pool_features: np.ndarray
    acquisition: Callable[[np.ndarray, SurrogateEnergyModel], int]

    def next_index(self, model: SurrogateEnergyModel) -> int:
        return int(self.acquisition(self.pool_features, model))


def max_std_proxy(X: np.ndarray, model: SurrogateEnergyModel) -> int:
    """Use deviation from mean prediction as exploration proxy."""
    preds = model.predict(X)
    return int(np.argmax(np.abs(preds - preds.mean())))
