"""UCCSD state-prep as :class:`~qchem_stack.backends.spec.CircuitIR` (JW-first Trotter product).

Uses dense cluster exponentials as ``UNITARY`` blocks (valid for small active spaces; parity-gated).
Per-Pauli-string gate decomposition (InQuanto-style ``exp(-iθP)`` chains) is deferred to follow-up.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from scipy.linalg import expm

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class UCCSDCircuitContext:
    """Minimal fermion context to rebuild UCCSD cluster layers."""

    mapping: str
    n_spin_orbitals: int
    n_electrons: int
    n_trotter_steps: int
    antiherm_mats: tuple[np.ndarray, ...]

    @classmethod
    def from_hamiltonian(
        cls,
        hamiltonian: QubitHamiltonian,
        *,
        trotter_steps: int | None,
    ) -> UCCSDCircuitContext:
        from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

        n_steps = 1 if trotter_steps is None else int(trotter_steps)
        ucc = (
            UCCSDTrotterVQE(hamiltonian, n_trotter_steps=n_steps)
            if trotter_steps is not None
            else UCCSDVQE(hamiltonian)
        )
        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("UCCSD circuit context requires hamiltonian.fermion_space")
        mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        return cls(
            mapping=mapping,
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
            n_trotter_steps=n_steps if trotter_steps is not None else 1,
            antiherm_mats=tuple(ucc._antiherm_mats),
        )


def uccsd_reference_statevector(ctx: UCCSDCircuitContext) -> np.ndarray:
    return reference_state_dense(
        mapping=ctx.mapping,
        n_spin_orbitals=ctx.n_spin_orbitals,
        n_electrons=ctx.n_electrons,
    )


def _project_jw_sector(psi: np.ndarray, *, n_electrons: int, n_qubits: int) -> np.ndarray:
    from openfermion.linalg.sparse_tools import jw_number_indices

    out = np.zeros_like(psi, dtype=np.complex128)
    for i in jw_number_indices(n_electrons, n_qubits):
        out[i] = psi[i]
    nrm = float(np.linalg.norm(out))
    if nrm < 1e-14:
        raise ValueError("JW sector projection collapsed to zero norm.")
    return out / nrm


def uccsd_prepare_statevector(
    angles: np.ndarray,
    ctx: UCCSDCircuitContext,
    *,
    n_qubits: int,
) -> np.ndarray:
    """Match :meth:`~qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE.prepare_state` ordering."""
    psi = uccsd_reference_statevector(ctx)
    inv = 1.0 / float(max(1, ctx.n_trotter_steps))
    ang = np.asarray(angles, dtype=float).ravel()
    if ang.size != len(ctx.antiherm_mats):
        raise ValueError(f"expected {len(ctx.antiherm_mats)} angles, got {ang.size}")
    for _ in range(max(1, ctx.n_trotter_steps)):
        for th, mat in zip(ang, ctx.antiherm_mats, strict=True):
            psi = expm(float(th * inv) * mat) @ psi
            nrm = float(np.linalg.norm(psi))
            if nrm < 1e-14:
                raise ValueError("UCCSD circuit state collapsed to zero norm.")
            psi = psi / nrm
    if ctx.mapping == "jordan_wigner":
        return _project_jw_sector(psi, n_electrons=ctx.n_electrons, n_qubits=n_qubits)
    nrm = float(np.linalg.norm(psi))
    return psi / nrm


def uccsd_prep_operations(
    angles: np.ndarray,
    ctx: UCCSDCircuitContext,
    *,
    n_qubits: int,
) -> list[dict[str, Any]]:
    """CircuitIR ops: reference INIT + sequential UNITARY cluster layers."""
    ref = uccsd_reference_statevector(ctx)
    ops: list[dict[str, Any]] = [
        {
            "name": "INIT_STATEVECTOR",
            "qubits": list(range(n_qubits)),
            "params": {"amplitudes": np.asarray(ref, dtype=np.complex128).tolist()},
        }
    ]
    inv = 1.0 / float(max(1, ctx.n_trotter_steps))
    ang = np.asarray(angles, dtype=float).ravel()
    for step in range(max(1, ctx.n_trotter_steps)):
        for idx, (th, mat) in enumerate(zip(ang, ctx.antiherm_mats, strict=True)):
            u = expm(float(th * inv) * mat)
            ops.append(
                {
                    "name": "UNITARY",
                    "qubits": list(range(n_qubits)),
                    "params": {
                        "matrix": np.asarray(u, dtype=np.complex128).tolist(),
                        "layer": int(step),
                        "generator_index": int(idx),
                    },
                }
            )
    return ops


def uccsd_circuit_ir(
    angles: np.ndarray,
    ctx: UCCSDCircuitContext,
    *,
    n_qubits: int,
) -> CircuitIR:
    return CircuitIR(
        n_qubits=n_qubits,
        operations=uccsd_prep_operations(angles, ctx, n_qubits=n_qubits),
        boxes=["UCCSDPrep"],
    )


def ansatz_prep_box_label(kind: Literal["hea", "uccsd"]) -> str:
    return "HEA" if kind == "hea" else "UCCSDPrep"
