"""Documented fermion→qubit transforms (config + OpenFermion wiring).

See :attr:`qchem_stack.config.ActiveSpaceSpec.fermion_qubit_mapping` and :mod:`qchem_stack.chem.hamiltonian`.

Research distributions such as **Tangelo** additionally advertise JKMN / generalized mappings in tutorials.
Those identifiers remain **out-of-scope** for execution until each mapping gets explicit OpenFermion plumbing,
parity fixtures, and documentation parity rows (:data:`DOCUMENTED_FERMION_QUBIT_MAPPINGS` is the whitelist).
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
