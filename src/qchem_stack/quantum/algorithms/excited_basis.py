"""Shared basis / Pauli helpers for excited-state algorithms."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_shot_sim import energy_estimate_grouped_shot_simulation
from qchem_stack.contracts.schema_ids import (
    TANGELO_DEFLATION_ANALOGY_V1,
    VQD_CROSS_STACK_SEMANTICS_V1,
)
from qchem_stack.quantum.statevector import hea_state, qubit_operator_to_sparse

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def _gram_schmidt(vectors: list[np.ndarray], *, eps: float = 1e-10) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for v in vectors:
        w = np.asarray(v, dtype=complex).copy()
        for u in out:
            w -= np.vdot(u, w) * u
        nrm = float(np.linalg.norm(w))
        if nrm > eps:
            out.append(w / nrm)
    return out


def build_qse_basis_from_uccsd_reference(
    angles: np.ndarray,
    hamiltonian: QubitHamiltonian,
    prepare_state: Callable[[np.ndarray], np.ndarray],
    *,
    max_basis: int,
) -> list[np.ndarray]:
    """Microscopic subspace: |psi0>, S_k|psi0> with mapped fermionic singles on UCCSD reference."""
    from qchem_stack.quantum.algorithms.sceom import fermionic_singles_generators_matching_h_mapping

    ref = np.asarray(prepare_state(np.asarray(angles, dtype=float)), dtype=complex).ravel()
    ref = ref / (np.linalg.norm(ref) + 1e-15)
    raw = [ref]
    gens = fermionic_singles_generators_matching_h_mapping(hamiltonian)
    n_qubits = hamiltonian.n_qubits
    for gen in gens:
        if len(raw) >= max_basis:
            break
        m = qubit_operator_to_sparse(gen, n_qubits)
        raw.append(m @ ref)
    return _gram_schmidt(raw)[:max_basis]


def _apply_pauli_string(state: np.ndarray, n_qubits: int, qubit: int, letter: str) -> np.ndarray:
    op = QubitOperator(((qubit, letter),), 1.0)
    m = qubit_operator_to_sparse(op, n_qubits)
    return m @ state


def build_qse_basis_from_vqe_hea(
    angles: np.ndarray,
    n_qubits: int,
    depth: int,
    *,
    max_basis: int,
) -> list[np.ndarray]:
    """Microscopic subspace: |psi0>, X_q|psi0> (raw then orthonormalized). McClean-style pool (toy)."""
    g = hea_state(angles, n_qubits, depth)
    g = np.asarray(g, dtype=complex).ravel()
    g = g / (np.linalg.norm(g) + 1e-15)
    raw = [g]
    for q in range(n_qubits):
        raw.append(_apply_pauli_string(g, n_qubits, q, "X"))
    return _gram_schmidt(raw)[:max_basis]


def _overlap_squared_swap_test(
    phi: np.ndarray,
    psi: np.ndarray,
    shots: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Swap-test statistic: ``P(ancilla=0)=(1+|\\langle\\phi|\\psi\\rangle|^2)/2``; return estimate of ``|\\langle\\phi|\\psi\\rangle|^2``."""
    ovl = np.vdot(phi, psi)
    p0 = 0.5 * (1.0 + abs(ovl) ** 2)
    p0 = float(min(1.0, max(0.0, np.real(p0))))
    if shots <= 0:
        return float(abs(ovl) ** 2), 0.0
    k = int(rng.binomial(shots, p0))
    phat = k / shots
    est = 2.0 * phat - 1.0
    stderr = 2.0 * math.sqrt(p0 * (1.0 - p0) / shots)
    return float(est), float(stderr)


