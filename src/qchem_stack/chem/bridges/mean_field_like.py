"""Backend-agnostic mean-field wrapper protocol (bridge-facing, M2-A precursor)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class MeanFieldLike(Protocol):
    """Small common subset consumed by bridge/downstream helpers."""

    backend_tag: str

    def total_energy_au(self) -> float: ...

    def mo_energies(self) -> np.ndarray: ...

    def raw_handle(self) -> Any: ...


@dataclass
class GenericMeanFieldLike:
    """Fallback wrapper for non-PySCF backends with attribute pass-through."""

    backend_tag: str
    _raw: Any
    _e_tot: float
    _mo_energy: np.ndarray

    def total_energy_au(self) -> float:
        return float(self._e_tot)

    def mo_energies(self) -> np.ndarray:
        return np.asarray(self._mo_energy, dtype=float)

    def raw_handle(self) -> Any:
        return self._raw

    def __getattr__(self, name: str) -> Any:
        return getattr(self._raw, name)


class PySCFMeanFieldLike(GenericMeanFieldLike):
    def __init__(self, *, _raw: Any, _e_tot: float, _mo_energy: np.ndarray) -> None:
        super().__init__(
            backend_tag="pyscf", _raw=_raw, _e_tot=float(_e_tot), _mo_energy=_mo_energy
        )

    def overlap_ao(self) -> np.ndarray:
        return np.asarray(self._raw.get_ovlp(), dtype=float)

    def hcore_ao(self) -> np.ndarray:
        return np.asarray(self._raw.get_hcore(), dtype=float)

    def rdm1_ao(self) -> np.ndarray:
        dm = self._raw.make_rdm1()
        if isinstance(dm, (tuple, list)):
            return np.asarray(dm[0], dtype=float) + np.asarray(dm[1], dtype=float)
        return np.asarray(dm, dtype=float)


def wrap_mean_field_like(
    *, backend_tag: str, raw_mf: Any, e_tot: float, mo_energy: np.ndarray
) -> MeanFieldLike:
    tag = str(backend_tag).strip().lower()
    if tag == "pyscf":
        return PySCFMeanFieldLike(
            _raw=raw_mf, _e_tot=float(e_tot), _mo_energy=np.asarray(mo_energy, dtype=float)
        )
    return GenericMeanFieldLike(
        backend_tag=tag or "unknown",
        _raw=raw_mf,
        _e_tot=float(e_tot),
        _mo_energy=np.asarray(mo_energy, dtype=float),
    )
