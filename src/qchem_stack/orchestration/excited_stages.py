"""Excited-state stages (VQD / QSE / SCEOM) after variational ground state."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.orchestration.excited_stages_resource import (
    build_excited_resource_summary,
    build_excited_resource_summary_for_export,
    excited_methods_unified,
    excited_protocol_contract_v1_block,
    excited_shot_channel_upper_bounds,
    excited_shots_upper_bound,
)
from qchem_stack.quantum.excited_plugins.registry import run_excited_stages_from_context
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.pre_quantum_input import PreQuantumInput
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
    pre_quantum_input: PreQuantumInput | None = None,
) -> ExcitedResourceSummary | None:
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=int(cfg.random_seed),
        ground_angles=np.asarray(angles, dtype=float),
        ground_energy=float(energy_pre),
        pre_quantum_input=pre_quantum_input,
    )
    run_excited_stages_from_context(ctx, out=out)
    excited_rs = build_excited_resource_summary(cfg, out)
    if excited_rs is not None:
        out["excited_resource_summary"] = excited_rs
    profile.mark("excited_stages")
    emit("excited_stages")
    return excited_rs
