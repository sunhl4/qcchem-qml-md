"""Quantum Coupled Cluster (QCC) minimal ansatz: fixed qubit-excitation pool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.contracts.schema_ids import ALGORITHM_UCCSD_REPORT_V1
from qchem_stack.quantum.algorithms.tolerances import NUMERICAL_TOLERANCE
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class QCCVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class QCCVQE:
    """Layered qubit-cluster exponentials from the IQEB qubit-excitation pool."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        executor: HamiltonianExpectationExecutor | None = None,
        pool_id: str = "iqeb_qubit_excitation",
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor
        from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense

        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self._executor = executor or StatevectorHeaExecutor()
        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("QCCVQE requires fermion_space for HF reference state.")
        mapping = str((hamiltonian.meta or {}).get("fermion_to_qubit_map") or "jordan_wigner")
        if mapping == "symmetry_conserving_bravyi_kitaev":
            raise ValueError(
                "QCCVQE requires square JW/BK reference; SCBK truncated space unsupported."
            )
        self._reference = reference_state_dense(
            mapping=mapping if mapping != "symmetry_conserving_bravyi_kitaev" else "jordan_wigner",
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
        )
        pool = build_registered_operator_pool(pool_id, hamiltonian)
        self._cluster_mats = [1.0j * qubit_operator_to_sparse(op, self.n_qubits) for op in pool]
        self.n_params = len(self._cluster_mats)
        self._pool_id = pool_id

    def _state_from_angles(self, angles: np.ndarray) -> np.ndarray:
        psi = self._reference.copy()
        for th, mat in zip(angles, self._cluster_mats, strict=False):
            psi = expm(float(th) * mat) @ psi
            nrm = float(np.linalg.norm(psi))
            if nrm < NUMERICAL_TOLERANCE:
                raise ValueError("QCC state collapsed to zero norm.")
            psi = psi / nrm
        return psi

    def run(
        self,
        maxiter: int = 200,
        *,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> QCCVQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        x0 = rng.uniform(-np.pi, np.pi, size=self.n_params)
        nfev = 0

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            st = self._state_from_angles(x)
            return float(exe.expectation_state(st, self.h_op, self.n_qubits))

        res = minimize(objective, x0, method="COBYLA", options={"maxiter": int(maxiter)})
        return QCCVQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x, dtype=float),
            nfev=nfev,
            meta={
                "variational_ansatz": "qcc",
                "qcc_pool_id": self._pool_id,
                "qcc_n_parameters": self.n_params,
                "scipy_message": str(res.message),
            },
        )


def qcc_algorithm_report_v1(result: QCCVQEResult) -> dict[str, Any]:
    return {
        "schema": ALGORITHM_UCCSD_REPORT_V1,
        "algorithm": "vqe",
        "variational_ansatz": "qcc",
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "final_parameters": result.angles.tolist(),
        "meta": dict(result.meta),
    }
