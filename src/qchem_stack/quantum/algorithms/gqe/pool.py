"""Operator-pool / vocabulary builders for GQE (Nakaji discrete time × Pauli)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from openfermion import jordan_wigner
from openfermion.ops import QubitOperator

from qchem_stack.quantum.algorithms.gqe.types import GQEPoolMode, PoolToken
from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import pauli_matrix

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def _nakaji_times(time_scale: float, exponents: tuple[int, ...]) -> list[float]:
    vals: list[float] = []
    for k in exponents:
        t = (2.0**int(k)) / float(time_scale)
        vals.extend([t, -t])
    return vals


def _pauli_string_from_term(term: tuple) -> str | None:
    if not term:
        return None
    max_q = max(int(q) for q, _ in term)
    chars = ["I"] * (max_q + 1)
    for q, op in term:
        chars[int(q)] = str(op)
    return "".join(chars)


def _pad_pauli(ps: str, n_qubits: int) -> str:
    if len(ps) > n_qubits:
        raise ValueError(f"Pauli string {ps!r} longer than n_qubits={n_qubits}")
    if len(ps) < n_qubits:
        return ps + ("I" * (n_qubits - len(ps)))
    return ps


def _qcc_proxy_cost(pauli_string: str) -> float:
    """Cheap cutting-cost proxy: non-identity support size (A2-style budget)."""
    return float(sum(1 for c in pauli_string if c != "I"))


def _smiles_label(pauli_string: str, time: float) -> str:
    """SMILES-inspired operator text (A3): shareable across molecules."""
    return f"[{pauli_string}]@{time:.6g}"


def _unique_pauli_strings_from_qubit_ops(
    ops: list[QubitOperator], n_qubits: int
) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for qop in ops:
        for term in qop.terms:
            ps = _pauli_string_from_term(term)
            if ps is None:
                continue
            ps = _pad_pauli(ps, n_qubits)
            if ps == "I" * n_qubits or ps in seen:
                continue
            seen.add(ps)
            out.append(ps)
    return out


def _hamiltonian_pauli_strings(hamiltonian: QubitHamiltonian) -> list[str]:
    return _unique_pauli_strings_from_qubit_ops([hamiltonian.operator], hamiltonian.n_qubits)


def _uccsd_pauli_strings(hamiltonian: QubitHamiltonian) -> list[str]:
    from qchem_stack.chem.kernels.spin_ucc import build_spin_uccsd_fermion_generators

    fs = hamiltonian.fermion_space
    if fs is None:
        return _hamiltonian_pauli_strings(hamiltonian)
    ferm_ops = build_spin_uccsd_fermion_generators(int(fs.n_spin_orbitals), int(fs.n_electrons))
    qops: list[QubitOperator] = []
    for fer in ferm_ops:
        q = jordan_wigner(fer)
        if isinstance(q, QubitOperator):
            qops.append(q)
    return _unique_pauli_strings_from_qubit_ops(qops, hamiltonian.n_qubits) or _hamiltonian_pauli_strings(
        hamiltonian
    )


def _spin_heisenberg_pauli_strings(n_qubits: int) -> list[str]:
    out: list[str] = []
    for i in range(n_qubits - 1):
        for axes in ("XX", "YY", "ZZ"):
            chars = ["I"] * n_qubits
            chars[i] = axes[0]
            chars[i + 1] = axes[1]
            out.append("".join(chars))
    return out


def _simple_pauli_strings(n_qubits: int) -> list[str]:
    out: list[str] = []
    for q in range(n_qubits):
        for ax in ("X", "Y", "Z"):
            chars = ["I"] * n_qubits
            chars[q] = ax
            out.append("".join(chars))
    for i in range(n_qubits - 1):
        chars = ["I"] * n_qubits
        chars[i] = "X"
        chars[i + 1] = "X"
        out.append("".join(chars))
    return out


def build_gqe_pool(
    hamiltonian: QubitHamiltonian,
    *,
    mode: GQEPoolMode = "hamiltonian_pauli",
    time_scale: float = 320.0,
    time_exponents: tuple[int, ...] = (0, 1, 2, 3),
    max_paulis: int | None = 32,
) -> list[PoolToken]:
    """Build Nakaji-style vocabulary ``{e^{i P t}} ∪ {I}``."""
    n = int(hamiltonian.n_qubits)
    if mode == "uccsd":
        paulis = _uccsd_pauli_strings(hamiltonian)
    elif mode == "spin_heisenberg":
        paulis = _spin_heisenberg_pauli_strings(n)
    elif mode == "simple":
        paulis = _simple_pauli_strings(n)
    else:
        paulis = _hamiltonian_pauli_strings(hamiltonian)
    if not paulis:
        paulis = _simple_pauli_strings(n)
    if max_paulis is not None and len(paulis) > int(max_paulis):
        paulis = paulis[: int(max_paulis)]

    times = _nakaji_times(time_scale, time_exponents)
    tokens: list[PoolToken] = [
        PoolToken(
            index=0,
            pauli_string=None,
            time=0.0,
            label="I",
            is_identity=True,
            qcc_cost=0.0,
            smiles_text="[I]@0",
        )
    ]
    idx = 1
    for ps in paulis:
        for t in times:
            tokens.append(
                PoolToken(
                    index=idx,
                    pauli_string=ps,
                    time=float(t),
                    label=f"{ps}:{t:+.6g}",
                    is_identity=False,
                    qcc_cost=_qcc_proxy_cost(ps),
                    smiles_text=_smiles_label(ps, float(t)),
                )
            )
            idx += 1
    return tokens


def precompute_token_unitaries(tokens: list[PoolToken], n_qubits: int) -> list[np.ndarray]:
    """Dense ``U_j = exp(i t P)`` matrices for fast sequence propagation."""
    from scipy.linalg import expm

    dim = 2**n_qubits
    eye = np.eye(dim, dtype=np.complex128)
    mats: list[np.ndarray] = []
    for tok in tokens:
        if tok.is_identity or tok.pauli_string is None:
            mats.append(eye)
            continue
        p = pauli_matrix(_pad_pauli(tok.pauli_string, n_qubits))
        mats.append(np.asarray(expm(1j * float(tok.time) * p), dtype=np.complex128))
    return mats
