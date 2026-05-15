from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.config import ExperimentConfig
from qchem_stack.orchestration.run_context import PipelineStageTimer


@dataclass(slots=True)
class ScfStageArtifacts:
    cfg: ExperimentConfig
    rhf: ClassicalMeanFieldReference
    precomputed_mode: bool
    solver_caps: Any
    energy_components: dict[str, Any]
    embedding_input_payload: dict[str, Any] | None
    classical_benchmarks: dict[str, Any] | None
    rdm_bundle_meta: dict[str, Any] | None
    rdm_correction_report: dict[str, Any] | None
    rdm_correction_readiness: dict[str, Any] | None


@dataclass(slots=True)
class PreQuantumStageArtifacts:
    pre_quantum_input: PreQuantumInput
    schmidt_ctx: dict[str, Any] | None
    qh: Any


def mark_stage_done(
    *,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
    logger: logging.Logger,
    stage: str,
    experiment_id: str,
    extra_message: str,
) -> None:
    profile.mark(stage)
    emit(stage)
    logger.info("pipeline %s experiment_id=%s %s", stage, experiment_id, extra_message)
