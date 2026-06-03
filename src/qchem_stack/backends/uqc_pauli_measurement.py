"""Compatibility shim for UQC Pauli measurement helpers."""

from qchem_stack_uqc.uqc_pauli_measurement import (
    _bitstring_to_parity,
    _evaluate_pauli_term_from_counts,
    compute_hamiltonian_expectation_from_counts,
)

__all__ = [
    "_bitstring_to_parity",
    "_evaluate_pauli_term_from_counts",
    "compute_hamiltonian_expectation_from_counts",
]
