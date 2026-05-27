"""Tests for classical H2 Morse force field (no qmlff required)."""

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


def _synthetic_h2_dataset() -> QMEFDataset:
    frames: list[QMFrame] = []
    p = ClassicalH2MorseParams(de_ev=4.5, a_inv_ang=2.0, re_ang=0.74, shift_ev=-30.0)
    model = build_classical_h2_handle(["H"]).model
    for r_bohr in np.linspace(0.9, 2.0, 8):
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


def test_classical_h2_morse_fit_reduces_error() -> None:
    dataset = _synthetic_h2_dataset()
    handle = build_classical_h2_handle(["H"])
    handle = train_classical_h2_on_qmef(handle, dataset)
    mae = handle.train_meta["final_metrics"]["energy_mae"]
    assert mae < 0.5
