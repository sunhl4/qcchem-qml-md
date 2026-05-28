"""Bit manipulation utilities for quantum circuit backends."""

from __future__ import annotations


def bit_reverse_index(value: int, n_qubits: int) -> int:
    """Reverse the bit order of an integer value with n_qubits width.

    This is used to convert between Qiskit's little-endian qubit ordering
    and the standard big-endian representation.

    Args:
        value: Integer value to reverse bits for
        n_qubits: Number of qubits (bit width)

    Returns:
        Integer with reversed bit order

    Example:
        >>> bit_reverse_index(0b001, 3)
        4  # 0b100
        >>> bit_reverse_index(0b110, 3)
        3  # 0b011
    """
    result = 0
    for i in range(n_qubits):
        if value & (1 << i):
            result |= 1 << (n_qubits - 1 - i)
    return result
