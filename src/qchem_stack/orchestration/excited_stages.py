"""Excited-state stages (VQD / QSE / SCEOM) after variational ground state."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ExperimentConfig
from qchem_stack.orchestration.run_context import PipelineStageTimer
from qchem_stack.quantum.algorithms.excited import QSE, VQD

def excited_protocol_contract_v1_block() -> dict[str, Any]:
    """Stable documentation slice for parity / Methods (shot semantics mirror YAML + implementation)."""

    return {
        "schema": "excited_protocol_contract_v1",
        "vqd_three_protocol": (
            "`objective`: deflation energy channel (exact statevector expectation or grouped Pauli when "
            "`vqd_shots_objective`>0). `overlap`: swap-test overlaps between solved levels when "
            "`vqd_shots_overlap`>0. `weight`: reserved coupling to overlap shot budget."
        ),
        "qse_shot_modes": {
            "exact": (
                "Dense Hamiltonian projected into QSE basis built from HEA single-reference determinants/"
                "excitations."
            ),
            "gaussian_h": (
                "`qse_shots_per_matrix_element` injects symmetric Gaussian noise on real parts of dense "
                "matrix elements — placeholder shot model vs device POVM."
            ),
            "pauli_transitions": (
                "Per-(i,j) transition channel built from Pauli transition strings; budgets via "
                "`qse_shots_per_ij_term` × schedule task count (`qse_total_shots_upper_bound`)."
            ),
        },
        "sceom_shot_semantics": (
            "When `sceom_shots_per_matrix_element`>0, apply symmetric Gaussian noise to real diagonal/"
            "off-diagonal entries of the nested-commutator matrix before GHEP (open-stack SCEOM prototype)."
        ),
    }


def build_excited_resource_summary_for_export(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """VQD / QSE / SCEOM shot book-keeping from YAML only (for ``export_parity_criteria_table`` without a run)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational:
        er["qse"] = {
            "shot_mode": q.qse_shot_mode,
            "qse_shots_per_matrix_element_yaml": q.qse_shots_per_matrix_element,
            "qse_shots_per_ij_term_yaml": q.qse_shots_per_ij_term,
        }
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = excited_protocol_contract_v1_block()
    return er


