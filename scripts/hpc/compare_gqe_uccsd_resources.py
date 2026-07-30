#!/usr/bin/env python3
"""Compute GQE vs standard UCCSD-VQE circuit / Pauli-pool resource metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from openfermion import jordan_wigner
from openfermion.ops import FermionOperator, QubitOperator

from qchem_stack.backends.spec import _depth_estimate, _twoq_gate_count
from qchem_stack.chem.kernels.spin_ucc import (
    build_spin_uccsd_fermion_generators,
    count_uccsd_excitations,
)
from qchem_stack.quantum.algorithms.uccsd_mapping import map_fermion_generator
from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import pauli_rotation_elementary_ops

REPO = Path(__file__).resolve().parents[2]

PAPER_TIME_GRID = [2**k / 320 for k in range(6)] + [-(2**k) / 320 for k in range(6)]

SPECS: dict[str, dict[str, int]] = {
    "h2": dict(nso=4, ne=2, seq=10, ep=200),
    "lih": dict(nso=10, ne=2, seq=40, ep=1000),
    "beh2": dict(nso=12, ne=4, seq=60, ep=1500),
    "n2": dict(nso=12, ne=6, seq=100, ep=1500),
}

HAMILTONIAN_EST = {
    "h2": dict(n_h=15, n_groups=8),
    "lih": dict(n_h=1850, n_groups=420),
    "beh2": dict(n_h=2500, n_groups=550),
    "n2": dict(n_h=3200, n_groups=680),
}

SHOTS_PER_GROUP = 2048
WARMUP = 200
N_SAMPLE = 50


def _pauli_string_from_term(term: tuple[tuple[int, str], ...], nq: int) -> str:
    s = ["I"] * nq
    for i, p in term:
        s[int(i)] = str(p)
    return "".join(s)


def _hermitian_pauli_pool(nso: int, ne: int) -> list[str]:
    """GQE appendix A.2: unique Hermitian Pauli strings from JW(UCCSD fermion pool)."""
    seen: dict[tuple[Any, ...], float] = {}
    for fop in build_spin_uccsd_fermion_generators(nso, ne):
        for term, coeff in jordan_wigner(fop).terms.items():
            if not term:
                continue
            c = complex(coeff)
            mag = float(np.real(c)) if abs(np.real(c)) > 1e-14 else float(np.imag(c))
            if abs(mag) < 1e-14:
                continue
            sign = 1.0 if mag >= 0 else -1.0
            if term not in seen:
                seen[term] = sign
    return [
        _pauli_string_from_term(term, nso)
        for term, _ in sorted(seen.items(), key=lambda kv: str(kv[0]))
    ]


def _antihermitian_qubit_operator(fop: FermionOperator, *, nso: int) -> QubitOperator:
    qop = map_fermion_generator(fop, "jordan_wigner", n_spin_orbitals=nso)
    adj = QubitOperator()
    for term, coeff in qop.terms.items():
        adj += QubitOperator(term, np.conj(coeff))
    return qop - adj


def _count_ops(ops: list[dict[str, Any]], nq: int) -> dict[str, float]:
    return {
        "n_ops": float(len(ops)),
        "n1": float(
            sum(
                1
                for o in ops
                if o.get("name") in ("H", "S", "SDG", "SX", "SXDG", "X", "Y", "Z", "RZ", "RX", "RY")
            )
        ),
        "n2": float(_twoq_gate_count(ops, "CX")),
        "depth": float(_depth_estimate(ops, nq)),
    }


def _single_pauli_token_stats(ps: str, nq: int) -> dict[str, float]:
    return _count_ops(pauli_rotation_elementary_ops(ps, 0.05), nq)


def _cluster_circuit_stats(fop: FermionOperator, *, nso: int, nq: int) -> dict[str, Any]:
    aop = _antihermitian_qubit_operator(fop, nso=nso)
    pauli_terms: list[tuple[str, complex]] = []
    for term, coeff in aop.terms.items():
        if not term:
            continue
        c = complex(coeff)
        if abs(c.imag) < 1e-12:
            continue
        pauli_terms.append((_pauli_string_from_term(term, nq), c))

    all_ops: list[dict[str, Any]] = []
    for ps, coeff in pauli_terms:
        phi = float(-2.0 * np.imag(0.1 * coeff))
        if abs(phi) < 1e-14:
            continue
        all_ops.extend(pauli_rotation_elementary_ops(ps, phi))
    stats = _count_ops(all_ops, nq)
    weights = [sum(c != "I" for c in ps) for ps, _ in pauli_terms]
    return {
        **stats,
        "n_pauli_rotations": float(len(pauli_terms)),
        "pauli_weight_mean": float(np.mean(weights)) if weights else 0.0,
        "pauli_weight_max": float(max(weights)) if weights else 0.0,
    }


def _agg(
    rows: list[dict[str, float]], keys: list[str]
) -> tuple[dict[str, float], dict[str, float]]:
    avg = {k: float(np.mean([r[k] for r in rows])) for k in keys}
    mx = {k: float(np.max([r[k] for r in rows])) for k in keys}
    return avg, mx


def compute_molecule(mid: str, spec: dict[str, int]) -> dict[str, Any]:
    nso, ne = int(spec["nso"]), int(spec["ne"])
    nq = nso
    seq = int(spec["seq"])
    epochs = int(spec["ep"])
    ferm_ops = build_spin_uccsd_fermion_generators(nso, ne)
    exc = count_uccsd_excitations(nso, ne)

    # --- GQE pool (Pauli strings × time grid) ---
    pstrings = _hermitian_pauli_pool(nso, ne)
    weights = [sum(c != "I" for c in ps) for ps in pstrings]
    token_rows = [_single_pauli_token_stats(ps, nq) for ps in pstrings]
    tok_avg, tok_max = _agg(token_rows, ["n_ops", "n1", "n2", "depth"])

    gqe_eval = {k: round(tok_avg[k] * seq, 1) for k in tok_avg}
    gqe_eval_max = {k: round(tok_max[k] * seq, 1) for k in tok_max}

    # --- UCCSD-VQE: one full product layer exp(θ_k A_k) ---
    cluster_rows = [_cluster_circuit_stats(fop, nso=nso, nq=nq) for fop in ferm_ops]
    cl_avg, cl_max = _agg(cluster_rows, ["n_ops", "n1", "n2", "depth", "n_pauli_rotations"])
    uccsd_layer = {k: round(cl_avg[k] * len(ferm_ops), 1) for k in ["n_ops", "n1", "n2", "depth"]}
    uccsd_layer_max = {
        k: round(cl_max[k] * len(ferm_ops), 1) for k in ["n_ops", "n1", "n2", "depth"]
    }
    uccsd_pauli_rots = int(round(cl_avg["n_pauli_rotations"] * len(ferm_ops)))

    n_eval_gqe = WARMUP + epochs * N_SAMPLE
    ham = HAMILTONIAN_EST[mid]
    shots_per_eval = ham["n_groups"] * SHOTS_PER_GROUP

    return {
        "n_qubits": nq,
        "n_electrons_cas": ne,
        "n_orbitals_cas": nso // 2,
        "uccsd": {
            "n_fermion_generators": len(ferm_ops),
            "n_single_excitations": exc["n_single_excitations"],
            "n_double_excitations": exc["n_double_excitations"],
            "n_variational_parameters": len(ferm_ops),
            "per_cluster_pauli_rotations_avg": round(cl_avg["n_pauli_rotations"], 2),
            "per_cluster_pauli_rotations_max": round(cl_max["n_pauli_rotations"], 0),
            "per_cluster_cx_avg": round(cl_avg["n2"], 2),
            "per_cluster_depth_avg": round(cl_avg["depth"], 2),
            "per_eval_ansatz_one_layer_avg": uccsd_layer,
            "per_eval_ansatz_one_layer_max": uccsd_layer_max,
            "total_pauli_rotations_one_layer": uccsd_pauli_rots,
            "note": (
                "Standard dense UCCSD-VQE: one energy eval = HF prep + "
                "∏_k exp(θ_k(T_k-T_k†)) with N_gen cluster exponentials; "
                "each cluster = ordered product of single-Pauli rotations (JW)."
            ),
        },
        "gqe": {
            "n_pauli_strings": len(pstrings),
            "vocab": 1 + len(pstrings) * len(PAPER_TIME_GRID),
            "seq_len": seq,
            "pauli_weight_min": int(min(weights)),
            "pauli_weight_max": int(max(weights)),
            "pauli_weight_mean": round(float(np.mean(weights)), 2),
            "per_token_single_pauli_avg": {k: round(tok_avg[k], 4) for k in tok_avg},
            "per_token_single_pauli_max": {k: round(tok_max[k], 4) for k in tok_max},
            "per_eval_ansatz_avg": gqe_eval,
            "per_eval_ansatz_max": gqe_eval_max,
            "n_energy_evals_training": n_eval_gqe,
            "note": "Each GQE token = one exp(i*t*P) for a single Pauli string P (paper pool A.2)",
        },
        "shared_hamiltonian_measurement": {
            "hamiltonian_pauli_terms_est": ham["n_h"],
            "measurement_groups_tp_est": ham["n_groups"],
            "shots_per_group": SHOTS_PER_GROUP,
            "shots_per_energy_eval": shots_per_eval,
            "note": "Identical for GQE and UCCSD — energy measurement depends only on H, not ansatz.",
        },
        "comparison_per_energy_eval": {
            "ansatz_cx_gqe": gqe_eval["n2"],
            "ansatz_cx_uccsd": uccsd_layer["n2"],
            "ansatz_cx_ratio_gqe_over_uccsd": round(
                gqe_eval["n2"] / max(uccsd_layer["n2"], 1e-9), 2
            ),
            "ansatz_depth_gqe": gqe_eval["depth"],
            "ansatz_depth_uccsd": uccsd_layer["depth"],
            "ansatz_depth_ratio_gqe_over_uccsd": round(
                gqe_eval["depth"] / max(uccsd_layer["depth"], 1e-9), 2
            ),
            "pauli_rotations_gqe_tokens": seq,
            "pauli_rotations_uccsd_one_layer": uccsd_pauli_rots,
            "pool_fermion_generators": len(ferm_ops),
            "pool_pauli_strings_gqe": len(pstrings),
            "vocab_expansion_factor": round((1 + len(pstrings) * 12) / max(len(ferm_ops), 1), 1),
        },
        # flat aliases for legacy plot script
        "n_pauli_strings": len(pstrings),
        "vocab": 1 + len(pstrings) * len(PAPER_TIME_GRID),
        "seq_len": seq,
        "pauli_weight_min": int(min(weights)),
        "pauli_weight_max": int(max(weights)),
        "pauli_weight_mean": round(float(np.mean(weights)), 2),
        "per_token_single_pauli_avg": {k: round(tok_avg[k], 4) for k in tok_avg},
        "per_token_single_pauli_max": {k: round(tok_max[k], 4) for k in tok_max},
        "per_eval_ansatz_avg": gqe_eval,
        "per_eval_ansatz_max": gqe_eval_max,
        "n_energy_evals_training": n_eval_gqe,
        "hamiltonian_pauli_terms_est": ham["n_h"],
        "measurement_groups_tp_est": ham["n_groups"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "results/gqe_circuit_metrics.json",
    )
    args = parser.parse_args()

    results = {mid: compute_molecule(mid, spec) for mid, spec in SPECS.items()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
