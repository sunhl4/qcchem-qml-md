from __future__ import annotations

import numpy as np
from scipy.linalg import eigvalsh

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.statevector import qubit_operator_to_sparse


def kitaev_qpe_energy_estimate(h: QubitHamiltonian, bits: int = 4) -> float:
    """Classical emulation of ideal QPE: return ground eigenvalue from dense H."""
    mat = qubit_operator_to_sparse(h.operator, h.n_qubits)
    w = eigvalsh(mat)
    return float(np.min(np.real(w)))
