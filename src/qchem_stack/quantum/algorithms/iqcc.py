"""Imaginary-time QCC (iQCC) research plugin — fixed small qubit-excitation pool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import expectation_qubit_operator, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class IQCCResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class IQCCVQE(AlgorithmBase):
    """iQCC-style variational loop with a fixed qubit-excitation pool (research plugin)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        pool_id: str = "iqeb_qubit_excitation",
        max_ops: int = 4,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        super().__init__()
        self._algorithm_name = "iqcc"
        self._report_schema = "algorithm_iqcc_report_v1"
        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.pool = build_registered_operator_pool(pool_id, hamiltonian)[: int(max_ops)]
        self.n_params = len(self.pool)
        self._executor = executor or StatevectorHeaExecutor()

    def _reference(self) -> np.ndarray:
        fs = self.hamiltonian.fermion_space
        if fs is None:
            raise ValueError("IQCCVQE requires fermion_space")
        mapping_raw = (self.hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        return reference_state_dense(
            mapping=str(mapping),
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
        )

    def _state(self, angles: np.ndarray) -> np.ndarray:
        st = self._reference()
        for theta, op in zip(angles, self.pool, strict=False):
            mat = qubit_operator_to_sparse(op, self.n_qubits)
            st = expm(-1j * float(theta) * mat) @ st
        return st

    def run(self, *, maxiter: int = 200, seed: int = 0) -> IQCCResult:
        x0 = np.zeros(self.n_params, dtype=float)
        nfev = 0

        def obj(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            st = self._state(x)
            return float(np.real(expectation_qubit_operator(st, self.h_op, self.n_qubits)))

        res = minimize(obj, x0, method="COBYLA", options={"maxiter": int(maxiter)})
        return IQCCResult(
            energy=float(res.fun),
            angles=np.asarray(res.x, dtype=float),
            nfev=int(nfev),
            meta={"variational_ansatz": "iqcc", "pool_size": len(self.pool)},
        )
