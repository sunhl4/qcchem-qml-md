"""Shared basis / Pauli helpers for excited-state algorithms."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, cast

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
    expansion_pool: str = "fermionic_singles",
) -> list[np.ndarray]:
    """Microscopic subspace: |psi0> plus mapped fermionic singles (optional doubles)."""
    from qchem_stack.chem.kernels.spin_ucc import build_spin_uccsd_fermion_generators
    from qchem_stack.quantum.algorithms.sceom import fermionic_singles_generators_matching_h_mapping
    from qchem_stack.quantum.algorithms.uccsd_mapping import map_fermion_generator

    ref = np.asarray(prepare_state(np.asarray(angles, dtype=float)), dtype=complex).ravel()
    ref = ref / (np.linalg.norm(ref) + 1e-15)
    raw = [ref]
    n_qubits = hamiltonian.n_qubits
    pool = expansion_pool.strip().lower()
    if pool in {"fermionic_singles", "singles"}:
        gens = fermionic_singles_generators_matching_h_mapping(hamiltonian)
    elif pool in {"fermionic_singles_doubles", "singles_doubles"}:
        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("fermionic_singles_doubles requires hamiltonian.fermion_space")
        mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map", "jordan_wigner")
        mapping = str(mapping_raw)
        ferm_ops = build_spin_uccsd_fermion_generators(int(fs.n_spin_orbitals), int(fs.n_electrons))
        gens = [map_fermion_generator(f, mapping) for f in ferm_ops]
    else:
        raise ValueError(f"unknown QSE expansion_pool: {expansion_pool!r}")
    for gen in gens:
        if len(raw) >= max_basis:
            break
        m = qubit_operator_to_sparse(gen, n_qubits)
        raw.append(m @ ref)
    return _gram_schmidt(raw)[:max_basis]


def _apply_pauli_string(state: np.ndarray, n_qubits: int, qubit: int, letter: str) -> np.ndarray:
    op = QubitOperator(((qubit, letter),), 1.0)
    m = qubit_operator_to_sparse(op, n_qubits)
    return cast("np.ndarray", m @ state)


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


def _vqd_objective_computable(
    prev_states: list[np.ndarray],
    g_new: np.ndarray,
    h_op: QubitOperator,
    n_qubits: int,
    *,
    shots_objective: int,
    rng: np.random.Generator,
    pauli_grouping: str = "tensor_product",
) -> dict[str, Any]:
    """Objective channel (ExpectationValue analog) for VQD three-computable mode."""
    return cast(
        "dict[str, Any]",
        _vqd_three_protocol_channels(
            prev_states,
            g_new,
            h_op,
            n_qubits,
            0.0,
            shots_objective=shots_objective,
            shots_overlap=0,
            shots_weight=0,
            rng=rng,
            pauli_grouping=pauli_grouping,
        )["objective"],
    )


def _vqd_overlap_computable(
    prev_states: list[np.ndarray],
    g_new: np.ndarray,
    h_op: QubitOperator,
    n_qubits: int,
    *,
    shots_overlap: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Overlap channel (OverlapSquared analog) for VQD three-computable mode."""
    return cast(
        "dict[str, Any]",
        _vqd_three_protocol_channels(
            prev_states,
            g_new,
            h_op,
            n_qubits,
            0.0,
            shots_objective=0,
            shots_overlap=shots_overlap,
            shots_weight=0,
            rng=rng,
        )["overlap"],
    )


