"""Typed shapes for excited-stage resource summaries and pipeline outputs."""

from __future__ import annotations

from typing import Any, TypedDict


class ExcitedProtocolContractV1(TypedDict):
    schema: str
    vqd_three_protocol: str
    qse_shot_modes: dict[str, str]
    sceom_shot_semantics: str


class VqdResourceBlock(TypedDict, total=False):
    n_states: int
    shots_objective_per_reporting_level: int
    shots_overlap_per_pair: int
    shots_weight_channel: int
    deflated_cobyla_levels: int
    swap_test_pair_count_if_shots: int


class QseResourceBlock(TypedDict, total=False):
    shot_mode: str
    K: int
    n_transition_tasks: int
    total_shots_upper_bound: int
    n_pauli_terms_in_schedule: int
    h_matrix_elements: int
    gaussian_h_shots_budget_reference: int
    shots_per_ij_term_yaml: int
    qse_shots_per_matrix_element_yaml: int


class SceomResourceBlock(TypedDict, total=False):
    generator_count_k: int
    m_matrix_elements: int
    shots_per_matrix_element_yaml: int
    sceom_m_element_tasks: dict[str, int]


class ExcitedShotChannelBounds(TypedDict):
    vqd: int
    qse: int
    sceom: int
    combined: int


class ExcitedResourceSummary(TypedDict, total=False):
    vqd: VqdResourceBlock
    qse: QseResourceBlock
    sceom: SceomResourceBlock
    shot_channel_upper_bounds: ExcitedShotChannelBounds
    excited_methods_unified: dict[str, Any]
    excited_protocol_contract_v1: ExcitedProtocolContractV1


class VqdPipelineBundle(TypedDict):
    schema: str
    energies: list[float]
    meta: dict[str, Any]


class QsePipelineBundle(TypedDict):
    schema: str
    excitation_energies: list[float]
    meta: dict[str, Any]


class SceomPipelineBundle(TypedDict):
    schema: str
    energies: list[float]
    meta: dict[str, Any]
