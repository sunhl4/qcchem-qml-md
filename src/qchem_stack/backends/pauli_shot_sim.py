"""Grouped Pauli shot simulation on a statevector (sample-then-recombine convention)."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan
from qchem_stack.backends.pauli_measure_expand import deserialize_basis_key
from qchem_stack.quantum.statevector import _apply_one_qubit_unitary, _pauli_char_to_mat


def _single_qubit_rot_to_z_matrix(axis: str) -> np.ndarray:
    """Clifford ``U`` with ``U P U^\\dagger = Z`` (up to global phase) for ``P \\in \\{X,Y,Z\\}``."""
    if axis in ("I", "Z"):
        return np.eye(2, dtype=complex)
    h = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
    if axis == "X":
        return h
    if axis == "Y":
        sdg = np.array([[1, 0], [0, -1j]], dtype=complex)
        return h @ sdg
    raise ValueError(axis)


def apply_pauli_tensor_basis_to_state(
    state: np.ndarray,
    basis_key: tuple[tuple[int, str], ...],
    n_qubits: int,
) -> np.ndarray:
    """Same single-qubit Cliffords as :func:`basis_change_operations`, left-to-right on tensor axes."""
    axis = ["I"] * n_qubits
    for idx, p in basis_key:
        axis[int(idx)] = p
    out = np.asarray(state, dtype=complex).ravel()
    for q in range(n_qubits):
        u = _single_qubit_rot_to_z_matrix(axis[q])
        if np.allclose(u, np.eye(2)):
            continue
        out = _apply_one_qubit_unitary(out, u, q, n_qubits)
    return out


def _pauli_eigenvalue_on_comp_bit(
    term: tuple[tuple[int, str], ...],
    comp_index: int,
    n_qubits: int,
    basis_key: tuple[tuple[int, str], ...],
) -> float:
    """Eigenvalue of a Pauli word on a computational basis ket after ``basis_key`` rotation."""
    axis = ["I"] * n_qubits
    for idx, p in basis_key:
        axis[int(idx)] = p
    term_d = {int(q): p for q, p in term}
    ev = 1.0
    for q in range(n_qubits):
        p = term_d.get(q, "I")
        if p == "I":
            continue
        b = (comp_index >> q) & 1
        u = _single_qubit_rot_to_z_matrix(axis[q])
        pmat = _pauli_char_to_mat(p)
        upu = u @ pmat @ u.conj().T
        vec = np.zeros(2, dtype=complex)
        vec[b] = 1.0
        ev *= float(np.real(np.vdot(vec, upu @ vec)))
    return ev


def _apply_pauli_word(
    state: np.ndarray,
    term: tuple[tuple[int, str], ...],
    n_qubits: int,
) -> np.ndarray:
    out = np.asarray(state, dtype=complex).ravel()
    for q, p in term:
        out = _apply_one_qubit_unitary(out, _pauli_char_to_mat(str(p)), int(q), n_qubits)
    return out


def _joint_projective_commuting_group_samples(
    psi_hea: np.ndarray,
    coeffs: list[tuple[tuple[tuple[int, str], ...], float]],
    n_qubits: int,
    shots_per_circuit: int,
    rng: np.random.Generator,
    *,
    return_histograms: bool,
    group_id: int,
) -> tuple[list[float], dict[str, Any] | None]:
    """Sample one commuting group by sequential projective measurements.

    For mutually commuting Pauli words, sequential projective measurement samples the
    joint eigenvalue distribution of the group. This provides a real grouped-shot
    path for commuting sets that are not a single tensor-product measurement basis.
    """
    draws: list[float] = []
    eig_counter: Counter[str] = Counter()
    term_order = [str(t) for t, _ in coeffs]
    for _ in range(shots_per_circuit):
        st = np.asarray(psi_hea, dtype=complex).ravel().copy()
        outcomes: list[int] = []
        val = 0.0
        for t, c in coeffs:
            p_st = _apply_pauli_word(st, t, n_qubits)
            exp_val = float(np.real(np.vdot(st, p_st)))
            exp_val = max(-1.0, min(1.0, exp_val))
            outcome = 1 if float(rng.random()) < (1.0 + exp_val) / 2.0 else -1
            projected = st + float(outcome) * p_st
            norm = float(np.linalg.norm(projected))
            if norm <= 1e-14:
                # Numerical guard for probabilities rounded to exactly zero.
                projected = st - float(outcome) * p_st
                norm = float(np.linalg.norm(projected))
                outcome *= -1
            st = projected / (norm + 1e-30)
            outcomes.append(outcome)
            val += c * float(outcome)
        draws.append(val)
        if return_histograms:
            eig_counter[",".join("+" if o > 0 else "-" for o in outcomes)] += 1
    hist = None
    if return_histograms:
        hist = {
            "group_id": group_id,
            "mode": "commuting_joint_projective",
            "pauli_terms": term_order,
            "histogram_eigenvalues": {str(k): int(v) for k, v in eig_counter.items()},
        }
    return draws, hist


def energy_estimate_grouped_shot_simulation(
    psi_hea: np.ndarray,
    hamiltonian: QubitOperator,
    plan: PauliMeasurementPlan,
    n_qubits: int,
    shots_per_circuit: int,
    rng: np.random.Generator,
    *,
    return_histograms: bool = False,
) -> tuple[float, float, dict[str, Any]]:
    """
    Monte Carlo energy: one simultaneous sample per commuting group (when basis is known).

    Returns (mean_energy, stderr_of_mean, meta).
    """
    psi_hea = np.asarray(psi_hea, dtype=complex).ravel()
    dim = 2**n_qubits
    if psi_hea.shape[0] != dim:
        raise ValueError("psi_hea dimension mismatch")

    terms_dict = dict(hamiltonian.terms)
    ident = float(np.real(terms_dict.get((), 0.0)))
    metas = plan.to_circuit_metas()
    group_means: list[float] = []
    per_group_stderr_sq: list[float] = []
    total_shots_used = 0
    histogram_rows: list[dict[str, Any]] = []

    for gid, g in enumerate(plan.groups):
        cmeta = metas[gid] if gid < len(metas) else {}
        bk = deserialize_basis_key(cmeta.get("basis_key"))
        coeffs = [(t, float(np.real(terms_dict[t]))) for t in g]

        if not coeffs:
            continue

        if bk is None:
            draws, hist = _joint_projective_commuting_group_samples(
                psi_hea,
                coeffs,
                n_qubits,
                shots_per_circuit,
                rng,
                return_histograms=return_histograms,
                group_id=gid,
            )
            if hist is not None:
                histogram_rows.append(hist)
            group_means.append(float(np.mean(draws)))
            if len(draws) > 1:
                per_group_stderr_sq.append(float(np.var(draws, ddof=1)) / shots_per_circuit)
            else:
                per_group_stderr_sq.append(0.0)
            total_shots_used += shots_per_circuit
            continue

        psi_r = apply_pauli_tensor_basis_to_state(psi_hea, bk, n_qubits)
        probs = np.abs(psi_r) ** 2
        probs = probs / (np.sum(probs) + 1e-30)
        draws: list[float] = []
        ctr_g: Counter[int] = Counter()
        for _ in range(shots_per_circuit):
            idx = int(rng.choice(dim, p=probs))
            if return_histograms:
                ctr_g[idx] += 1
            val = 0.0
            for t, c in coeffs:
                val += c * _pauli_eigenvalue_on_comp_bit(t, idx, n_qubits, bk)
            draws.append(val)
        if return_histograms:
            histogram_rows.append(
                {
                    "group_id": gid,
                    "mode": "commuting_group",
                    "histogram_comp_index": {str(k): int(v) for k, v in ctr_g.items()},
                }
            )
        group_means.append(float(np.mean(draws)))
        if len(draws) > 1:
            per_group_stderr_sq.append(float(np.var(draws, ddof=1)) / shots_per_circuit)
        else:
            per_group_stderr_sq.append(0.0)
        total_shots_used += shots_per_circuit

    mean_e = ident + float(sum(group_means))
    stderr = math.sqrt(sum(per_group_stderr_sq)) if per_group_stderr_sq else 0.0
    meta_out: dict[str, Any] = {
        "identity_coeff": ident,
        "n_groups_sampled": len(group_means),
        "shot_noise_model": "grouped_simultaneous_or_joint_projective",
        "total_shots_used": int(total_shots_used),
    }
    if return_histograms:
        meta_out["measurement_histogram_rows"] = histogram_rows
    return mean_e, stderr, meta_out
