"""
Compute Hamiltonian expectation values from UQC measurement counts.

UQC returns bit-string measurement histograms. This module evaluates
``<H>`` from those counts using Pauli-term decomposition.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


def _bitstring_to_parity(bitstring: str, qubit_indices: list[int]) -> int:
    """Compute parity of selected qubits in a bit-string.

    Returns +1 for even parity, -1 for odd parity.
    """
    parity = 0
    for q in qubit_indices:
        if q < len(bitstring):
            parity ^= int(bitstring[q])
    return 1 - 2 * parity


def _evaluate_pauli_term_from_counts(
    counts: dict[str, int],
    term_qubits: list[int],
    n_qubits: int,
) -> float:
    """Evaluate a single Pauli-Z-basis term from measurement counts.

    For a general Pauli term, the circuit must be basis-rotated before measurement.
    This function assumes the circuit has already been rotated to the Z basis for
    the specific Pauli string.
    """
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0

    expectation = 0.0
    for bitstring, count in counts.items():
        bitstring_clean = bitstring.replace(" ", "")
        parity = _bitstring_to_parity(bitstring_clean, term_qubits)
        expectation += parity * count

    return expectation / total_shots


def _group_pauli_terms_by_basis(
    hamiltonian: QubitOperator, n_qubits: int
) -> dict[str, list[tuple[list[int], complex]]]:
    """Group Pauli terms by measurement basis rotation.

    Returns dict mapping basis key -> list of (qubit_indices, coefficient).
    Basis key is a string like 'ZZII', 'XYIZ', etc.
    """
    groups: dict[str, list[tuple[list[int], complex]]] = {}

    for term, coeff in hamiltonian.terms.items():
        if not term:
            # Identity term
            key = "I" * n_qubits
            if key not in groups:
                groups[key] = []
            groups[key].append(([], complex(coeff)))
            continue

        chars = ["I"] * n_qubits
        qubits = []
        for idx, pauli in term:
            if idx < n_qubits:
                chars[idx] = pauli
                qubits.append(idx)
        key = "".join(chars)
        if key not in groups:
            groups[key] = []
        groups[key].append((qubits, complex(coeff)))

    return groups


def compute_hamiltonian_expectation_from_counts(
    counts: dict[str, int],
    hamiltonian: QubitOperator,
    n_qubits: int,
) -> float:
    """Compute Hamiltonian expectation value from measurement counts.

    This assumes the measurement counts come from circuits that have been
    basis-rotated to measure each Pauli term group. For a full implementation,
    separate counts per basis group would be needed.

    For single-group Z-basis measurements (or when all terms are Z-type),
    this computes the expectation directly. For mixed Pauli bases, this
    provides an approximation assuming Z-basis rotation was applied.

    Args:
        counts: Measurement histogram {bitstring: count}.
        hamiltonian: QubitOperator Hamiltonian.
        n_qubits: Number of qubits.

    Returns:
        Expectation value <H>.
    """
    groups = _group_pauli_terms_by_basis(hamiltonian, n_qubits)
    total_expectation = 0.0

    for _basis_key, terms in groups.items():
        for qubit_indices, coeff in terms:
            if not qubit_indices:
                # Identity term
                total_expectation += float(np.real(coeff))
                continue

            term_exp = _evaluate_pauli_term_from_counts(counts, qubit_indices, n_qubits)
            total_expectation += float(np.real(coeff)) * term_exp

    return total_expectation
