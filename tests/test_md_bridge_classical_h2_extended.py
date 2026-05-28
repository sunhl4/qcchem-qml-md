"""Extended Morse H2 classical force-field validation."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.md_bridge.classical_h2_ff import (
    ClassicalH2MorseParams,
    build_classical_h2_handle,
    train_classical_h2_on_qmef,
)
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

pytestmark = pytest.mark.l1_md_ml


def _extended_h2_dataset(n: int = 12) -> QMEFDataset:
    frames: list[QMFrame] = []
    p = ClassicalH2MorseParams(de_ev=4.7, a_inv_ang=2.1, re_ang=0.74, shift_ev=-31.0)
    model = build_classical_h2_handle(["H"]).model
    for r_bohr in np.linspace(0.8, 2.2, n):
        pos = [[0.0, 0.0, 0.0], [0.0, 0.0, float(r_bohr)]]
        r_ang = r_bohr * 0.529177210903
        e_ev = float(model._morse_energy_ev(np.array(r_ang), p))
        e_ha = e_ev / 27.211386245988
        frames.append(
            QMFrame(
                atomic_numbers=[1, 1],
                positions_bohr=pos,
                energy_hartree=e_ha,
                forces_hartree_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            )
        )
    return QMEFDataset(frames=frames)


def test_morse_fit_on_extended_grid() -> None:
    dataset = _extended_h2_dataset()
    handle = build_classical_h2_handle(["H"])
    handle = train_classical_h2_on_qmef(handle, dataset)
    mae = handle.train_meta["final_metrics"]["energy_mae"]
    assert mae < 0.25


def test_morse_params_energy_monotone_at_equilibrium() -> None:
    p = ClassicalH2MorseParams()
    model = build_classical_h2_handle(["H"]).model
    e_re = float(model._morse_energy_ev(np.array(p.re_ang), p))
    e_far = float(model._morse_energy_ev(np.array(p.re_ang + 2.0), p))
    assert e_re < e_far