def build_excited_resource_summary(
    cfg: ExperimentConfig,
    out: dict[str, Any],
) -> dict[str, Any] | None:
    """YAML + run meta for Methods-style shot/task accounting (VQD / QSE / SCEOM stages)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational and "qse" in out:
        meta = out["qse"].get("meta") or {}
        block: dict[str, Any] = {"shot_mode": q.qse_shot_mode, "K": meta.get("K")}
        sched = meta.get("qse_pauli_transition_schedule")
        if isinstance(sched, dict):
            block["n_transition_tasks"] = sched.get("n_transition_tasks")
            block["total_shots_upper_bound"] = sched.get("total_shots_upper_bound")
            block["n_pauli_terms_in_schedule"] = sched.get("n_pauli_terms")
        if q.qse_shot_mode == "gaussian_h":
            k = meta.get("K")
            if isinstance(k, int) and k > 0:
                block["h_matrix_elements"] = k * k
                block["gaussian_h_shots_budget_reference"] = k * k * q.qse_shots_per_matrix_element
        if q.qse_shot_mode == "pauli_transitions":
            block["shots_per_ij_term_yaml"] = q.qse_shots_per_ij_term
        er["qse"] = {k2: v for k2, v in block.items() if v is not None}
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = excited_protocol_contract_v1_block()
    return er


def vqd_channel_upper(v: dict[str, Any]) -> int:
    n = 0
    pairs = int(v.get("swap_test_pair_count_if_shots") or 0)
    sov = int(v.get("shots_overlap_per_pair") or 0)
    n += pairs * sov
    levels = int(v.get("deflated_cobyla_levels") or 0)
    obj = int(v.get("shots_objective_per_reporting_level") or 0)
    n += levels * obj
    sw = int(v.get("shots_weight_channel") or 0)
    if sw > 0 and sov > 0:
        n += levels * sw
    return n


def qse_channel_upper(qs: dict[str, Any]) -> int:
    tub = qs.get("total_shots_upper_bound")
    if isinstance(tub, (int, float)) and tub > 0:
        return int(tub)
    gref = qs.get("gaussian_h_shots_budget_reference")
    if isinstance(gref, (int, float)) and gref > 0:
        return int(gref)
    nt = qs.get("n_transition_tasks")
    sp = qs.get("shots_per_ij_term_yaml")
    if (
        isinstance(nt, (int, float))
        and isinstance(sp, (int, float))
        and int(nt) > 0
        and int(sp) > 0
    ):
        return int(nt) * int(sp)
    return 0


def sceom_channel_upper(sc: dict[str, Any]) -> int:
    m = int(sc.get("m_matrix_elements") or 0)
    sp = int(sc.get("shots_per_matrix_element_yaml") or 0)
    if m > 0 and sp > 0:
        return m * sp
    return 0


def excited_shot_channel_upper_bounds(excited: dict[str, Any]) -> dict[str, int]:
    """Per-channel upper bounds (VQD / QSE / SCEOM) for Methods one-table accounting."""
    out: dict[str, int] = {"vqd": 0, "qse": 0, "sceom": 0, "combined": 0}
    v = excited.get("vqd")
    if isinstance(v, dict):
        out["vqd"] = vqd_channel_upper(v)
    qs = excited.get("qse")
    if isinstance(qs, dict):
        out["qse"] = qse_channel_upper(qs)
    sc = excited.get("sceom")
    if isinstance(sc, dict):
        out["sceom"] = sceom_channel_upper(sc)
    out["combined"] = int(out["vqd"] + out["qse"] + out["sceom"])
    return out


def excited_shots_upper_bound(excited: dict[str, Any]) -> int:
    """Conservative additive upper bound on shot-like budgets declared for excited stages (YAML + QSE schedule)."""
    b = excited_shot_channel_upper_bounds(excited)
    return int(b["combined"])


def excited_methods_unified(excited_rs: dict[str, Any]) -> dict[str, Any]:
    """Single export shape for VQD / QSE / SCEOM (Methods one-block)."""
    return {
        "schema_version": "1",
        "vqd": excited_rs.get("vqd"),
        "qse": excited_rs.get("qse"),
        "sceom": excited_rs.get("sceom"),
        "shot_channel_upper_bounds": excited_rs.get("shot_channel_upper_bounds"),
    }

def run_excited_stages(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    exe: Any,
    angles: Any,
    energy_pre: float,
    out: dict[str, Any],
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any] | None:
    q = cfg.quantum
    ang = np.asarray(angles, dtype=float)
    if q.vqd_after_variational:
        prepare_state = None
        n_vp: int | None = None
        param_bounds: list[tuple[float, float]] | None = None
        if q.variational_ansatz == "uccsd":
            from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

            if q.uccsd_trotter_steps is not None:
                ucc = UCCSDTrotterVQE(
                    qh,
                    executor=exe,
                    n_trotter_steps=int(q.uccsd_trotter_steps),
                )
            else:
                ucc = UCCSDVQE(qh, executor=exe)
            prepare_state = ucc.prepare_state
            n_vp = int(ucc.n_params)
            param_bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * n_vp
        vqd = VQD(
            qh,
            n_states=q.vqd_n_states,
            depth=q.vqe_depth,
            penalty_weight=q.vqd_penalty_weight,
            penalty_weights=q.vqd_penalty_weights,
            overlap_exponent=q.vqd_overlap_exponent,
            cobyla_maxiter=q.vqd_cobyla_maxiter,
            optimizer_method=q.vqd_optimizer_method,
            prepare_state=prepare_state,
            n_var_parameters=n_vp,
            parameter_bounds=param_bounds,
            init_strategy=q.vqd_init_strategy,
            init_noise_scale=q.vqd_init_noise_scale,
            max_overlap_warn=q.vqd_max_overlap_warn,
            overlap_mode=q.vqd_overlap_mode,
            executor=exe,
        )
        vqd_res = vqd.run(
            seed=cfg.random_seed,
            shots_objective=q.vqd_shots_objective,
            shots_overlap=q.vqd_shots_overlap,
            shots_weight=q.vqd_shots_weight,
            pauli_grouping=q.pauli_grouping,
            ground_angles=ang,
            ground_energy=float(energy_pre),
        )
        out["vqd"] = {
            "schema": "excited_vqd_bundle_v1",
            "energies": vqd_res.energies,
            "meta": vqd_res.meta,
        }
    if q.qse_after_variational:
        qse = QSE(qh, subspace_dim=q.qse_subspace_dim)
        kb = q.qse_max_basis
        if q.qse_shot_mode == "exact":
            qse_res = qse.run_from_vqe_hea_basis(ang, q.vqe_depth, max_basis=kb)
        elif q.qse_shot_mode == "gaussian_h":
            qse_res = qse.run_from_vqe_hea_basis_shot_noise(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_matrix_element=q.qse_shots_per_matrix_element,
                seed=cfg.random_seed,
            )
        else:
            qse_res = qse.run_from_vqe_hea_basis_pauli_transitions(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_ij_term=q.qse_shots_per_ij_term,
                seed=cfg.random_seed,
            )
        qse_meta = dict(qse_res.meta)
        qse_meta["qse_shot_mode"] = q.qse_shot_mode
        out["qse"] = {
            "schema": "excited_qse_bundle_v1",
            "excitation_energies": qse_res.excitation_energies,
            "meta": qse_meta,
        }
    if q.sceom_after_variational:
        from qchem_stack.quantum.algorithms.sceom import (
            resolve_sceom_s_generators,
            run_sceom_nested_commutator_from_hea,
        )

        sceom_kw: dict[str, Any] = {}
        gens, _ = resolve_sceom_s_generators(
            strategy=q.sceom_generator_strategy,
            hamiltonian=qh,
            subspace_dim=q.sceom_subspace_dim,
        )
        if gens is not None:
            sceom_kw["s_generators"] = gens
        sceom_kw["generator_strategy_yaml"] = q.sceom_generator_strategy
        sceom_res = run_sceom_nested_commutator_from_hea(
            qh,
            ang,
            q.vqe_depth,
            subspace_dim=q.sceom_subspace_dim,
            shots_per_matrix_element=q.sceom_shots_per_matrix_element,
            seed=cfg.random_seed,
            **sceom_kw,
        )
        out["sceom"] = {
            "schema": "excited_sceom_bundle_v1",
            "energies": sceom_res.energies,
            "meta": sceom_res.meta,
        }
    excited_rs = build_excited_resource_summary(cfg, out)
    if excited_rs is not None:
        out["excited_resource_summary"] = excited_rs
    profile.mark("excited_stages")
    emit("excited_stages")
    return excited_rs

