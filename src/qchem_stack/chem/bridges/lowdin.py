"""Backend-neutral Löwdin orthogonalization helpers for embedding workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import numpy as np

from qchem_stack.chem.tolerances import LOWDIN_SINGULARITY_TOLERANCE


@dataclass(frozen=True)
class LowdinTensors:
    """Löwdin-orthogonal AO tensors (``C_low^T S C_low = I``)."""

    c_low: np.ndarray
    h1_low: np.ndarray
    dm_low: np.ndarray


def coalesce_spin_summed_rdm1(rdm1_raw: Any) -> np.ndarray:
    """Collapse PySCF alpha/beta tuple densities to a single spatial AO matrix."""
    if isinstance(rdm1_raw, (tuple, list)):
        return cast(
            "np.ndarray",
            np.asarray(rdm1_raw[0], dtype=float) + np.asarray(rdm1_raw[1], dtype=float),
        )
    return cast("np.ndarray", np.asarray(rdm1_raw, dtype=float))


def build_lowdin_tensors(
    overlap: np.ndarray,
    hcore: np.ndarray,
    rdm1_ao: np.ndarray,
    *,
    singular_tol: float = LOWDIN_SINGULARITY_TOLERANCE,
) -> LowdinTensors:
    """Build ``C_low``, one-electron, and density matrices in the Löwdin basis."""
    s = np.asarray(overlap, dtype=float)
    hcore_a = np.asarray(hcore, dtype=float)
    dm_ao = coalesce_spin_summed_rdm1(rdm1_ao)
    evals, evecs = np.linalg.eigh(s)
    if np.min(evals) <= singular_tol:
        raise ValueError("AO overlap matrix is near singular; cannot build stable Lowdin basis.")
    c_low = np.asarray(evecs @ np.diag(evals**-0.5) @ evecs.T, dtype=float)
    h1_low = np.einsum("pi,pq,qj->ij", c_low, hcore_a, c_low, optimize=True)
    c_inv = np.linalg.inv(c_low)
    dm_low = np.asarray(c_inv @ dm_ao @ c_inv.T, dtype=float)
    return LowdinTensors(c_low=c_low, h1_low=h1_low, dm_low=dm_low)
