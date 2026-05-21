"""PySCF runtime object shims for static checking (PySCF ships incomplete stubs)."""

from __future__ import annotations

from typing import Any, cast

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import MeanFieldLike, unwrap_mean_field_raw

# PySCF mean-field / MCSCF objects (attribute surface varies by build).
PyscfMeanField = Any
PyscfCasSolver = Any


def as_pyscf_mf(mf: MeanFieldLike) -> PyscfMeanField:
    """Return the backend mean-field handle for PySCF attribute access."""
    return cast("PyscfMeanField", unwrap_mean_field_raw(mf))


def as_pyscf_cas(cas: object) -> PyscfCasSolver:
    return cast("PyscfCasSolver", cas)


def as_complex_array(value: object) -> np.ndarray:
    """Normalize array-likes for complex-safe ``np.imag`` / ``np.real`` under pyright."""
    return np.asarray(value, dtype=np.complex128)


def max_abs_imag(arr: object, *, tol: float = 1e-7) -> float:
    arr_a = as_complex_array(arr)
    return float(np.max(np.abs(np.imag(arr_a))))


def as_real_array(arr: object) -> np.ndarray:
    return np.asarray(np.real(as_complex_array(arr)), dtype=float)
