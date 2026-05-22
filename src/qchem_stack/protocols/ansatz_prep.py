"""Ansatz-aware state preparation for Pauli averaging (InQuanto/Tangelo-style Ansatz × Protocol)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.backends.pauli_measure_expand import hea_operations
from qchem_stack.quantum.algorithms.uccsd_circuit import (
    UCCSDCircuitContext,
    uccsd_prep_operations,
    uccsd_prepare_statevector,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class AnsatzPrepSpec:
    kind: Literal["hea", "uccsd"]
    n_qubits: int
    angles: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=float))
    hea_depth: int = 1
    uccsd_ctx: UCCSDCircuitContext | None = None

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
    ) -> AnsatzPrepSpec:
        ctx = UCCSDCircuitContext.from_hamiltonian(hamiltonian, trotter_steps=trotter_steps)
        return cls(
            kind="uccsd",
            n_qubits=int(hamiltonian.n_qubits),
            angles=np.asarray(angles, dtype=float),
            uccsd_ctx=ctx,
        )


def build_prep_operations(spec: AnsatzPrepSpec) -> list[dict[str, Any]]:
    if spec.kind == "hea":
        return hea_operations(spec.n_qubits, spec.hea_depth, spec.angles)
    if spec.uccsd_ctx is None:
        raise ValueError("uccsd AnsatzPrepSpec requires uccsd_ctx")
    return uccsd_prep_operations(spec.angles, spec.uccsd_ctx, n_qubits=spec.n_qubits)


def prepare_statevector(spec: AnsatzPrepSpec) -> np.ndarray:
    if spec.kind == "hea":
        from qchem_stack.quantum.statevector import hea_state

        return np.asarray(
            hea_state(spec.angles, spec.n_qubits, spec.hea_depth),
            dtype=np.complex128,
        ).ravel()
    if spec.uccsd_ctx is None:
        raise ValueError("uccsd AnsatzPrepSpec requires uccsd_ctx")
    return uccsd_prepare_statevector(spec.angles, spec.uccsd_ctx, n_qubits=spec.n_qubits)


def prep_box_label(spec: AnsatzPrepSpec) -> str:
    return "HEA" if spec.kind == "hea" else "UCCSDPrep"


def ansatz_prep_meta(spec: AnsatzPrepSpec) -> dict[str, Any]:
    meta: dict[str, Any] = {"ansatz_kind": spec.kind}
    if spec.kind == "hea":
        meta["hea_depth"] = int(spec.hea_depth)
    elif spec.uccsd_ctx is not None:
        meta["uccsd_trotter_steps"] = int(spec.uccsd_ctx.n_trotter_steps)
        meta["fermion_to_qubit_map"] = spec.uccsd_ctx.mapping
    return meta
