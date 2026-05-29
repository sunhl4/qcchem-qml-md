"""Hard-core boson (paired-electron) fermion-to-qubit mapping for spatial MO models."""

from __future__ import annotations

import numpy as np
from openfermion import BosonOperator
from openfermion.ops import QubitOperator


def _boson_ladder(qubit: int, *, dagger: bool) -> QubitOperator:
    """Single-mode boson ladder operator mapped to one qubit (JW-like, no trailing strings)."""
    sign = -1.0 if dagger else 1.0
    return 0.5 * QubitOperator(f"X{qubit}") + 0.5j * sign * QubitOperator(f"Y{qubit}")


def hard_core_boson_from_spatial(
    constant: float,
    h1: np.ndarray,
    h2: np.ndarray,
) -> BosonOperator:
    """Build a hard-core bosonic Hamiltonian from spatial MO integrals."""
    one_e = np.asarray(h1, dtype=float)
    two_e = np.asarray(h2, dtype=float) * 2.0
    n_modes = int(one_e.shape[0])
    boson = BosonOperator((), float(constant))

    for i in range(n_modes):
        diag = 2.0 * one_e[i, i] + two_e[i, i, i, i]
        boson += BosonOperator(f"{i}^ {i}", float(diag))

    for i in range(n_modes):
        for j in range(n_modes):
            if i == j:
                continue
            boson += BosonOperator(f"{i}^ {j}", float(two_e[i, i, j, j]))
            pair = 2.0 * two_e[i, j, j, i] - two_e[i, j, i, j]
            boson += BosonOperator(f"{i}^ {i} {j}^ {j}", float(pair))
    return boson


def boson_to_qubit_mapping(bos_op: BosonOperator) -> QubitOperator:
    """Map a bosonic operator to qubits."""
    mapped = QubitOperator((), bos_op.constant)
    for term, coeff in bos_op.terms.items():
        if not term:
            continue
        piece = QubitOperator((), complex(coeff))
        for mode, is_dagger in term:
            piece *= _boson_ladder(int(mode), dagger=bool(is_dagger))
        mapped += piece
    return mapped


def hard_core_boson_qubit_hamiltonian(
    constant: float,
    h1: np.ndarray,
    h2: np.ndarray,
) -> QubitOperator:
    """Spatial integrals → qubit Hamiltonian under hard-core boson encoding."""
    return boson_to_qubit_mapping(hard_core_boson_from_spatial(constant, h1, h2))


def hcb_reference_statevector(*, n_spin_orbitals: int, n_electrons: int) -> np.ndarray:
    """Hartree–Fock reference in the HCB register (``n_qubits = n_spin_orbitals // 2``)."""
    n_modes = int(n_spin_orbitals) // 2
    n_pairs = int(n_electrons) // 2
    if n_pairs > n_modes:
        raise ValueError("HCB reference: n_electrons exceeds active spatial capacity.")
    dim = 2**n_modes
    psi = np.zeros(dim, dtype=np.complex128)
    psi[(2**n_pairs) - 1] = 1.0
    return psi


def hcb_n_qubits(n_spin_orbitals: int) -> int:
    return int(np.ceil(int(n_spin_orbitals) / 2))


__all__ = [
    "boson_to_qubit_mapping",
    "hard_core_boson_from_spatial",
    "hard_core_boson_qubit_hamiltonian",
    "hcb_n_qubits",
    "hcb_reference_statevector",
]
