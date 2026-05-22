"""Excited-stage resource summaries and shot upper-bound accounting."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from qchem_stack.config.quantum_helpers import (
    excited_any_after_variational,
    excited_qse_after_variational,
    excited_qse_plugin_params,
    excited_sceom_after_variational,
    excited_sceom_plugin_params,
    excited_vqd_after_variational,
    excited_vqd_plugin_params,
)
from qchem_stack.contracts.schema_ids import EXCITED_PROTOCOL_CONTRACT_V1
from qchem_stack.orchestration.excited_stages_types import (
    ExcitedProtocolContractV1,
    ExcitedResourceSummary,
    ExcitedShotChannelBounds,
    QseResourceBlock,
    SceomResourceBlock,
    VqdResourceBlock,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def excited_protocol_contract_v1_block() -> ExcitedProtocolContractV1:
    return {
        "schema": EXCITED_PROTOCOL_CONTRACT_V1,
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


def _vqd_resource_block(cfg: ExperimentConfig) -> VqdResourceBlock:
    p = excited_vqd_plugin_params(cfg)
    ns = int(p["n_states"])
    n_exc = max(0, ns - 1)
    n_pairs = n_exc * (n_exc + 1) // 2
    shots_overlap = int(p["shots_overlap"])
    return VqdResourceBlock(
        n_states=ns,
        shots_objective_per_reporting_level=int(p["shots_objective"]),
        shots_overlap_per_pair=shots_overlap,
        shots_weight_channel=int(p["shots_weight"]),
        deflated_cobyla_levels=n_exc,
        swap_test_pair_count_if_shots=n_pairs if shots_overlap > 0 else 0,
    )


def _qse_resource_block_from_config(cfg: ExperimentConfig) -> QseResourceBlock:
    p = excited_qse_plugin_params(cfg)
    return cast(
        "QseResourceBlock",
        {
            "shot_mode": str(p["shot_mode"]),
            "qse_shots_per_matrix_element_yaml": p["shots_per_matrix_element"],
            "qse_shots_per_ij_term_yaml": p["shots_per_ij_term"],
        },
    )


def _sceom_resource_block(cfg: ExperimentConfig) -> SceomResourceBlock:
    p = excited_sceom_plugin_params(cfg)
    k = int(p["subspace_dim"])
    return SceomResourceBlock(
        generator_count_k=k,
        m_matrix_elements=k * k,
        shots_per_matrix_element_yaml=int(p["shots_per_matrix_element"]),
    )


def _finalize_excited_resource_summary(er: ExcitedResourceSummary) -> ExcitedResourceSummary:
    ch = excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = excited_protocol_contract_v1_block()
    return er


def build_excited_resource_summary_for_export(
    cfg: ExperimentConfig,
) -> ExcitedResourceSummary | None:
    if not excited_any_after_variational(cfg):
        return None
    er: ExcitedResourceSummary = {}
    if excited_vqd_after_variational(cfg):
        er["vqd"] = _vqd_resource_block(cfg)
    if excited_qse_after_variational(cfg):
        er["qse"] = _qse_resource_block_from_config(cfg)
    if excited_sceom_after_variational(cfg):
        er["sceom"] = _sceom_resource_block(cfg)
    return _finalize_excited_resource_summary(er)


def build_excited_resource_summary(
    cfg: ExperimentConfig,
    out: dict[str, Any],
) -> ExcitedResourceSummary | None:
    if not excited_any_after_variational(cfg):
        return None
    er: ExcitedResourceSummary = {}
    if excited_vqd_after_variational(cfg):
        er["vqd"] = _vqd_resource_block(cfg)
    qse_kw = excited_qse_plugin_params(cfg)
    if excited_qse_after_variational(cfg) and "qse" in out:
        meta = out["qse"].get("meta") or {}
        block: QseResourceBlock = {"shot_mode": str(qse_kw["shot_mode"])}
        k_val = meta.get("K")
        if isinstance(k_val, int):
            block["K"] = k_val
        sched = meta.get("qse_pauli_transition_schedule")
        if isinstance(sched, dict):
            ntt = sched.get("n_transition_tasks")
            if isinstance(ntt, int):
                block["n_transition_tasks"] = ntt
            tsb = sched.get("total_shots_upper_bound")
            if isinstance(tsb, int):
                block["total_shots_upper_bound"] = tsb
            npt = sched.get("n_pauli_terms")
            if isinstance(npt, int):
                block["n_pauli_terms_in_schedule"] = npt
        if qse_kw["shot_mode"] == "gaussian_h":
            k = meta.get("K")
            if isinstance(k, int) and k > 0:
                block["h_matrix_elements"] = k * k
                block["gaussian_h_shots_budget_reference"] = (
                    k * k * int(qse_kw["shots_per_matrix_element"])
                )
        if qse_kw["shot_mode"] == "pauli_transitions":
            block["shots_per_ij_term_yaml"] = qse_kw["shots_per_ij_term"]
        er["qse"] = cast("QseResourceBlock", {k2: v for k2, v in block.items() if v is not None})
    if excited_sceom_after_variational(cfg):
        er["sceom"] = _sceom_resource_block(cfg)
    return _finalize_excited_resource_summary(er)


def vqd_channel_upper(v: VqdResourceBlock) -> int:
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


def qse_channel_upper(qs: QseResourceBlock) -> int:
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


def sceom_channel_upper(sc: SceomResourceBlock) -> int:
    m = int(sc.get("m_matrix_elements") or 0)
    sp = int(sc.get("shots_per_matrix_element_yaml") or 0)
    if m > 0 and sp > 0:
        return m * sp
    return 0


def excited_shot_channel_upper_bounds(excited: ExcitedResourceSummary) -> ExcitedShotChannelBounds:
    out: ExcitedShotChannelBounds = {"vqd": 0, "qse": 0, "sceom": 0, "combined": 0}
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


def excited_shots_upper_bound(excited: ExcitedResourceSummary) -> int:
    b = excited_shot_channel_upper_bounds(excited)
    return int(b["combined"])


def excited_methods_unified(excited_rs: ExcitedResourceSummary) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "vqd": excited_rs.get("vqd"),
        "qse": excited_rs.get("qse"),
        "sceom": excited_rs.get("sceom"),
        "shot_channel_upper_bounds": excited_rs.get("shot_channel_upper_bounds"),
    }
