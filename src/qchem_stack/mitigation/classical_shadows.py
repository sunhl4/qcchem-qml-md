"""Minimal classical-shadows Pauli expectation (local random Pauli snapshots).

.. warning:: TOY/STUB IMPLEMENTATION
    This module provides a minimal implementation of classical shadows for
    demonstration and research purposes. It is NOT suitable for production
    quantum computing workloads.

    Limitations:
    - Uses statevector simulation instead of actual quantum measurements
    - No support for derandomization or adaptive measurement strategies
    - Limited to small qubit counts due to statevector memory requirements
    - No integration with hardware-specific noise models
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.backends.pauli_shot_sim import _single_qubit_rot_to_z_matrix
from qchem_stack.quantum.algorithms.tolerances import PROBABILITY_FLOOR
from qchem_stack.quantum.statevector import _apply_one_qubit_unitary

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


def _pauli_string_for_term(term: tuple[tuple[int, str], ...], n_qubits: int) -> list[str]:
    axes = ["I"] * n_qubits
    for idx, p in term:
        axes[int(idx)] = str(p)
    return axes


def _rotate_to_pauli_basis(state: np.ndarray, basis: list[str], n_qubits: int) -> np.ndarray:
    st = np.asarray(state, dtype=complex).reshape(-1)
    for q, axis in enumerate(basis):
        u = _single_qubit_rot_to_z_matrix(axis)
        if np.allclose(u, np.eye(2)):
            continue
        st = _apply_one_qubit_unitary(st, u, q, n_qubits)
    return st


def _sample_z_outcomes(state: np.ndarray, n_qubits: int, rng: np.random.Generator) -> list[int]:
    probs = np.abs(state) ** 2
    probs = probs / max(float(probs.sum()), PROBABILITY_FLOOR)
    idx = int(rng.choice(len(probs), p=probs))
    return [(idx >> q) & 1 for q in range(n_qubits)]


def _snapshot_hamiltonian_value(
    bits: list[int],
    basis: list[str],
    terms: list[tuple[tuple[tuple[int, str], ...], complex]],
    *,
    n_qubits: int,
) -> float:
    total = 0.0
    for term, coeff in terms:
        if not term:
            total += float(np.real(coeff))
            continue
        target = _pauli_string_for_term(term, n_qubits)
        support = [q for q, p in enumerate(target) if p != "I"]
        if not all(basis[q] == target[q] for q in support):
            continue
        prod = 1
        for q in support:
            prod *= 1 if bits[q] == 0 else -1
        total += float(np.real(coeff)) * float((3 ** len(support)) * prod)
    return float(total)


def classical_shadows_hamiltonian_expectation(
    state: np.ndarray,
    hamiltonian: QubitOperator,
    n_qubits: int,
    *,
    budget_pairs: int,
    seed: int,
) -> dict[str, Any]:
    """
    Estimate ⟨H⟩ with local random-Pauli classical shadows (Huang et al. style estimator).

    Uses a fixed ``seed`` for reproducibility; intended for small active spaces in tests.
    Implements median-of-means for robust estimation against outliers.
    """
    rng = np.random.default_rng(int(seed))
    terms = list(hamiltonian.terms.items())
    estimates: list[float] = []
    axes_choices = ("X", "Y", "Z")
    for _ in range(max(1, int(budget_pairs))):
        basis = [axes_choices[int(rng.integers(3))] for _ in range(n_qubits)]
        rotated = _rotate_to_pauli_basis(state, basis, n_qubits)
        bits = _sample_z_outcomes(rotated, n_qubits, rng)
        estimates.append(_snapshot_hamiltonian_value(bits, basis, terms, n_qubits=n_qubits))

    # Median-of-means: split into k batches, compute batch means, take median
    if not estimates:
        expectation = 0.0
    else:
        n_batches = max(1, int(len(estimates) ** 0.5))  # sqrt(n) batches
        batch_size = len(estimates) // n_batches
        if batch_size == 0:
            # Not enough samples for batching, use simple mean
            expectation = float(np.mean(estimates))
        else:
            batch_means = []
            for i in range(n_batches):
                start = i * batch_size
                end = start + batch_size if i < n_batches - 1 else len(estimates)
                batch = estimates[start:end]
                if batch:
                    batch_means.append(float(np.mean(batch)))
            expectation = float(np.median(batch_means)) if batch_means else 0.0

    return {
        "expectation": expectation,
        "budget_pairs": int(budget_pairs),
        "seed": int(seed),
        "n_qubits": int(n_qubits),
        "estimator": "local_random_pauli_classical_shadows_median_of_means_v1",
    }
