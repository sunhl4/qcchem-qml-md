"""Backend-agnostic mean-field wrapper protocol (bridge-facing, M2-A precursor)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast, runtime_checkable

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
        # Whitelist of attributes that may be accessed through the raw backend
        # This prevents accidental access to unintended attributes while maintaining
        # compatibility with legitimate backend-specific extensions
        _allowed_passthrough = frozenset(
            {
                "mol",
                "get_ovlp",
                "get_hcore",
                "get_fock",
                "make_rdm1",
                "make_rdm2",
                "mo_coeff",
                "mo_energy",
                "mo_occ",
                "e_tot",
                "converged",
                "with_df",
                "with_x2c",
                "with_solvent",  # PySCF extensions
                "wfn",
                "molecule",
                "basis",
                "options",  # Psi4 extensions
            }
        )

        if name not in _allowed_passthrough:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "GenericMeanFieldLike: accessing undefined attribute '%s' from raw backend. "
                "This may indicate a type error. Consider adding an explicit method.",
                name,
            )

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
            return cast(
                "np.ndarray", np.asarray(dm[0], dtype=float) + np.asarray(dm[1], dtype=float)
            )
        return cast("np.ndarray", np.asarray(dm, dtype=float))

    def make_rdm1(self) -> np.ndarray:
        return self.rdm1_ao()


class Psi4MeanFieldLike(GenericMeanFieldLike):
    def __init__(self, *, _raw: Any, _e_tot: float, _mo_energy: np.ndarray) -> None:
        super().__init__(backend_tag="psi4", _raw=_raw, _e_tot=float(_e_tot), _mo_energy=_mo_energy)

    def _ao_view(self) -> Any:
        from qchem_stack.chem.bridges.ao_basis_view import Psi4AOBasisView

        return Psi4AOBasisView(_wfn=self._raw)

    def overlap_ao(self) -> np.ndarray:
        return cast("np.ndarray", self._ao_view().overlap_ao())

    def get_ovlp(self) -> np.ndarray:
        return self.overlap_ao()

    def make_rdm1(self) -> np.ndarray:
        return cast("np.ndarray", self._ao_view().make_rdm1_ao())


def unwrap_mean_field_raw(mf: Any) -> Any:
    """Return the backend-native mean-field handle (strip MeanFieldLike wrappers)."""
    cur = mf
    seen: set[int] = set()
    while True:
        oid = id(cur)
        if oid in seen:
            break
        seen.add(oid)
        raw_handle = getattr(cur, "raw_handle", None)
        if not callable(raw_handle):
            break
        nxt = raw_handle()
        if nxt is None or nxt is cur:
            break
        cur = nxt
    return cur


def wrap_mean_field_like(
    *, backend_tag: str, raw_mf: Any, e_tot: float, mo_energy: np.ndarray
) -> MeanFieldLike:
    tag = str(backend_tag).strip().lower()
    raw_mf = unwrap_mean_field_raw(raw_mf)
    if tag == "pyscf":
        return PySCFMeanFieldLike(
            _raw=raw_mf, _e_tot=float(e_tot), _mo_energy=np.asarray(mo_energy, dtype=float)
        )
    if tag == "psi4":
        return Psi4MeanFieldLike(
            _raw=raw_mf, _e_tot=float(e_tot), _mo_energy=np.asarray(mo_energy, dtype=float)
        )
    return GenericMeanFieldLike(
        backend_tag=tag or "unknown",
        _raw=raw_mf,
        _e_tot=float(e_tot),
        _mo_energy=np.asarray(mo_energy, dtype=float),
    )


def nuclear_repulsion_energy_au(mf_like: MeanFieldLike) -> float | None:
    """Best-effort nuclear repulsion extraction across backends."""
    raw = mf_like.raw_handle()
    try:
        mol = getattr(raw, "mol", None)
        if mol is not None and hasattr(mol, "energy_nuc"):
            return float(mol.energy_nuc())
    except Exception:  # noqa: BLE001
        return None
    return None
