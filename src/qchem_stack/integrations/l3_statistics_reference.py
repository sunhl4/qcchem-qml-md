"""
Open reference: L3-style **energy CI stub** from independent energy samples (e.g. repeated jobs).

Not device-calibration parity; a reproducible bootstrap for Methods text.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def energy_bootstrap_ci_stub(
    energy_samples: list[float],
    *,
    n_bootstrap: int = 400,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Percentile bootstrap on the mean energy from i.i.d. batch means (open stack).

    If fewer than two samples, returns a structured skip row.
    """
    if len(energy_samples) < 2:
        return {
            "schema": "l3_energy_bootstrap_stub_v1",
            "status": "insufficient_samples",
            "n_samples": len(energy_samples),
        }
    rng = np.random.default_rng(seed)
    arr = np.asarray(energy_samples, dtype=float)
    n = arr.size
    means = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        means[i] = float(rng.choice(arr, size=n, replace=True).mean())
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "schema": "l3_energy_bootstrap_stub_v1",
        "status": "ok",
        "n_samples": int(n),
        "n_bootstrap": int(n_bootstrap),
        "alpha": float(alpha),
        "mean_of_input_samples": float(arr.mean()),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "seed": int(seed),
    }
