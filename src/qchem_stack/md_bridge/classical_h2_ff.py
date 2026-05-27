"""Analytical H2 Morse force field for validating the MD active-learning loop.

Uses a two-body Morse potential in eV/Å (QML-FF/JAX-MD internal units). Training
fits ``(D_e, a, r_e)`` to a :class:`~qchem_stack.md_bridge.QMEFDataset` via
nonlinear least squares on bond lengths. No ``qmlff`` dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    from qchem_stack.md_bridge.schema import QMEFDataset

_BOHR_TO_ANGSTROM = 0.529177210903
_HARTREE_TO_EV = 27.211386245988
_HARTREE_BOHR_TO_EV_ANG = _HARTREE_TO_EV / _BOHR_TO_ANGSTROM


def _bond_length_ang(positions_bohr: np.ndarray) -> float:
    pos = np.asarray(positions_bohr, dtype=np.float64)
    if pos.shape != (2, 3):
        raise ValueError(f"H2 Morse model expects 2 atoms; got shape {pos.shape!r}")
    return float(np.linalg.norm(pos[1] - pos[0]) * _BOHR_TO_ANGSTROM)


@dataclass
class ClassicalH2MorseParams:
    """Morse parameters in QML-FF units (eV, Å)."""

    de_ev: float = 4.75
    a_inv_ang: float = 1.93
    re_ang: float = 0.74
    shift_ev: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "de_ev": float(self.de_ev),
            "a_inv_ang": float(self.a_inv_ang),
            "re_ang": float(self.re_ang),
            "shift_ev": float(self.shift_ev),
        }


@dataclass
class ClassicalH2MorseHandle:
    """Handle mirroring :class:`~qchem_stack.md_bridge.QmlffModelHandle` surface."""

    model: ClassicalH2MorseModel
    params: dict[str, Any]
    species_list: list[str]
    backend: str = "classical_h2"
    preset_name: str = "classical_h2_morse"
    train_meta: dict[str, Any] = field(default_factory=dict)
    opt_state: Any | None = None
    step: int = 0
    epoch: int = 0

    def species_indices(self, atomic_numbers: Sequence[int]) -> np.ndarray:
        _sym = {1: "H"}
        idx: list[int] = []
        for z in atomic_numbers:
            sym = _sym.get(int(z), "X")
            if sym not in self.species_list:
                raise ValueError(f"species {sym!r} not in {self.species_list!r}")
            idx.append(self.species_list.index(sym))
        return np.asarray(idx, dtype=np.int32)


class ClassicalH2MorseModel:
    """JAX-MD-compatible Morse PES for H2 (energy in eV, positions in Å)."""

    def __init__(self, *, species_list: list[str] | None = None, cutoff: float = 6.0):
        self.species_list = list(species_list or ["H"])
        self.cutoff = float(cutoff)
        self._params = ClassicalH2MorseParams()

    def get_parameters(self) -> dict[str, Any]:
        return self._params.as_dict()

    def set_parameters(self, params: dict[str, Any]) -> None:
        self._params = ClassicalH2MorseParams(
            de_ev=float(params.get("de_ev", self._params.de_ev)),
            a_inv_ang=float(params.get("a_inv_ang", self._params.a_inv_ang)),
            re_ang=float(params.get("re_ang", self._params.re_ang)),
            shift_ev=float(params.get("shift_ev", self._params.shift_ev)),
        )

    @staticmethod
    def _morse_energy_ev(r_ang: np.ndarray, p: ClassicalH2MorseParams) -> np.ndarray:
        x = np.exp(-p.a_inv_ang * (r_ang - p.re_ang))
        return p.de_ev * (1.0 - x) ** 2 - p.de_ev + p.shift_ev

    def compute_total_energy(
        self,
        positions: Any,
        species: Any,
        params: dict[str, Any] | None = None,
        box: Any = None,
        neighbor_list: Any = None,
    ) -> Any:
        import jax.numpy as jnp

        p = ClassicalH2MorseParams(**(params or self.get_parameters()))
        pos = np.asarray(positions, dtype=np.float64)
        r = float(np.linalg.norm(pos[1] - pos[0]))
        e = float(self._morse_energy_ev(np.array(r), p))
        return jnp.asarray(e, dtype=jnp.float32)

    def compute_forces(
        self,
        positions: Any,
        species: Any,
        params: dict[str, Any] | None = None,
        box: Any = None,
        neighbor_list: Any = None,
    ) -> Any:
        import jax
        import jax.numpy as jnp

        pos = jnp.asarray(positions, dtype=jnp.float32)

        def _e(rpos):
            return self.compute_total_energy(rpos, species, params, box, neighbor_list)

        return -jax.grad(_e)(pos)

    def compute_energy_and_forces(
        self,
        positions: Any,
        species: Any,
        params: dict[str, Any] | None = None,
        box: Any = None,
        neighbor_list: Any = None,
    ) -> tuple[Any, Any]:
        e = self.compute_total_energy(positions, species, params, box, neighbor_list)
        f = self.compute_forces(positions, species, params, box, neighbor_list)
        return e, f


def build_classical_h2_handle(species_list: Sequence[str] | None = None) -> ClassicalH2MorseHandle:
    species = list(species_list or ["H"])
    model = ClassicalH2MorseModel(species_list=species)
    params = model.get_parameters()
    return ClassicalH2MorseHandle(model=model, params=params, species_list=species)


def train_classical_h2_on_qmef(
    handle: ClassicalH2MorseHandle,
    dataset: QMEFDataset,
) -> ClassicalH2MorseHandle:
    """Fit Morse parameters to QMEF frames (Hartree/Bohr → eV/Å internally)."""
    if not dataset.frames:
        raise ValueError("dataset must contain at least one frame")

    rs: list[float] = []
    es: list[float] = []
    for fr in dataset.frames:
        if len(fr.atomic_numbers) != 2:
            continue
        rs.append(_bond_length_ang(np.asarray(fr.positions_bohr)))
        es.append(float(fr.energy_hartree) * _HARTREE_TO_EV)

    if len(rs) < 2:
        raise ValueError("need at least 2 diatomic frames to fit Morse parameters")

    r_arr = np.asarray(rs, dtype=np.float64)
    e_arr = np.asarray(es, dtype=np.float64)

    def _predict(x: np.ndarray, r: np.ndarray) -> np.ndarray:
        de, a, re, shift = float(x[0]), float(x[1]), float(x[2]), float(x[3])
        return de * (1.0 - np.exp(-a * (r - re))) ** 2 - de + shift

    def _residuals(x: np.ndarray) -> np.ndarray:
        de, a, re = float(x[0]), float(x[1]), float(x[2])
        if de <= 0 or a <= 0 or re <= 0:
            return np.full_like(e_arr, 1e6)
        return _predict(x, r_arr) - e_arr

    x0 = np.array([4.5, 1.93, 0.74, float(np.min(e_arr))], dtype=np.float64)
    try:
        from scipy.optimize import least_squares

        res = least_squares(
            _residuals,
            x0,
            bounds=([1e-4, 0.05, 0.3, -500.0], [50.0, 10.0, 3.0, 50.0]),
        )
        de, a, re, shift = [float(v) for v in res.x]
    except ImportError:
        de, a, re, shift = x0.tolist()

    fitted = ClassicalH2MorseParams(de_ev=de, a_inv_ang=a, re_ang=re, shift_ev=shift)
    handle.model.set_parameters(fitted.as_dict())
    handle.params = handle.model.get_parameters()

    pred = ClassicalH2MorseModel._morse_energy_ev(r_arr, fitted)
    mae = float(np.mean(np.abs(pred - e_arr)))
    rmse = float(np.sqrt(np.mean((pred - e_arr) ** 2)))
    handle.train_meta = {
        "backend": "classical_h2",
        "n_train_frames": len(rs),
        "final_metrics": {
            "energy_mae": mae,
            "energy_rmse": rmse,
            "de_ev": de,
            "a_inv_ang": a,
            "re_ang": re,
            "shift_ev": shift,
        },
    }
    return handle
