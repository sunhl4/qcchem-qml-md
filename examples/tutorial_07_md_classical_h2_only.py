#!/usr/bin/env python3
"""Classical H2 Morse MD smoke — no QML-FF dependency."""

from __future__ import annotations

import numpy as np

from qchem_stack.md_bridge.classical_h2_ff import ClassicalH2MorseModel


def main() -> None:
    model = ClassicalH2MorseModel()
    pos = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float)
    species = np.array([0, 0], dtype=np.int32)
    e, f = model.compute_energy_and_forces(pos, species)
    assert np.isfinite(float(e))
    assert np.asarray(f).shape == (2, 3)
    print("classical_h2 energy_ev", float(e), "forces_shape", np.asarray(f).shape)


if __name__ == "__main__":
    main()
