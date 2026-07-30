"""Pauli-term features for GQE coefficient re-weighting (Nakaji et al.).

Store ``q_a(j) = <P_a>`` once per circuit sequence; transfer to a new geometry by
recombining with that geometry's coefficients ``h_a(Δ')``:

    E(Δ', j) = Σ_a h_a(Δ') q_a(j)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


@dataclass(frozen=True)
class PauliTermBasis:
    """Shared Pauli string basis (identity omitted from features; kept as constant)."""

    terms: tuple[tuple[tuple[int, str], ...], ...]
    """Each term is a tuple of ``(qubit, Pauli)`` pairs (OpenFermion term key)."""
    labels: tuple[str, ...]

    @property
    def n_terms(self) -> int:
        return len(self.terms)


def _term_label(term: tuple[tuple[int, str], ...]) -> str:
    if not term:
        return "I"
    return " ".join(f"{p}{q}" for q, p in term)


def pauli_basis_from_hamiltonian(hamiltonian: QubitOperator) -> PauliTermBasis:
    """Collect non-identity Pauli strings appearing in ``hamiltonian`` (stable order)."""
    keys: list[tuple[tuple[int, str], ...]] = []
    for term in hamiltonian.terms:
        t = tuple(term)
        if len(t) == 0:
            continue
        keys.append(t)
    keys = sorted(set(keys), key=_term_label)
    return PauliTermBasis(terms=tuple(keys), labels=tuple(_term_label(t) for t in keys))


def hamiltonian_coefficients(
    hamiltonian: QubitOperator,
    basis: PauliTermBasis,
) -> tuple[float, np.ndarray]:
    """Return ``(identity_coeff, h_a)`` aligned with ``basis``."""
    const = float(np.real(hamiltonian.terms.get((), 0.0)))
    h = np.zeros(basis.n_terms, dtype=np.float64)
    for i, term in enumerate(basis.terms):
        h[i] = float(np.real(hamiltonian.terms.get(term, 0.0)))
    return const, h


def pauli_expectations(
    state: np.ndarray,
    basis: PauliTermBasis,
    *,
    n_qubits: int,
) -> np.ndarray:
    """Compute ``q_a = Re <ψ|P_a|ψ>`` for each basis Pauli."""
    from openfermion.ops import QubitOperator

    st = np.asarray(state, dtype=np.complex128).ravel()
    q = np.zeros(basis.n_terms, dtype=np.float64)
    for i, term in enumerate(basis.terms):
        op = QubitOperator(term, 1.0)
        mat = qubit_operator_to_sparse(op, n_qubits)
        q[i] = float(np.real(np.vdot(st, mat @ st)))
    return q


def energy_from_pauli_features(
    *,
    identity_coeff: float,
    h_coeffs: np.ndarray,
    q_expect: np.ndarray,
) -> float:
    """``E = h_I + Σ_a h_a q_a``."""
    return float(
        identity_coeff
        + np.dot(np.asarray(h_coeffs, dtype=float), np.asarray(q_expect, dtype=float))
    )


def reweight_dataset_energies(
    records: list[dict[str, Any]],
    *,
    identity_coeff: float,
    h_coeffs: np.ndarray,
) -> list[dict[str, Any]]:
    """Rewrite ``labels.energy_hartree`` via stored Pauli features (config-to-config transfer)."""
    out: list[dict[str, Any]] = []
    h = np.asarray(h_coeffs, dtype=float)
    for rec in records:
        feats = rec.get("pauli_features")
        if not feats or "q" not in feats:
            raise ValueError("oracle record missing pauli_features.q for reweighting")
        q = np.asarray(feats["q"], dtype=float)
        if q.shape != h.shape:
            raise ValueError(f"q shape {q.shape} != h shape {h.shape}")
        e = energy_from_pauli_features(identity_coeff=identity_coeff, h_coeffs=h, q_expect=q)
        new = dict(rec)
        labels = dict(rec.get("labels") or {})
        labels["energy_hartree"] = e
        labels["energy_unit"] = "hartree"
        labels["reweighted"] = True
        new["labels"] = labels
        out.append(new)
    return out


def dataset_from_oracle_records(records: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    """Extract ``(tokens[B,T], energies[B])`` for pre-training."""
    if not records:
        raise ValueError("empty dataset")
    seqs = [np.asarray(r["candidate"]["token_sequence"], dtype=np.int32) for r in records]
    lens = {s.shape[0] for s in seqs}
    if len(lens) != 1:
        raise ValueError(f"inconsistent sequence lengths in dataset: {sorted(lens)}")
    toks = np.stack(seqs, axis=0)
    ens = np.asarray([float(r["labels"]["energy_hartree"]) for r in records], dtype=np.float64)
    return toks, ens
