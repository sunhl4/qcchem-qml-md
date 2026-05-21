"""HEA angle padding helpers for Pauli averaging protocols."""

from __future__ import annotations

import numpy as np


def hea_angles_for_depth(
    angles: np.ndarray, *, n_qubits: int, base_depth: int, eff_depth: int
) -> np.ndarray:
    """Pad or truncate variational angles for ``hea_state`` when ZNE uses a larger effective HEA depth."""
    n_base = int(2 * n_qubits * base_depth)
    n_eff = int(2 * n_qubits * eff_depth)
    a = np.asarray(angles, dtype=float).reshape(-1)
    if a.size == n_eff:
        return a
    if a.size != n_base:
        raise ValueError(
            f"HEA angles length mismatch: got {a.size}, expected {n_base} for depth={base_depth} "
            f"or {n_eff} for effective depth={eff_depth}"
        )
    if eff_depth <= base_depth:
        return a[:n_eff]
    return np.concatenate([a, np.zeros(n_eff - n_base, dtype=float)])