def _vqd_three_protocol_channels(
    prev_states: list[np.ndarray],
    g_new: np.ndarray,
    h_op: QubitOperator,
    n_qubits: int,
    penalty_weight: float,
    *,
    shots_objective: int,
    shots_overlap: int,
    shots_weight: int,
    rng: np.random.Generator,
    pauli_grouping: str = "tensor_product",
) -> dict[str, Any]:
    """Three-channel reporting model: Hamiltonian expectation, overlap(s), deflation weight (product)."""
    g_new = np.asarray(g_new, dtype=complex).ravel()
    g_new = g_new / (np.linalg.norm(g_new) + 1e-15)
    h_dense = qubit_operator_to_sparse(h_op, n_qubits)
    e_ex = float(np.real(np.vdot(g_new, h_dense @ g_new)))
    obj: dict[str, Any] = {
        "energy_exact": e_ex,
        "shots_budget_objective": int(max(0, shots_objective)),
    }
    if shots_objective > 0:
        plan = build_measurement_plan(h_op, n_qubits, grouping=pauli_grouping)  # type: ignore[arg-type]
        m, se, _ = energy_estimate_grouped_shot_simulation(
            g_new, h_op, plan, n_qubits, shots_objective, rng
        )
        obj["energy_shot_mean"] = float(m)
        obj["energy_shot_stderr"] = float(se)
    overlap_ex = float(sum(abs(np.vdot(s, g_new)) ** 2 for s in prev_states))
    ov: dict[str, Any] = {
        "overlap_squared_sum_exact": overlap_ex,
        "shots_per_pair": int(max(0, shots_overlap)),
    }
    if shots_overlap > 0 and prev_states:
        est_sum = 0.0
        se_sq = 0.0
        for s in prev_states:
            e2, se2 = _overlap_squared_swap_test(s, g_new, shots_overlap, rng)
            est_sum += e2
            se_sq += se2 * se2
        ov["overlap_squared_sum_shot_mean"] = float(est_sum)
        ov["overlap_squared_sum_shot_stderr"] = float(math.sqrt(se_sq))
    w_ex = penalty_weight * overlap_ex
    wt: dict[str, Any] = {
        "penalty_weight": penalty_weight,
        "weight_exact": float(w_ex),
        "shots_budget_weight": int(max(0, shots_weight)),
    }
    if (
        shots_weight > 0
        and shots_overlap > 0
        and prev_states
        and "overlap_squared_sum_shot_mean" in ov
    ):
        wt["weight_shot_mean"] = float(penalty_weight * ov["overlap_squared_sum_shot_mean"])
        wt["weight_shot_stderr"] = float(penalty_weight * ov["overlap_squared_sum_shot_stderr"])
    return {"objective": obj, "overlap": ov, "weight": wt}


def vqd_cross_stack_semantics_meta(
    *,
    penalty_weight: float,
    penalty_weights_resolved: list[float],
    overlap_mode: str,
) -> dict[str, Any]:
    """Cross-stack narrative hooks for VQD reporting (parity / Methods export)."""
    coeff = (
        float(penalty_weights_resolved[0]) if penalty_weights_resolved else float(penalty_weight)
    )
    overlap_repr = (
        "statevector_amplitude_overlap"
        if overlap_mode == "statevector_overlap"
        else "statevector_overlap_with_tangelo_circuit_analogy_reporting"
    )
    return {
        "tangelo_deflation_analogy_v1": {
            "schema": TANGELO_DEFLATION_ANALOGY_V1,
            "deflation_coeff_yaml": coeff,
            "penalty_schedule_resolved": list(penalty_weights_resolved),
            "selected_overlap_mode": overlap_mode,
            "open_stack_overlap_representation": overlap_repr,
            "tangelo_deflation_circuits_analogy": (
                "Tangelo VQESolver adds deflation via deflation_circuits + deflation_coeff "
                "on measured overlaps; this stack collapses overlaps into one classical objective."
            ),
        },
        "vqd_cross_stack_semantics_v1": {
            "schema": VQD_CROSS_STACK_SEMANTICS_V1,
            "optimization_model": "single_objective_collapsed",
            "three_protocol_role": "reporting_and_optional_shots_not_triple_optimizer",
            "note": (
                "Closed vendor AlgorithmVQD exposes separate ExpectationValue / OverlapSquared "
                "computables; open stack matches Higgott et al. scalar penalty + optional "
                "Pauli/swap-test channels."
            ),
        },
    }
