"""Bridge GQE token sequences to ``HamiltonianExpectationExecutor``."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import expm

from qchem_stack.contracts.schema_ids import GQE_ORACLE_RECORD_V1
from qchem_stack.integrations.gqe.native.pauli_features import (
    PauliTermBasis,
    hamiltonian_coefficients,
    pauli_basis_from_hamiltonian,
    pauli_expectations,
)
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.integrations.gqe.native.operator_pool import GQEOperatorPool

GQECostFn = Callable[[Sequence[int]], float]


def apply_pool_sequence(
    pool: GQEOperatorPool,
    indices: Sequence[int],
    reference: np.ndarray,
    *,
    angles: Sequence[float] | None = None,
) -> np.ndarray:
    """Apply ``∏_k exp(θ_{j_k} G_{j_k})`` to ``reference`` (dense statevector).

    Generators follow the OpenFermion UCCSD anti-Hermitian convention
    (``U = exp(θ G)``, not ``exp(-i θ P)``).
    """
    st = np.asarray(reference, dtype=np.complex128).ravel().copy()
    if st.size != 2**pool.n_qubits:
        raise ValueError(f"reference length {st.size} incompatible with n_qubits={pool.n_qubits}")
    for step, idx in enumerate(indices):
        j = int(idx)
        if j < 0 or j >= pool.vocab_size:
            raise IndexError(f"token {j} outside pool vocab_size={pool.vocab_size}")
        theta = float(pool.angle_for(j) if angles is None else angles[step])
        if abs(theta) < 1e-15:
            continue
        st = expm(theta * pool.matrices[j]) @ st
    norm = float(np.linalg.norm(st))
    if norm <= 0.0:
        raise ValueError("state collapsed to zero after pool sequence")
    return st / norm


def default_hf_reference(*, n_qubits: int, n_electrons: int | None = None) -> np.ndarray:
    """Jordan–Wigner HF reference; falls back to |0…0⟩ if electron count unknown."""
    if n_electrons is None:
        st = np.zeros(2**n_qubits, dtype=np.complex128)
        st[0] = 1.0
        return st
    return reference_state_dense(
        mapping="jordan_wigner",
        n_spin_orbitals=n_qubits,
        n_electrons=int(n_electrons),
    )


def make_gqe_cost(
    executor: HamiltonianExpectationExecutor,
    hamiltonian: QubitOperator,
    pool: GQEOperatorPool,
    *,
    reference: np.ndarray | None = None,
    n_electrons: int | None = None,
    angles: Sequence[float] | None = None,
) -> GQECostFn:
    """Return ``cost(indices) -> energy`` using the stack executor (Plan B oracle)."""
    ref = (
        np.asarray(reference, dtype=np.complex128).ravel()
        if reference is not None
        else default_hf_reference(n_qubits=pool.n_qubits, n_electrons=n_electrons)
    )

    def cost(indices: Sequence[int]) -> float:
        state = apply_pool_sequence(pool, indices, ref, angles=angles)
        return float(executor.expectation_state(state, hamiltonian, pool.n_qubits))

    return cost


def make_gqe_oracle(
    executor: HamiltonianExpectationExecutor,
    hamiltonian: QubitOperator,
    pool: GQEOperatorPool,
    *,
    reference: np.ndarray | None = None,
    n_electrons: int | None = None,
    angles: Sequence[float] | None = None,
    store_pauli_features: bool = True,
) -> Callable[[Sequence[int]], dict[str, Any]]:
    """Return ``oracle(indices) -> record`` with energy and optional Pauli features."""
    ref = (
        np.asarray(reference, dtype=np.complex128).ravel()
        if reference is not None
        else default_hf_reference(n_qubits=pool.n_qubits, n_electrons=n_electrons)
    )
    basis: PauliTermBasis | None = None
    identity_coeff = 0.0
    h_coeffs: np.ndarray | None = None
    if store_pauli_features:
        basis = pauli_basis_from_hamiltonian(hamiltonian)
        identity_coeff, h_coeffs = hamiltonian_coefficients(hamiltonian, basis)

    def oracle(indices: Sequence[int]) -> dict[str, Any]:
        state = apply_pool_sequence(pool, indices, ref, angles=angles)
        energy = float(executor.expectation_state(state, hamiltonian, pool.n_qubits))
        feats: dict[str, Any] | None = None
        if basis is not None and h_coeffs is not None:
            q = pauli_expectations(state, basis, n_qubits=pool.n_qubits)
            feats = {
                "labels": list(basis.labels),
                "q": q.tolist(),
                "h": h_coeffs.tolist(),
                "identity_coeff": float(identity_coeff),
            }
            # sanity: reconstructed energy should match executor
            e_rec = float(identity_coeff + np.dot(h_coeffs, q))
            feats["energy_from_features"] = e_rec
        return make_oracle_record(
            indices=indices,
            energy=energy,
            pool=pool,
            pauli_features=feats,
        )

    return oracle


def make_oracle_record(
    *,
    indices: Sequence[int],
    energy: float,
    pool: GQEOperatorPool,
    meta: dict[str, Any] | None = None,
    pauli_features: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Minimal path-1 style oracle record for replay / repro / reweighting."""
    rec: dict[str, Any] = {
        "schema": GQE_ORACLE_RECORD_V1,
        "candidate": {
            "type": "operator_sequence",
            "token_sequence": [int(i) for i in indices],
            "sequence_length": len(indices),
            "operator_pool": pool.pool_id,
        },
        "labels": {"energy_hartree": float(energy), "energy_unit": "hartree"},
        "quantum_execution": {
            "n_qubits": pool.n_qubits,
            "default_angle": pool.default_angle,
            "token_angles": [pool.angle_for(int(i)) for i in indices],
            "backend": "hamiltonian_expectation_executor",
            "unitary_convention": "expm(theta * G)",
        },
        "meta": dict(meta or {}),
    }
    if pauli_features is not None:
        rec["pauli_features"] = pauli_features
    return rec
