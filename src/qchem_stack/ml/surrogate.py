from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import cast

import numpy as np


@dataclass
class SurrogateEnergyModel:
    """Ridge-style linear surrogate on scalar features.

    Deprecated for MD/ML workflows: prefer :mod:`qchem_stack.md_bridge` and QML-FF presets.
    """

    weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray, lam: float = 1e-3) -> None:
        warnings.warn(
            "SurrogateEnergyModel is a toy ridge stub; use qchem_stack.md_bridge for production MD/ML.",
            DeprecationWarning,
            stacklevel=2,
        )
        x = np.c_[np.ones(len(X)), X]
        d = x.shape[1]
        self.weights = np.linalg.solve(x.T @ x + lam * np.eye(d), x.T @ y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("call fit first")
        x = np.c_[np.ones(len(X)), X]
        return cast("np.ndarray", x @ self.weights)
