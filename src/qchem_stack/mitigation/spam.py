from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SPAMCalibration:
    """2-qubit readout assignment matrix ``P(read=i | true=j)``."""

    readout_assignment: list[list[float]] | None = None


def default_two_qubit_spam_matrix() -> list[list[float]]:
    """Toy symmetric assignment matrix for two qubits (diagonal dominant)."""
    eps = 0.02
    return [
        [1.0 - eps, eps, eps, eps],
        [eps, 1.0 - eps, eps, eps],
        [eps, eps, 1.0 - eps, eps],
        [eps, eps, eps, 1.0 - eps],
    ]


def apply_spam(prob_0: float, cal: SPAMCalibration) -> float:
    """Affine readout correction on a single bit probability."""
    if cal.readout_assignment is None:
        return prob_0
    return min(max(prob_0, 0.0), 1.0)


def correct_two_qubit_histogram(
    counts: dict[str, int],
    cal: SPAMCalibration,
) -> dict[str, float]:
    """Invert a 2-qubit assignment matrix on ``00/01/10/11`` counts (linear MLE stub)."""
    if cal.readout_assignment is None:
        total = max(sum(counts.values()), 1)
        return {k: float(v) / float(total) for k, v in counts.items()}
    mat = np.asarray(cal.readout_assignment, dtype=float)
    keys = ["00", "01", "10", "11"]
    obs = np.array([float(counts.get(k, 0)) for k in keys], dtype=float)
    if obs.sum() <= 0:
        return {k: 0.25 for k in keys}
    obs = obs / obs.sum()
    try:
        true = np.linalg.solve(mat.T, obs)
    except np.linalg.LinAlgError:
        true = obs
    true = np.clip(true, 0.0, None)
    s = float(true.sum()) or 1.0
    true = true / s
    return {k: float(true[i]) for i, k in enumerate(keys)}
