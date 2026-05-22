"""``chem.kernels`` lazy exports for spin-UCC builders."""

from __future__ import annotations

import importlib


def test_chem_kernels_lazy_spin_ucc_exports() -> None:
    kernels = importlib.import_module("qchem_stack.chem.kernels")
    assert callable(kernels.build_spin_uccsd_fermion_generators)
    assert callable(kernels.count_uccsd_excitations)
    gens = kernels.build_spin_uccsd_fermion_generators(4, 2)
    assert len(gens) >= 1
