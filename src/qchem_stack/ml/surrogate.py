from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SurrogateEnergyModel:
    """Ridge-style linear surrogate on scalar features (placeholder for GNN)."""

    weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray, lam: float = 1e-3) -> None:
        x = np.c_[np.ones(len(X)), X]
        d = x.shape[1]
        self.weights = np.linalg.solve(x.T @ x + lam * np.eye(d), x.T @ y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("call fit first")
        x = np.c_[np.ones(len(X)), X]
        return x @ self.weights
