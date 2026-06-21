"""Excited-stage resource summaries and shot upper-bound accounting (pipeline runs)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from qchem_stack.config.quantum_helpers import (
    excited_any_after_variational,
    excited_qse_after_variational,
    excited_qse_plugin_params,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
)
from qchem_stack.contracts.excited_resource_types import ExcitedResourceSummary, QseResourceBlock
from qchem_stack.protocols.excited_resource_export import (
    _finalize_excited_resource_summary,
    _sceom_resource_block,
    _vqd_resource_block,
    build_excited_resource_summary_for_export,
    excited_methods_unified,
    excited_protocol_contract_v1_block,
    excited_shot_channel_upper_bounds,
    qse_channel_upper,
    sceom_channel_upper,
    vqd_channel_upper,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig

__all__ = [
    "build_excited_resource_summary",
    "build_excited_resource_summary_for_export",
    "excited_methods_unified",
    "excited_protocol_contract_v1_block",
    "excited_shot_channel_upper_bounds",
    "excited_shots_upper_bound",
    "qse_channel_upper",
    "sceom_channel_upper",
    "vqd_channel_upper",
]


def build_excited_resource_summary(
    cfg: ExperimentConfig,
    out: dict[str, object],
) -> ExcitedResourceSummary | None:
    if not excited_any_after_variational(cfg):
        return None
    er: ExcitedResourceSummary = {}
    if excited_vqd_after_variational(cfg):
        er["vqd"] = _vqd_resource_block(cfg)
    qse_kw = excited_qse_plugin_params(cfg)
    qse_out = out.get("qse")
    if excited_qse_after_variational(cfg) and isinstance(qse_out, dict):
        meta_raw = qse_out.get("meta")
        meta: dict[str, object] = meta_raw if isinstance(meta_raw, dict) else {}
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
        sceom_block = _sceom_resource_block(cfg)
        meta: dict[str, object] = {}
        if "sceom" in out:
            sceom_out = out["sceom"]
            if isinstance(sceom_out, dict):
                meta_raw = sceom_out.get("meta")
                meta = meta_raw if isinstance(meta_raw, dict) else {}
            tasks = meta.get("sceom_m_element_tasks")
            if isinstance(tasks, dict):
                sceom_block["sceom_m_element_tasks"] = {
                    k: tasks[k]
                    for k in (
                        "n_generators",
                        "n_matrix_elements",
                        "n_tasks_total",
                        "shots_per_matrix_element",
                    )
                    if k in tasks
                }
        er["sceom"] = sceom_block
    return _finalize_excited_resource_summary(er)


def excited_shots_upper_bound(excited: ExcitedResourceSummary) -> int:
    b = excited_shot_channel_upper_bounds(excited)
    return int(b["combined"])
