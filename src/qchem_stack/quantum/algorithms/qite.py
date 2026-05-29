"""Quantum imaginary-time evolution (QITE) research plugin — steepest descent on cluster angles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import expm

from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import expectation_qubit_operator, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class QITEResult:
    energy: float
    angles: np.ndarray
    n_steps: int
    meta: dict[str, Any] = field(default_factory=dict)


class QITEVQE(AlgorithmBase):
    """QITE-style imaginary-time stepping on a small fixed operator pool."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        pool_id: str = "fermionic_uccsd_singles",
        max_ops: int = 2,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        super().__init__()
        self._algorithm_name = "qite"
        self._report_schema = "algorithm_qite_report_v1"
        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.pool = build_registered_operator_pool(pool_id, hamiltonian)[: int(max_ops)]
        self._executor = executor or StatevectorHeaExecutor()

    def _apply_pool(self, st: np.ndarray, angles: np.ndarray) -> np.ndarray:
        out = st
        for theta, op in zip(angles, self.pool, strict=False):
            mat = qubit_operator_to_sparse(op, self.n_qubits)
            out = expm(-1j * float(theta) * mat) @ out
        return out

    def run(self, *, n_steps: int = 30, dt: float = 0.05, seed: int = 0) -> QITEResult:
        del seed
        fs = self.hamiltonian.fermion_space
        if fs is None:
            raise ValueError("QITEVQE requires fermion_space")
        mapping_raw = (self.hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        ref = reference_state_dense(
            mapping=str(mapping),
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
        )
        h_mat = qubit_operator_to_sparse(self.h_op, self.n_qubits)
        angles = np.zeros(len(self.pool), dtype=float)
        st = ref
        e = float(np.real(expectation_qubit_operator(st, self.h_op, self.n_qubits)))
        for _ in range(int(n_steps)):
            grads = []
            for op in self.pool:
                mat = qubit_operator_to_sparse(op, self.n_qubits)
                psi = mat @ st
                grads.append(float(np.real(np.vdot(st, h_mat @ psi))))
            g = np.asarray(grads, dtype=float)
            if float(np.linalg.norm(g)) < 1e-8:
                break
            angles -= float(dt) * g
            st = self._apply_pool(ref, angles)
            e = float(np.real(expectation_qubit_operator(st, self.h_op, self.n_qubits)))
        return QITEResult(
            energy=float(e),
            angles=angles,
            n_steps=int(n_steps),
            meta={"variational_ansatz": "qite", "pool_size": len(self.pool), "dt": float(dt)},
        )
