"""Typed shapes for excited-state basis / VQD helper exports."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class VqdObjectiveChannelV1(TypedDict):
    energy_exact: float
    shots_budget_objective: int
    energy_shot_mean: NotRequired[float]
    energy_shot_stderr: NotRequired[float]


class VqdOverlapChannelV1(TypedDict):
    overlap_squared_sum_exact: float
    shots_per_pair: int
    overlap_squared_sum_shot_mean: NotRequired[float]
    overlap_squared_sum_shot_stderr: NotRequired[float]


class VqdWeightChannelV1(TypedDict):
    penalty_weight: float
    weight_exact: float
    shots_budget_weight: int
    weight_shot_mean: NotRequired[float]
    weight_shot_stderr: NotRequired[float]


class VqdThreeProtocolChannelsV1(TypedDict):
    objective: VqdObjectiveChannelV1
    overlap: VqdOverlapChannelV1
    weight: VqdWeightChannelV1


class CircuitIrOperationV1(TypedDict):
    name: str
    qubits: list[int]
    params: dict[str, Any]


class VqdDeflationSwapTestCircuitSketchV1(TypedDict):
    schema: str
    n_qubits: int
    n_system_qubits: int
    ancilla_qubit: int
    reference_qubits: list[int]
    trial_qubits: list[int]
    operations: list[CircuitIrOperationV1]
    boxes: list[str]
    note: str


class VqdDeflationCircuitSketchV1(TypedDict, total=False):
    schema: str
    n_system_qubits: int
    circuit_ir: dict[str, Any]


class TangeloDeflationAnalogyV1(TypedDict, total=False):
    schema: str
    deflation_coeff_yaml: float
    penalty_schedule_resolved: list[float]
    selected_overlap_mode: str
    open_stack_overlap_representation: str
    deflation_circuits_analogy: str
    deflation_circuit_recipe_v1: dict[str, Any]


class VqdCrossStackSemanticsMetaV1(TypedDict, total=False):
    schema: str
    optimization_model: str
    three_protocol_role: str
    note: str


class VqdCrossStackSemanticsBundleV1(TypedDict, total=False):
    tangelo_deflation_analogy_v1: TangeloDeflationAnalogyV1
    vqd_cross_stack_semantics_v1: VqdCrossStackSemanticsMetaV1


class VqdCrossStackSemanticsV1(TypedDict, total=False):
    schema: str
    overlap_mode: str
    optimizer_mode: str
    deflation_analogy: dict[str, Any]
    three_protocol: dict[str, Any]
