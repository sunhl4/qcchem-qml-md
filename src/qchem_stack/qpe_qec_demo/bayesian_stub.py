from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class BayesianQPEStub:
    """Posterior over phase grid (toy) — swap with phayes/JAX in production."""

    grid_points: int = 256

    def estimate(self, measurements: list[tuple[float, float]]) -> dict[str, Any]:
        """Each item is (bit_outcome, phase_setting); return MAP phase in a small JSON-safe dict."""
        phis = np.linspace(-np.pi, np.pi, self.grid_points, endpoint=False)
        logp = np.zeros_like(phis)
        for y, beta in measurements:
            p = np.cos(phis * beta + y * np.pi) ** 2
            logp += np.log(np.maximum(p, 1e-12))
        idx = int(np.argmax(logp))
        return {
            "schema": "bayesian_qpe_stub_map_v1",
            "map_phase": float(phis[idx]),
            "grid_points": int(self.grid_points),
            "argmax_index": idx,
        }
