"""QSE degenerate eigenvalue handling."""

from __future__ import annotations

import numpy as np

from qchem_stack.quantum.qse_transition import solve_qse_ghep


def test_qse_ghep_degenerate_subspace_gives_zero_excitations() -> None:
    h = np.eye(3)
    s = np.eye(3)
    evals, exc = solve_qse_ghep(h, s)
    assert len(exc) == 2
    assert exc[0] == 0.0
    assert exc[1] == 0.0
    assert np.allclose(evals, 1.0)


def test_qse_ghep_two_level_z_model() -> None:
    h = np.diag([0.0, 0.7])
    s = np.eye(2)
    _, exc = solve_qse_ghep(h, s)
    assert exc == [0.7]
