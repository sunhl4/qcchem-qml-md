"""Fermionic slice sizes (singles / doubles) vs UCCSD excitation counts."""

from __future__ import annotations

from qchem_stack.chem.kernels.spin_ucc import (
    build_spin_ucc_doubles_only_fermion_generators,
    build_spin_ucc_singles_only_fermion_generators,
    build_spin_uccsd_fermion_generators,
    count_uccsd_excitations,
)


def test_singles_doubles_slices_partition_uccsd_spin_orbital_count() -> None:
    n_so, ne = 4, 2
    c = count_uccsd_excitations(n_so, ne)
    s = build_spin_ucc_singles_only_fermion_generators(n_so, ne)
    d = build_spin_ucc_doubles_only_fermion_generators(n_so, ne)
    full = build_spin_uccsd_fermion_generators(n_so, ne)
    assert len(s) == c["n_single_excitations"]
    assert len(d) == c["n_double_excitations"]
    assert len(full) == len(s) + len(d)
