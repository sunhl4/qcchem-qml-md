"""
Dense statevector expectation **reference** for small :class:`openfermion.QubitOperator`.

Cross-checks Pauli energies vs tensor-network narratives without cuTensorNet. Complexity ``O(4^n)``.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from openfermion.linalg import get_sparse_operator


def dense_expectation_api_descriptor() -> dict[str, Any]:
    return {
        "schema": "dense_expectation_reference_v1",
        "function": "qchem_stack.tensornet.dense_expectation_reference.expectation_qubit_operator_dense",
        "max_qubits_recommended": 16,
        "note": "Explicit dense matrix — for auditing small systems; not scalable TN chemistry.",
    }


def expectation_qubit_operator_dense(
    q_op: Any, statevec: np.ndarray, *, n_qubits: int | None = None
) -> float:
    """Return ``Re ⟨ψ|H|ψ⟩`` for normalized ``statevec`` (length ``2**n``)."""
    psi = np.asarray(statevec, dtype=np.complex128).ravel()
    n = n_qubits if n_qubits is not None else int(np.log2(psi.size))
    if 2**n != psi.size:
        raise ValueError("statevec length must be 2**n_qubits")
    mat = get_sparse_operator(q_op, n_qubits=n).toarray()
    return float(np.real(np.vdot(psi, mat @ psi)))
