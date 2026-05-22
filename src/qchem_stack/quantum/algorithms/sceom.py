"""SCEOM / q-sc-EOM (Chemical Science D2SC05371C): reference subspace + nested-commutator ``M`` matrix.

Use :func:`run_sceom_nested_commutator` for ``M_{ij}=\\langle\\psi|[S_i^\\dagger,[H,S_j]]|\\psi\\rangle`` with
Pauli toy generators; :func:`run_sceom_reference_subspace` remains a separate numerical anchor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion import bravyi_kitaev, jordan_wigner
from openfermion.ops import QubitOperator
from scipy.linalg import eigh

from qchem_stack.chem.kernels.spin_ucc import build_spin_ucc_singles_only_fermion_generators
from qchem_stack.quantum.algorithms.excited import qse_matrices_hs
from qchem_stack.quantum.statevector import (
    expectation_qubit_operator,
    hea_state,
    qubit_operator_to_sparse,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class SCEOMResult:
    """Low-lying energies in a *correlated* subspace spanned by exact eigenvectors (reference only)."""

    energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


def run_sceom_reference_subspace(
    hamiltonian: QubitHamiltonian,
    *,
    subspace_dim: int = 4,
) -> SCEOMResult:
    """Diagonalize full H, take lowest-``subspace_dim`` eigenvectors as correlated basis, then rediagonalize.

    This is **not** the full shot-based ``M`` matrix from `Chem. Sci. D2SC05371C`, but provides a
    **numerical anchor** for small systems until SCEOM matrix protocols are implemented.
    """
    n = hamiltonian.n_qubits
    h_full = qubit_operator_to_sparse(hamiltonian.operator, n)
    w, vecs = eigh(h_full)
    order = np.argsort(np.real(w))
    k = min(subspace_dim, len(order))
    basis = [vecs[:, order[i]].ravel() for i in range(k)]
    h_sub, s_sub = qse_matrices_hs(hamiltonian.operator, n, basis)
    evals, _ = eigh(h_sub, s_sub)
    evals = np.sort(np.real(evals))
    return SCEOMResult(
        energies=[float(x) for x in evals],
        meta={
            "reference": "10.1039/D2SC05371C (SCEOM — here: eigenvector-subspace reference only)",
            "subspace_dim": k,
            "implementation_note": "correlated_basis=lowest_exact_eigenvectors_then_rediagonalize",
        },
    )


def run_sceom_reference_subspace_shot_noise(
    hamiltonian: QubitHamiltonian,
    *,
    subspace_dim: int = 4,
    shots_per_matrix_element: int = 4096,
    seed: int = 0,
) -> SCEOMResult:
    """Same correlated basis as :func:`run_sceom_reference_subspace`, Gaussian noise on ``real(H_sub)`` (placeholder)."""
    rng = np.random.default_rng(seed)
    n = hamiltonian.n_qubits
    h_full = qubit_operator_to_sparse(hamiltonian.operator, n)
    w, vecs = eigh(h_full)
    order = np.argsort(np.real(w))
    k = min(subspace_dim, len(order))
    basis = [vecs[:, order[i]].ravel() for i in range(k)]
    h_sub, s_sub = qse_matrices_hs(hamiltonian.operator, n, basis)
    scale = 1.0 / math.sqrt(max(1, shots_per_matrix_element))
    noise = rng.normal(0.0, scale, np.real(h_sub).shape)
    noise = (noise + noise.T) / 2.0
    h_noisy = np.real(h_sub) + noise
    evals, _ = eigh(h_noisy, np.real(s_sub))
    evals = np.sort(np.real(evals))
    return SCEOMResult(
        energies=[float(x) for x in evals],
        meta={
            "reference": "10.1039/D2SC05371C (SCEOM — shot noise on H_sub only, not true M-matrix)",
            "subspace_dim": k,
            "shot_noise_model": "symmetric_gaussian_on_real_H_sub",
            "shots_per_matrix_element": shots_per_matrix_element,
        },
    )


@dataclass
class SCEOMPlaceholder:
    """Deprecated name — use :func:`run_sceom_reference_subspace`."""

    note: str = "Use run_sceom_reference_subspace(hamiltonian, subspace_dim=...)."


def nested_sceom_q_sc_eom_operator(
    h: QubitOperator, si: QubitOperator, sj: QubitOperator
) -> QubitOperator:
    """``[S_i^\\dagger, [H, S_j]]`` for q-sc-EOM (Chemical Science, D2SC05371C / arXiv:2206.10502)."""
    comm = h * sj - sj * h
    return si * comm - comm * si


def default_sceom_pauli_generators(n_qubits: int, k: int) -> list[QubitOperator]:
    """Toy excitation operators: identity + single-qubit :math:`X_a` (not full fermionic pool)."""
    ops: list[QubitOperator] = [QubitOperator((), 1.0)]
    for q in range(n_qubits):
        if len(ops) >= k:
            break
        ops.append(QubitOperator(((q, "X"),), 1.0))
    while len(ops) < k:
        ops.append(QubitOperator((), 1.0))
    return ops[:k]


def fermionic_singles_generators_matching_h_mapping(
    hamiltonian: QubitHamiltonian,
) -> list[QubitOperator]:
    """Map spin-orbital singles to qubit Paulis using the Hamiltonian fermion-encoding metadata."""

    fs = hamiltonian.fermion_space
    if fs is None:
        raise ValueError("mapped SCEOM fermionic generators require hamiltonian.fermion_space")
    mmap_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
    mmap = str(mmap_raw or "jordan_wigner")
    if mmap == "symmetry_conserving_bravyi_kitaev":
        raise ValueError(
            "Mapped SCEOM singles are not wired for symmetry_conserving_bravyi_kitaev (truncated qubit Hilbert)."
        )
    if mmap not in {"jordan_wigner", "bravyi_kitaev"}:
        raise ValueError(f"Unsupported fermion_to_qubit_map for SCEOM singles: {mmap!r}")
    xf = {"jordan_wigner": jordan_wigner, "bravyi_kitaev": bravyi_kitaev}[mmap]
    ferm_ops = build_spin_ucc_singles_only_fermion_generators(
        int(fs.n_spin_orbitals), int(fs.n_electrons)
    )
    ops: list[QubitOperator] = []
    for fer in ferm_ops:
        q = xf(fer)
        if isinstance(q, QubitOperator):
            ops.append(q)
    if not ops:
        raise ValueError("Fermionic singles mapping produced zero qubit generators.")
    return ops


def sceom_extended_pauli_xy_generators(n_qubits: int, max_terms: int) -> list[QubitOperator]:
    """Identity-first pool interleaving :math:`X_q` then :math:`Y_q` (bounded literature-style toy expansions)."""
    ops: list[QubitOperator] = [QubitOperator((), 1.0)]
    for q in range(n_qubits):
        if len(ops) >= max_terms:
            break
        ops.append(QubitOperator(((q, "X"),), 1.0))
        if len(ops) >= max_terms:
            break
        ops.append(QubitOperator(((q, "Y"),), 1.0))
    while len(ops) < max_terms:
        ops.append(QubitOperator((), 1.0))
    return ops[:max_terms]


def resolve_sceom_s_generators(
    *,
    strategy: str,
    hamiltonian: QubitHamiltonian,
    subspace_dim: int,
) -> tuple[list[QubitOperator] | None, str]:
    """Return `(generators_or_none, resolver_label)`. ``None`` means caller should use toy defaults."""

    s = strategy.strip().lower().replace("-", "_")
    if s in {"", "legacy", "default", "pauli_x_toy"}:
        return None, "default_pauli_x_toy"
    if s in {"fermionic_singles_mapped", "fermionic_mapped_singles"}:
        pool = fermionic_singles_generators_matching_h_mapping(hamiltonian)
        k = max(1, int(subspace_dim))
        trimmed = pool[: min(k, len(pool))]
        return trimmed, "fermionic_singles_mapped"
    if s in {"pauli_xy_extended", "pauli_xy_balanced"}:
        k = max(1, int(subspace_dim))
        return sceom_extended_pauli_xy_generators(hamiltonian.n_qubits, k), "pauli_xy_extended"
    raise ValueError(
        "Unknown sceom_generator_strategy; use legacy | fermionic_singles_mapped | pauli_xy_extended."
    )


def run_sceom_nested_commutator(
    hamiltonian: QubitHamiltonian,
    reference_state: np.ndarray,
    *,
    s_generators: list[QubitOperator] | None = None,
    subspace_dim: int | None = None,
    shots_per_matrix_element: int = 0,
    seed: int = 0,
    generator_strategy_yaml: str | None = None,
) -> SCEOMResult:
    """Build ``M_{ij} = \\langle\\psi|[S_i^\\dagger,[H,S_j]]|\\psi\\rangle`` and diagonalize (``V\\approx I`` toy)."""
    n = hamiltonian.n_qubits
    ref = np.asarray(reference_state, dtype=complex).ravel()
    ref = ref / (np.linalg.norm(ref) + 1e-15)
    k_target = subspace_dim or 4
    s_ops = s_generators or default_sceom_pauli_generators(n, k_target)
    k = len(s_ops)
    m_mat = np.zeros((k, k), dtype=float)
    task_meta: list[dict[str, Any]] = []
    for i in range(k):
        for j in range(k):
            op = nested_sceom_q_sc_eom_operator(hamiltonian.operator, s_ops[i], s_ops[j])
            val = expectation_qubit_operator(ref, op, n)
            m_mat[i, j] = float(np.real(val))
            task_meta.append({"i": i, "j": j, "n_operator_terms": len(op.terms)})
    m_mat = (m_mat + m_mat.T) / 2.0
    if shots_per_matrix_element > 0:
        rng = np.random.default_rng(seed)
        scale = 1.0 / math.sqrt(max(1, shots_per_matrix_element))
        nz = rng.normal(0.0, scale, m_mat.shape)
        nz = (nz + nz.T) / 2.0
        m_mat = m_mat + nz
    evals, _ = eigh(m_mat)
    evals = np.sort(np.real(evals))
    sceom_analysis = [
        {
            "state_index": int(i),
            "sz_expectation": 0.0,
            "s2_expectation": 0.0,
            "ground_state_overlap": 0.0,
        }
        for i in range(len(evals))
    ]
    strat_label = generator_strategy_yaml or "legacy_default_pauli_x"
    meta_block: dict[str, Any] = {
        "reference": "10.1039/D2SC05371C (q-sc-EOM M matrix; nested commutator)",
        "subspace_dim": k,
        "construction": (f"M_ij=<psi|[Si,[H,Sj]]|psi>; n_generators={k};strategy={strat_label}"),
        "tasking": task_meta[: min(8, len(task_meta))],
        "shot_noise_model": "symmetric_gaussian_on_real_M"
        if shots_per_matrix_element > 0
        else "none",
        "shots_per_matrix_element": shots_per_matrix_element,
        "sceom_analysis": sceom_analysis,
        "symmetry_filter": "none",
    }
    if generator_strategy_yaml:
        meta_block["generator_strategy_yaml"] = generator_strategy_yaml
    return SCEOMResult(energies=[float(x) for x in evals], meta=meta_block)


def run_sceom_nested_commutator_from_hea(
    hamiltonian: QubitHamiltonian,
    angles: np.ndarray,
    depth: int,
    **kwargs: Any,
) -> SCEOMResult:
    """Reference = HEA state ``|psi(theta)\\rangle`` (same ansatz as pipeline VQE)."""
    ref = hea_state(np.asarray(angles, dtype=float), hamiltonian.n_qubits, depth)
    return run_sceom_nested_commutator(hamiltonian, ref, **kwargs)


def run_sceom_nested_commutator_from_uccsd(
    hamiltonian: QubitHamiltonian,
    angles: np.ndarray,
    prepare_state: Callable[[np.ndarray], np.ndarray],
    **kwargs: Any,
) -> SCEOMResult:
    """Reference = UCCSD state ``|psi(theta)\\rangle`` from ``prepare_state``."""
    ref = np.asarray(prepare_state(np.asarray(angles, dtype=float)), dtype=complex).ravel()
    return run_sceom_nested_commutator(hamiltonian, ref, **kwargs)