def _vqd_weight_computable(
    prev_states: list[np.ndarray],
    g_new: np.ndarray,
    h_op: QubitOperator,
    n_qubits: int,
    penalty_weight: float,
    *,
    shots_overlap: int,
    shots_weight: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Weight channel for VQD three-computable mode."""
    return cast(
        "dict[str, Any]",
        _vqd_three_protocol_channels(
            prev_states,
            g_new,
            h_op,
            n_qubits,
            penalty_weight,
            shots_objective=0,
            shots_overlap=shots_overlap,
            shots_weight=shots_weight,
            rng=rng,
        )["weight"],
    )


def vqd_deflation_swap_test_circuit_sketch(*, n_system_qubits: int) -> dict[str, Any]:
    """Open-stack swap-test CircuitIR for ``overlap_mode: deflation_circuit`` (reference |phi>, trial |psi>)."""
    n = int(n_system_qubits)
    anc = 2 * n
    n_total = 2 * n + 1
    ops: list[dict[str, Any]] = [
        {"name": "H", "qubits": [anc], "params": {}},
    ]
    for k in range(n):
        ops.append({"name": "CSWAP", "qubits": [anc, k, n + k], "params": {}})
    ops.append({"name": "MEASURE", "qubits": [anc], "params": {}})
    return {
        "schema": "vqd_deflation_swap_test_circuit_sketch_v1",
        "n_qubits": n_total,
        "n_system_qubits": n,
        "ancilla_qubit": anc,
        "reference_qubits": list(range(n)),
        "trial_qubits": list(range(n, 2 * n)),
        "operations": ops,
        "boxes": ["PrepareReference", "PrepareTrial", "SwapTest", "MeasureAncilla"],
        "note": (
            "Fredkin-style swap test on paired reference/trial registers; "
            "optimization still uses statevector overlap unless VQD shot budgets are set."
        ),
    }


def vqd_cross_stack_semantics_meta(
    *,
    penalty_weight: float,
    penalty_weights_resolved: list[float],
    overlap_mode: str,
    optimizer_mode: str = "collapsed",
    n_system_qubits: int | None = None,
) -> dict[str, Any]:
    """Cross-stack narrative hooks for VQD reporting (parity / Methods export)."""
    coeff = (
        float(penalty_weights_resolved[0]) if penalty_weights_resolved else float(penalty_weight)
    )
    if overlap_mode == "statevector_overlap":
        overlap_repr = "statevector_amplitude_overlap"
    elif overlap_mode == "deflation_circuit":
        overlap_repr = "deflation_circuit_recipe_with_circuit_ir_sketch"
    else:
        overlap_repr = "statevector_overlap_with_circuit_analogy_reporting"
    deflation_block: dict[str, Any] = {
        "schema": TANGELO_DEFLATION_ANALOGY_V1,
        "deflation_coeff_yaml": coeff,
        "penalty_schedule_resolved": list(penalty_weights_resolved),
        "selected_overlap_mode": overlap_mode,
        "open_stack_overlap_representation": overlap_repr,
        "deflation_circuits_analogy": (
            "Reference stacks add deflation via deflation_circuits + deflation_coeff "
            "on measured overlaps; this stack collapses overlaps into one classical objective."
        ),
    }
    if overlap_mode == "deflation_circuit":
        recipe: dict[str, Any] = {
            "schema": "vqd_deflation_circuit_recipe_v1",
            "note": (
                "Deflation-circuit analogy with open-stack swap-test CircuitIR sketch; "
                "optimization still uses statevector overlap unless shot budgets are set."
            ),
            "steps": [
                "prepare_excited_ansatz",
                "apply_deflation_projectors_from_previous_states",
                "measure_overlap_squared_on_device",
            ],
        }
        if n_system_qubits is not None and n_system_qubits >= 1:
            sketch = vqd_deflation_swap_test_circuit_sketch(n_system_qubits=int(n_system_qubits))
            recipe["circuit_ir_sketch_v1"] = sketch
            try:
                from qchem_stack.backends.vqd_deflation_qiskit import (
                    deflation_swap_test_qiskit_export_v1,
                )

                recipe["qiskit_export_v1"] = deflation_swap_test_qiskit_export_v1(
                    n_system_qubits=int(n_system_qubits)
                )
            except ImportError:
                pass
        deflation_block["deflation_circuit_recipe_v1"] = recipe
    opt_model = (
        "three_computable_decoupled_channels"
        if optimizer_mode == "three_computable"
        else "single_objective_collapsed"
    )
    return {
        "tangelo_deflation_analogy_v1": deflation_block,
        "vqd_cross_stack_semantics_v1": {
            "schema": VQD_CROSS_STACK_SEMANTICS_V1,
            "optimization_model": opt_model,
            "three_protocol_role": (
                "optimizer_channels_when_three_computable"
                if optimizer_mode == "three_computable"
                else "reporting_and_optional_shots_not_triple_optimizer"
            ),
            "note": (
                "Closed vendor AlgorithmVQD exposes separate ExpectationValue / OverlapSquared "
                "computables; open stack matches Higgott et al. scalar penalty + optional "
                "Pauli/swap-test channels."
            ),
        },
    }
