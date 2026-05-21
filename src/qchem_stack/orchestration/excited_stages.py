"""Excited-state stages (VQD / QSE / SCEOM) after variational ground state."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.orchestration.excited_stages_qse import run_qse_stage
from qchem_stack.orchestration.excited_stages_resource import (
    build_excited_resource_summary,
    build_excited_resource_summary_for_export,
    excited_methods_unified,
    excited_protocol_contract_v1_block,
    excited_shot_channel_upper_bounds,
    excited_shots_upper_bound,
)
from qchem_stack.orchestration.excited_stages_sceom import run_sceom_stage
from qchem_stack.orchestration.excited_stages_vqd import run_vqd_stage

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.excited_stages_types import ExcitedResourceSummary
    from qchem_stack.orchestration.run_context import PipelineStageTimer

__all__ = [
    "build_excited_resource_summary",
    "build_excited_resource_summary_for_export",
    "excited_methods_unified",
    "excited_protocol_contract_v1_block",
    "excited_shot_channel_upper_bounds",
    "excited_shots_upper_bound",
    "run_excited_stages",
]


def run_excited_stages(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    exe: HamiltonianExpectationExecutor,
    angles: np.ndarray,
    energy_pre: float,
    out: dict[str, Any],
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> ExcitedResourceSummary | None:
    q = cfg.quantum
    ang = np.asarray(angles, dtype=float)
    if q.excited.vqd.after_variational:
        run_vqd_stage(cfg, qh=qh, exe=exe, angles=ang, energy_pre=energy_pre, out=out)
    if q.excited.qse.after_variational:
        run_qse_stage(cfg, qh=qh, angles=ang, out=out)
    if q.excited.sceom.after_variational:
        run_sceom_stage(cfg, qh=qh, angles=ang, out=out)
    excited_rs = build_excited_resource_summary(cfg, out)
    if excited_rs is not None:
        out["excited_resource_summary"] = excited_rs
    profile.mark("excited_stages")
    emit("excited_stages")
    return excited_rs
