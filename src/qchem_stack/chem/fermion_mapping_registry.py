"""Documented fermion→qubit transforms (config + OpenFermion wiring).

See :attr:`qchem_stack.config.ActiveSpaceSpec.fermion_qubit_mapping` and :mod:`qchem_stack.chem.hamiltonian`.
"""

from __future__ import annotations

from typing import Final

DOCUMENTED_FERMION_QUBIT_MAPPINGS: Final[tuple[str, ...]] = (
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
)


def list_documented_fermion_qubit_mappings() -> tuple[str, ...]:
    return DOCUMENTED_FERMION_QUBIT_MAPPINGS
