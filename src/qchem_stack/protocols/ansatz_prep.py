"""Ansatz-aware state preparation for Pauli averaging (Ansatz × Protocol orthogonality)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.backends.pauli_measure_expand import hea_operations
from qchem_stack.quantum.algorithms.qcc_circuit import (
    QCCCircuitContext,
    qcc_prep_operations,
    qcc_prepare_statevector,
)
from qchem_stack.quantum.algorithms.uccsd_circuit import (
    UCCSDCircuitContext,
    uccsd_prep_operations,
    uccsd_prepare_statevector,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import DecompositionMode

ClusterAnsatzKind = Literal["uccsd", "uccgd", "upccgsd", "puccd"]


@dataclass
class AnsatzPrepSpec:
    kind: Literal["hea", "uccsd", "uccgd", "upccgsd", "puccd", "qcc"]
    n_qubits: int
    angles: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=float))
    hea_depth: int = 1
    uccsd_ctx: UCCSDCircuitContext | None = None
    qcc_ctx: QCCCircuitContext | None = None
    uccsd_decomposition_mode: DecompositionMode = "pauli"

    @classmethod
    def hea(
        cls,
        *,
        n_qubits: int,
        angles: np.ndarray,
        depth: int,
    ) -> AnsatzPrepSpec:
        return cls(
            kind="hea",
            n_qubits=int(n_qubits),
            angles=np.asarray(angles, dtype=float),
            hea_depth=int(depth),
        )

    @classmethod
    def uccsd(
        cls,
        *,
        hamiltonian: QubitHamiltonian,
        angles: np.ndarray,
        trotter_steps: int | None,
        decomposition_mode: DecompositionMode = "pauli",
    ) -> AnsatzPrepSpec:
        return cls.cluster(
            kind="uccsd",
            hamiltonian=hamiltonian,
            angles=angles,
            trotter_steps=trotter_steps,
            decomposition_mode=decomposition_mode,
        )

    @classmethod
    def cluster(
        cls,
        *,
        kind: ClusterAnsatzKind,
        hamiltonian: QubitHamiltonian,
        angles: np.ndarray,
        trotter_steps: int | None,
        decomposition_mode: DecompositionMode = "pauli",
    ) -> AnsatzPrepSpec:
        ctx = UCCSDCircuitContext.from_hamiltonian(
            hamiltonian, trotter_steps=trotter_steps, cluster_ansatz=kind
        )
        return cls(
            kind=kind,
            n_qubits=int(hamiltonian.n_qubits),
            angles=np.asarray(angles, dtype=float),
            uccsd_ctx=ctx,
            uccsd_decomposition_mode=decomposition_mode,
        )

    @classmethod
    def qcc(
        cls,
        *,
        hamiltonian: QubitHamiltonian,
        angles: np.ndarray,
        pool_id: str = "iqeb_qubit_excitation",
        decomposition_mode: DecompositionMode = "pauli",
    ) -> AnsatzPrepSpec:
        ctx = QCCCircuitContext.from_hamiltonian(hamiltonian, pool_id=pool_id)
        return cls(
            kind="qcc",
            n_qubits=int(hamiltonian.n_qubits),
            angles=np.asarray(angles, dtype=float),
            qcc_ctx=ctx,
            uccsd_decomposition_mode=decomposition_mode,
        )


def build_prep_operations(spec: AnsatzPrepSpec) -> list[dict[str, Any]]:
    if spec.kind == "hea":
        return hea_operations(spec.n_qubits, spec.hea_depth, spec.angles)
    if spec.kind == "qcc":
        if spec.qcc_ctx is None:
            raise ValueError("qcc AnsatzPrepSpec requires qcc_ctx")
        return qcc_prep_operations(
            spec.angles,
            spec.qcc_ctx,
            decomposition_mode=spec.uccsd_decomposition_mode,
        )
    if spec.uccsd_ctx is None:
        raise ValueError(f"{spec.kind} AnsatzPrepSpec requires uccsd_ctx")
    return uccsd_prep_operations(
        spec.angles,
        spec.uccsd_ctx,
        n_qubits=spec.n_qubits,
        decomposition_mode=spec.uccsd_decomposition_mode,
    )


def prepare_statevector(spec: AnsatzPrepSpec) -> np.ndarray:
    if spec.kind == "hea":
        from qchem_stack.quantum.statevector import hea_state

        return np.asarray(
            hea_state(spec.angles, spec.n_qubits, spec.hea_depth),
            dtype=np.complex128,
        ).ravel()
    if spec.kind == "qcc":
        if spec.qcc_ctx is None:
            raise ValueError("qcc AnsatzPrepSpec requires qcc_ctx")
        return qcc_prepare_statevector(spec.angles, spec.qcc_ctx)
    if spec.uccsd_ctx is None:
        raise ValueError("uccsd AnsatzPrepSpec requires uccsd_ctx")
    return uccsd_prepare_statevector(spec.angles, spec.uccsd_ctx, n_qubits=spec.n_qubits)


def prep_box_label(spec: AnsatzPrepSpec) -> str:
    if spec.kind == "hea":
        return "HEA"
    if spec.kind == "qcc":
        return "QCCPrep"
    return f"{spec.kind.upper()}Prep"


def ansatz_prep_meta(spec: AnsatzPrepSpec) -> dict[str, Any]:
    meta: dict[str, Any] = {"ansatz_kind": spec.kind}
    if spec.kind == "hea":
        meta["hea_depth"] = int(spec.hea_depth)
    elif spec.kind == "qcc" and spec.qcc_ctx is not None:
        meta["fermion_to_qubit_map"] = spec.qcc_ctx.mapping
        meta["uccsd_decomposition_mode"] = spec.uccsd_decomposition_mode
        meta["cluster_ansatz"] = "qcc"
        meta["qcc_pool_id"] = spec.qcc_ctx.pool_id
        meta["qcc_n_parameters"] = len(spec.qcc_ctx.cluster_mats)
    elif spec.uccsd_ctx is not None:
        meta["uccsd_trotter_steps"] = int(spec.uccsd_ctx.n_trotter_steps)
        meta["fermion_to_qubit_map"] = spec.uccsd_ctx.mapping
        meta["uccsd_decomposition_mode"] = spec.uccsd_decomposition_mode
        meta["cluster_ansatz"] = spec.kind
    return meta
