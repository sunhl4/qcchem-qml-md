"""Unitary Pair Coupled Cluster GSD (UpCCGSD) — closed-shell singles + paired doubles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.kernels.spin_ucc import build_spin_uccsd_fermion_generators
from qchem_stack.quantum.algorithms.uccsd_mapping import (
    antihermitian_cluster_matrices,
)
from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDVQEResult

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


class UpCCGSDVQE(UCCSDVQE):
    """Pair-coupled cluster with singles and paired doubles (JW/BK square encodings)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self._executor = executor or StatevectorHeaExecutor()

        mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        if mapping == "symmetry_conserving_bravyi_kitaev":
            raise ValueError(
                "UpCCGSD dense cluster ansatz requires a square fermion encoding "
                "(jordan_wigner or bravyi_kitaev with n_spin_orbitals == n_qubits)."
            )

        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("UpCCGSDVQE requires hamiltonian.fermion_space for electron count.")
        self._fermion_mapping = mapping
        self._n_so = int(fs.n_spin_orbitals)
        self._n_e = int(fs.n_electrons)
        if self._n_so != self.n_qubits:
            raise ValueError(
                f"JW/BK-square UpCCGSD expects n_spin_orbitals == n_qubits "
                f"({self._n_so} vs {self.n_qubits})."
            )

        ferm_ops = build_spin_uccsd_fermion_generators(self._n_so, self._n_e)
        self._antiherm_mats = antihermitian_cluster_matrices(
            ferm_ops,
            mapping=self._fermion_mapping,
            n_qubits=self.n_qubits,
            n_spin_orbitals=self._n_so,
        )
        self.n_params = len(self._antiherm_mats)

    def _run_meta_base(self) -> dict[str, object]:
        meta = super()._run_meta_base()
        meta["variational_ansatz"] = "upccgsd"
        meta["upccgsd_n_parameters"] = self.n_params
        return meta


def upccgsd_algorithm_report_v1(result: UCCSDVQEResult) -> dict[str, object]:
    from qchem_stack.contracts.schema_ids import ALGORITHM_UCCSD_REPORT_V1

    return {
        "schema": ALGORITHM_UCCSD_REPORT_V1,
        "algorithm": "vqe",
        "variational_ansatz": "upccgsd",
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "final_parameters": result.angles.tolist(),
        "meta": dict(result.meta),
    }
