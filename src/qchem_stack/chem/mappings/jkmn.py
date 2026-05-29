"""JKMN fermion-to-qubit mapping via ternary-tree Majorana encodings (arXiv:1910.10746)."""

from __future__ import annotations

import math

import numpy as np
from openfermion.ops import QubitOperator
from openfermion.transforms.opconversions.conversions import get_majorana_operator

_PAULI_BY_DIGIT = ("X", "Y", "Z")


def _tree_height(n_qubits: int) -> int:
    return int(math.log(2 * n_qubits + 1, 3))


def _node_index(path: str, depth: int) -> int:
    index = (3**depth - 1) // 2
    for j in range(depth):
        index += int(path[j]) * 3 ** (depth - 1 - j)
    return index


def _leaf_pauli_strings(height: int) -> list[list[tuple[int, str]]]:
    strings: list[list[tuple[int, str]]] = []
    for value in range(3**height):
        digits: list[str] = []
        v = value
        for _ in range(height):
            digits.append(str(v % 3))
            v //= 3
        terstring = "".join(reversed(digits))
        strings.append(
            [
                (_node_index(terstring, ch), _PAULI_BY_DIGIT[int(terstring[ch])])
                for ch in range(height)
            ]
        )
    return strings


def _expand_majorana_map(n_qubits: int) -> dict[int, QubitOperator]:
    height = _tree_height(n_qubits)
    leaves = _leaf_pauli_strings(height)
    internal_nodes = (3**height - 1) // 2
    n_extra_leaves = n_qubits - internal_nodes

    expanded: list[list[tuple[int, str]]] = []
    for leaf_idx in range(n_extra_leaves):
        base = leaves.pop(0)
        anchor = internal_nodes + leaf_idx
        for digit in range(3):
            expanded.append(base + [(anchor, _PAULI_BY_DIGIT[digit])])
    expanded.extend(leaves)

    raw_map = {idx: QubitOperator(terms) for idx, terms in enumerate(expanded[:-1])}
    return _rotate_vacuum_majorana(raw_map, n_qubits)


def _rotate_vacuum_majorana(
    raw_map: dict[int, QubitOperator], n_qubits: int
) -> dict[int, QubitOperator]:
    """Apply the JKMN vacuum rotation (X ↔ Z on selected qubits)."""
    vacuum_pauli: dict[int, str] = {}
    for mode in range(n_qubits):
        fock = 0.5 * QubitOperator(()) - 0.5j * raw_map[2 * mode] * raw_map[2 * mode + 1]
        for term in fock.terms:
            for qubit, pauli in term:
                vacuum_pauli.setdefault(int(qubit), pauli)
    flip_qubits = {q for q, p in vacuum_pauli.items() if p == "X"}

    rotated: dict[int, QubitOperator] = {}
    for idx, op in raw_map.items():
        transformed: list[tuple[int, str]] = []
        for term in op.terms:
            for qubit, pauli in term:
                if qubit in flip_qubits and pauli in ("X", "Z"):
                    transformed.append((qubit, "Z" if pauli == "X" else "X"))
                else:
                    transformed.append((qubit, pauli))
        rotated[idx] = QubitOperator(transformed)

    compact: dict[int, QubitOperator] = {}
    for mode in range(n_qubits):
        q1 = next(iter(rotated[2 * mode].terms))
        q2 = next(iter(rotated[2 * mode + 1].terms))
        q2_set = set(q2)
        for qubit, pauli in q1:
            if pauli == "X" and (qubit, "Y") in q2_set:
                compact[2 * qubit] = rotated[2 * mode]
                compact[2 * qubit + 1] = rotated[2 * mode + 1]
            elif pauli == "Y" and (qubit, "X") in q2_set:
                compact[2 * qubit] = -rotated[2 * mode]
                compact[2 * qubit + 1] = rotated[2 * mode + 1]
    return compact


def jkmn(fermion_operator: object, *, n_qubits: int) -> QubitOperator:
    """Map a fermionic operator to qubits with the JKMN encoding."""
    majorana = get_majorana_operator(fermion_operator)
    encoding = _expand_majorana_map(int(n_qubits))
    mapped = QubitOperator()
    atol = 1.0e-12
    for term, coeff in majorana.terms.items():
        if abs(coeff) <= atol:
            continue
        piece = QubitOperator((), coeff)
        for majorana_idx in term:
            piece *= encoding[majorana_idx]
        mapped += piece
    mapped.compress()
    return mapped


def jkmn_prep_vector(occupation: list[int] | np.ndarray) -> np.ndarray:
    """Return computational-basis occupation bits for a spin-orbital vector under JKMN."""
    occ = np.asarray(occupation, dtype=int).ravel()
    n_qubits = int(occ.size)
    encoding = _expand_majorana_map(n_qubits)
    state_op = QubitOperator((), 1.0)
    for orbital, filled in enumerate(occ):
        if filled == 1:
            state_op *= encoding[2 * orbital]
    bits = np.zeros(n_qubits, dtype=int)
    for term in state_op.terms:
        for qubit, pauli in term:
            bits[int(qubit)] = 1 if pauli in ("X", "Y") else 0
    return bits


def jkmn_reference_statevector(*, n_spin_orbitals: int, n_electrons: int) -> np.ndarray:
    """Hartree–Fock reference statevector under JKMN."""
    occ = np.zeros(int(n_spin_orbitals), dtype=int)
    occ[: int(n_electrons)] = 1
    x_bits = jkmn_prep_vector(occ)
    dim = 2 ** int(n_spin_orbitals)
    psi = np.zeros(dim, dtype=np.complex128)
    psi[int(sum(int(b) << q for q, b in enumerate(x_bits)))] = 1.0
    return psi


__all__ = ["jkmn", "jkmn_prep_vector", "jkmn_reference_statevector"]
