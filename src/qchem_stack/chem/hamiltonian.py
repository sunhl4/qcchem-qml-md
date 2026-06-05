"""Qubit Hamiltonian build facade (chem layer; do not import orchestration).

Implementation is split across ``hamiltonian_meta``, ``hamiltonian_mapping``, and
``hamiltonian_build``; this module re-exports the public API for backward compatibility.
"""

from __future__ import annotations

from .hamiltonian_build import (
    QubitHamiltonian,
    fermionic_active_space_interaction_operator_from_canonical_pack,
    fermionic_active_space_interaction_operator_from_classical_reference,
    molecular_hamiltonian_from_canonical_active_space_pack,
    qubit_hamiltonian_from_active_space_fermionic_operator,
    qubit_hamiltonian_from_compact_restricted_active_space,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from .hamiltonian_meta import (
    FermionQubitMappingName,
    hamiltonian_fingerprint_from_qubit_operator,
)

__all__ = [
    "FermionQubitMappingName",
    "QubitHamiltonian",
    "fermionic_active_space_interaction_operator_from_canonical_pack",
    "fermionic_active_space_interaction_operator_from_classical_reference",
    "hamiltonian_fingerprint_from_qubit_operator",
    "molecular_hamiltonian_from_canonical_active_space_pack",
    "qubit_hamiltonian_from_active_space_fermionic_operator",
    "qubit_hamiltonian_from_compact_restricted_active_space",
    "qubit_hamiltonian_from_spatial_chemist_integrals",
]
