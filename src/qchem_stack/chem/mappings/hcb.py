"""Hard-core boson (paired-electron) fermion-to-qubit mapping for spatial MO models."""

from __future__ import annotations

from functools import lru_cache

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
    """Build a hard-core bosonic Hamiltonian from spatial MO integrals.

    Maps a fermionic Hamiltonian in spatial orbital basis to hard-core bosons,
    where each spatial orbital represents a pair of electrons (spin-up and spin-down).
    The mapping is exact for closed-shell systems with strong pairing.

    Args:
        constant: Constant energy shift (e.g., nuclear repulsion, core energy).
        h1: One-electron integrals in spatial MO basis, shape (n, n).
            Should be the spatial part of the Fock matrix or core Hamiltonian.
        h2: Two-electron integrals in spatial MO basis, shape (n, n, n, n).
            **Convention**: Chemist's notation (pq|rs) = <pr|qs>, where the integral is:
            integral phi_p(r1) phi_r(r1) (1/r12) phi_q(r2) phi_s(r2) dr1 dr2
            These should be spatial integrals (not spin-orbital integrals).
            The factor of 2.0 applied internally accounts for spin degeneracy in
            closed-shell systems (both alpha-alpha and beta-beta contributions).

    Returns:
        BosonOperator: Hard-core boson Hamiltonian. The bosonic creation/annihilation
        operators b_i, b_i create/destroy electron pairs on spatial orbital i.

    Notes:
        The resulting Hamiltonian has the form:
        H = constant + sum_i eps_i b_i b_i + sum_{i!=j} t_{ij} b_i b_j
            + sum_{i!=j} V_{ij} b_i b_i b_j b_j

        where:
        - eps_i = 2*h1[i,i] + 2*(ii|ii) (diagonal energy with spin factor)
        - t_{ij} = 2*(ii|jj) (pair hopping, Coulomb-like)
        - V_{ij} = 4*(ij|ji) - 2*(ij|ij) (density-density, exchange-dominated)

        The factors of 2 arise from spin summation (alpha-alpha + beta-beta for
        diagonal terms, alpha-alpha + beta-beta + alpha-beta + beta-alpha for
        off-diagonal terms).

    Example:
        >>> import numpy as np
        >>> h1 = np.array([[-1.0, 0.1], [0.1, -0.8]])
        >>> h2 = np.zeros((2, 2, 2, 2))
        >>> h2[0, 0, 0, 0] = 0.5  # (00|00)
        >>> h2[1, 1, 1, 1] = 0.4  # (11|11)
        >>> h2[0, 0, 1, 1] = 0.3  # (00|11)
        >>> h2[0, 1, 1, 0] = 0.2  # (01|10)
        >>> h2[0, 1, 0, 1] = 0.15 # (01|01)
        >>> boson_op = hard_core_boson_from_spatial(0.0, h1, h2)
    """
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
        piece = QubitOperator((), complex(coeff))  # type: ignore[arg-type]
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


@lru_cache(maxsize=128)
def hcb_n_qubits(n_spin_orbitals: int) -> int:
    return int(np.ceil(int(n_spin_orbitals) / 2))


__all__ = [
    "boson_to_qubit_mapping",
    "hard_core_boson_from_spatial",
    "hard_core_boson_qubit_hamiltonian",
    "hcb_n_qubits",
    "hcb_reference_statevector",
]
