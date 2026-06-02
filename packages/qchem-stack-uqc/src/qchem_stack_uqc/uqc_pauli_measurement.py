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


def _is_z_basis_only(basis_key: str) -> bool:
    """Check if a basis key contains only Z and I operators (no X or Y).
    
    Args:
        basis_key: Pauli string like "ZZII", "XYIZ", etc.
        
    Returns:
        True if basis key contains only Z and I, False if X or Y present.
    """
    return "X" not in basis_key and "Y" not in basis_key


def compute_hamiltonian_expectation_from_counts(
    counts: dict[str, int],
    hamiltonian: QubitOperator,
    n_qubits: int,
) -> float:
    """Compute Hamiltonian expectation value from measurement counts.

    This function evaluates the expectation value using computational-basis
    measurement counts. It only supports Z-type Pauli operators because X/Y
    operators require basis rotation measurements that are not available
    from a single Z-basis measurement.

    For a full implementation supporting all Pauli bases, separate counts
    per basis group would be needed (one measurement circuit per basis).

    Args:
        counts: Measurement histogram {bitstring: count} from Z-basis measurement.
        hamiltonian: QubitOperator Hamiltonian.
        n_qubits: Number of qubits.

    Returns:
        Expectation value <H>.
        
    Raises:
        NotImplementedError: If Hamiltonian contains X or Y Pauli operators.
            These require per-basis measurement circuits (planned for future release).
    """
    groups = _group_pauli_terms_by_basis(hamiltonian, n_qubits)
    
    # Check for unsupported X/Y Pauli operators
    for basis_key in groups.keys():
        if not _is_z_basis_only(basis_key):
            raise NotImplementedError(
                f"X/Y Pauli operators not supported (found basis {basis_key!r}). "
                "Only Z-type operators are currently supported because X/Y require "
                "per-basis measurement circuits. Full X/Y support is planned for "
                "a future release."
            )
    
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
