"""Unit tests for Psi4 fallback CASCI effective blocks math."""

from __future__ import annotations

import numpy as np

from qchem_stack.chem.integrals.psi4_active_space import _casci_effective_blocks_from_mo_integrals


def test_casci_effective_blocks_no_core_is_identity_projection() -> None:
    h_mo = np.asarray([[1.2, 0.1], [0.1, 0.8]], dtype=float)
    eri = np.zeros((2, 2, 2, 2), dtype=float)
    eri[0, 0, 1, 1] = 0.3
    eri[1, 1, 0, 0] = 0.3
    enuc = 0.7

    constant, h1, h2, _route = _casci_effective_blocks_from_mo_integrals(
        h_core_mo=h_mo,
        eri_mo_chemist=eri,
        enuc=enuc,
        n_core_pairs=0,
        active_start=0,
        n_active_orbitals=2,
    )

    assert constant == enuc
    assert np.allclose(h1, h_mo)
    assert np.allclose(h2, eri)


def test_casci_effective_blocks_adds_core_energy_and_core_shift() -> None:
    # One frozen doubly occupied core orbital (0), one active orbital (1).
    h_mo = np.asarray([[1.2, 0.0], [0.0, 0.3]], dtype=float)
    eri = np.zeros((2, 2, 2, 2), dtype=float)
    eri[0, 0, 0, 0] = 0.7  # (ii|jj) and (ij|ji) with i=j=0
    eri[1, 1, 0, 0] = 0.4  # (uv|ii) with u=v=1,i=0
    eri[1, 0, 0, 1] = 0.1  # (ui|iv) with u=v=1,i=0
    enuc = 0.5

    constant, h1, h2, _route = _casci_effective_blocks_from_mo_integrals(
        h_core_mo=h_mo,
        eri_mo_chemist=eri,
        enuc=enuc,
        n_core_pairs=1,
        active_start=1,
        n_active_orbitals=1,
    )

    # E_core = Enuc + 2*h_ii + 2*(ii|jj) - (ij|ji) with i=j=0.
    assert constant == 0.5 + 2.0 * 1.2 + 2.0 * 0.7 - 0.7
    # h_eff = h + 2*(uv|ii) - (ui|iv).
    assert np.allclose(h1, np.asarray([[0.3 + 2.0 * 0.4 - 0.1]], dtype=float))
    assert np.allclose(h2, np.asarray([[[[0.0]]]], dtype=float))
