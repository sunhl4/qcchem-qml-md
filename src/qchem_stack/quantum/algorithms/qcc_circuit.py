"""QCC state-prep as CircuitIR (Pauli rotation chains from qubit-excitation pool)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from scipy.linalg import expm

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense
from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import (
    DecompositionMode,
    cluster_layer_ops,
)
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class QCCCircuitContext:
    """Minimal fermion context to rebuild QCC qubit-cluster layers."""

    mapping: str
    n_spin_orbitals: int
    n_electrons: int
    n_qubits: int
    cluster_mats: tuple[np.ndarray, ...]
    pool_id: str

    @classmethod
    def from_hamiltonian(
        cls,
        hamiltonian: QubitHamiltonian,
        *,
        pool_id: str = "iqeb_qubit_excitation",
    ) -> QCCCircuitContext:
        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("QCC circuit context requires hamiltonian.fermion_space")
        mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        if mapping == "symmetry_conserving_bravyi_kitaev":
            raise ValueError(
                "QCC circuit context requires square JW/BK reference; SCBK unsupported."
            )
        pool = build_registered_operator_pool(pool_id, hamiltonian)
        cluster_mats = tuple(
            1.0j * qubit_operator_to_sparse(op, hamiltonian.n_qubits) for op in pool
        )
        return cls(
            mapping=mapping,
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
            n_qubits=int(hamiltonian.n_qubits),
            cluster_mats=cluster_mats,
            pool_id=str(pool_id),
        )


def qcc_reference_statevector(ctx: QCCCircuitContext) -> np.ndarray:
    return reference_state_dense(
        mapping=ctx.mapping,
        n_spin_orbitals=ctx.n_spin_orbitals,
        n_electrons=ctx.n_electrons,
    )


def qcc_prepare_statevector(angles: np.ndarray, ctx: QCCCircuitContext) -> np.ndarray:
    """Match :meth:`~qchem_stack.quantum.algorithms.qcc_vqe.QCCVQE._state_from_angles`."""
    psi = qcc_reference_statevector(ctx).copy()
    ang = np.asarray(angles, dtype=float).ravel()
    if ang.size != len(ctx.cluster_mats):
        raise ValueError(f"expected {len(ctx.cluster_mats)} angles, got {ang.size}")
    for th, mat in zip(ang, ctx.cluster_mats, strict=True):
        psi = expm(float(th) * mat) @ psi
        nrm = float(np.linalg.norm(psi))
        if nrm < 1e-14:
            raise ValueError("QCC circuit state collapsed to zero norm.")
        psi = psi / nrm
    return psi


def qcc_prep_operations(
    angles: np.ndarray,
    ctx: QCCCircuitContext,
    *,
    decomposition_mode: DecompositionMode = "pauli",
) -> list[dict[str, Any]]:
    """CircuitIR ops: reference INIT + QCC cluster exponentials."""
    ref = qcc_reference_statevector(ctx)
    ops: list[dict[str, Any]] = [
        {
            "name": "INIT_STATEVECTOR",
            "qubits": list(range(ctx.n_qubits)),
            "params": {"amplitudes": np.asarray(ref, dtype=np.complex128).tolist()},
        }
    ]
    ang = np.asarray(angles, dtype=float).ravel()
    if ang.size != len(ctx.cluster_mats):
        raise ValueError(f"expected {len(ctx.cluster_mats)} angles, got {ang.size}")
    for idx, (th, mat) in enumerate(zip(ang, ctx.cluster_mats, strict=True)):
        layer_angle = float(th)
        if decomposition_mode == "pauli":
            ops.extend(
                cluster_layer_ops(
                    mat,
                    layer_angle,
                    ctx.n_qubits,
                    layer=0,
                    generator_index=idx,
                )
            )
        elif decomposition_mode == "unitary":
            u = expm(layer_angle * mat)
            ops.append(
                {
                    "name": "UNITARY",
                    "qubits": list(range(ctx.n_qubits)),
                    "params": {
                        "matrix": np.asarray(u, dtype=np.complex128).tolist(),
                        "layer": 0,
                        "generator_index": int(idx),
                    },
                }
            )
        else:
            raise ValueError(f"unknown qcc decomposition_mode: {decomposition_mode!r}")
    return ops


def qcc_circuit_ir(
    angles: np.ndarray,
    ctx: QCCCircuitContext,
    *,
    decomposition_mode: DecompositionMode = "pauli",
) -> CircuitIR:
    return CircuitIR(
        n_qubits=ctx.n_qubits,
        operations=qcc_prep_operations(angles, ctx, decomposition_mode=decomposition_mode),
        boxes=["QCCPrep"],
    )


def ansatz_prep_box_label(kind: Literal["qcc"]) -> str:
    return "QCCPrep"


__all__ = [
    "QCCCircuitContext",
    "ansatz_prep_box_label",
    "qcc_circuit_ir",
    "qcc_prep_operations",
    "qcc_prepare_statevector",
    "qcc_reference_statevector",
]
