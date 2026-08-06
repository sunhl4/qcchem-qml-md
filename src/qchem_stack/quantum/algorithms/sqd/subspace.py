"""Configuration recovery (S-CORE-lite) and subspace diagonalization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.linalg import eigh

from qchem_stack.quantum.algorithms.sqd.sampling import hf_bitstring, popcount
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


def recover_configurations(
    bitstrings: np.ndarray,
    *,
    n_qubits: int,
    n_electrons: int | None,
    occupancy: np.ndarray | None = None,
) -> np.ndarray:
    """Map particle-number-violating bitstrings toward a reference occupancy (S-CORE-lite).

    Epistemic bound: full IBM S-CORE uses soft ReLU weights over orbital occupancy
    profiles from batch eigenstates. Here we flip the bit farthest from the occupancy
    (or HF) profile until ``popcount == n_electrons``.
    """
    if n_electrons is None:
        return np.asarray(bitstrings, dtype=int)
    ne = int(n_electrons)
    if occupancy is None:
        hf = hf_bitstring(n_qubits, ne)
        occ = np.array([(hf >> (n_qubits - 1 - q)) & 1 for q in range(n_qubits)], dtype=float)
    else:
        occ = np.asarray(occupancy, dtype=float).ravel()
        if occ.size != n_qubits:
            raise ValueError("occupancy length must equal n_qubits")

    out: list[int] = []
    for raw in bitstrings:
        b = int(raw)
        bits = [(b >> (n_qubits - 1 - q)) & 1 for q in range(n_qubits)]
        while popcount(b) > ne:
            # flip occupied bit with lowest occupancy preference
            cands = [q for q, bit in enumerate(bits) if bit == 1]
            q_flip = min(cands, key=lambda q: float(occ[q]))
            bits[q_flip] = 0
            b ^= 1 << (n_qubits - 1 - q_flip)
        while popcount(b) < ne:
            cands = [q for q, bit in enumerate(bits) if bit == 0]
            q_flip = max(cands, key=lambda q: float(occ[q]))
            bits[q_flip] = 1
            b ^= 1 << (n_qubits - 1 - q_flip)
        out.append(b)
    return np.asarray(out, dtype=int)


def subspace_hamiltonian_matrix(
    hamiltonian: QubitOperator,
    n_qubits: int,
    basis_indices: list[int],
) -> np.ndarray:
    """Dense H restricted to computational-basis indices (orthonormal)."""
    h = qubit_operator_to_sparse(hamiltonian, n_qubits)
    idxs = np.asarray(basis_indices, dtype=int)
    return np.asarray(h[np.ix_(idxs, idxs)], dtype=np.complex128)


def diagonalize_subspace(
    hamiltonian: QubitOperator,
    n_qubits: int,
    basis_indices: list[int],
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return (E0, eigenvector in subspace, orbital occupancy estimate)."""
    if not basis_indices:
        raise ValueError("empty subspace")
    mats = subspace_hamiltonian_matrix(hamiltonian, n_qubits, basis_indices)
    evals, evecs = eigh(mats)
    e0 = float(np.real(evals[0]))
    c = np.asarray(evecs[:, 0], dtype=np.complex128)
    # orbital occupancy from CI vector
    occ = np.zeros(n_qubits, dtype=float)
    probs = np.abs(c) ** 2
    for amp2, idx in zip(probs, basis_indices, strict=True):
        for q in range(n_qubits):
            if (int(idx) >> (n_qubits - 1 - q)) & 1:
                occ[q] += float(amp2)
    return e0, c, occ


def cbs_energy_estimate(
    state: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
    *,
    top_r: int,
) -> tuple[float, list[int]]:
    """CBS-style truncated computational-basis expectation of H (diagonal-dominant path).

    Epistemic bound: full Kohda CBS reconstructs off-diagonal interference via
    auxiliary circuits. This dense implementation uses exact amplitudes on the
    top-R support (valid for simulator; still demonstrates CB concentration).
    """
    psi = np.asarray(state, dtype=np.complex128).ravel()
    probs = np.abs(psi) ** 2
    order = np.argsort(probs)[::-1][: max(1, int(top_r))]
    support = [int(i) for i in order if probs[int(i)] > 0.0]
    if not support:
        support = [0]
    h_sub = subspace_hamiltonian_matrix(hamiltonian, n_qubits, support)
    # Reconstruct truncated state on support
    amps = psi[np.asarray(support)]
    nrm = float(np.linalg.norm(amps))
    if nrm <= 0.0:
        return 0.0, support
    amps = amps / nrm
    e = float(np.real(np.vdot(amps, h_sub @ amps)))
    return e, support
