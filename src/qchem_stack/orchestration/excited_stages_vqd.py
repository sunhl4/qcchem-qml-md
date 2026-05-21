"""VQD excited-state stage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.contracts.schema_ids import EXCITED_VQD_BUNDLE_V1
from qchem_stack.quantum.algorithms.excited import VQD

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.excited_stages_types import VqdPipelineBundle


def run_vqd_stage(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    exe: HamiltonianExpectationExecutor,
    angles: np.ndarray,
    energy_pre: float,
    out: dict[str, Any],
) -> None:
    q = cfg.quantum
    prepare_state = None
    n_vp: int | None = None
    param_bounds: list[tuple[float, float]] | None = None
    if q.variational.ansatz == "uccsd":
        from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

        if q.variational.uccsd_trotter_steps is not None:
            ucc = UCCSDTrotterVQE(
                qh,
                executor=exe,
                n_trotter_steps=int(q.variational.uccsd_trotter_steps),
            )
        else:
            ucc = UCCSDVQE(qh, executor=exe)
        prepare_state = ucc.prepare_state
        n_vp = int(ucc.n_params)
        param_bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * n_vp
    vqd = VQD(
        qh,
        n_states=q.excited.vqd.n_states,
        depth=q.vqe.depth,
        penalty_weight=q.excited.vqd.penalty_weight,
        penalty_weights=q.excited.vqd.penalty_weights,
        overlap_exponent=q.excited.vqd.overlap_exponent,
        cobyla_maxiter=q.excited.vqd.cobyla_maxiter,
        optimizer_method=q.excited.vqd.optimizer_method,
        prepare_state=prepare_state,
        n_var_parameters=n_vp,
        parameter_bounds=param_bounds,
        init_strategy=q.excited.vqd.init_strategy,
        init_noise_scale=q.excited.vqd.init_noise_scale,
        max_overlap_warn=q.excited.vqd.max_overlap_warn,
        overlap_mode=q.excited.vqd.overlap_mode,
        executor=exe,
    )
    vqd_res = vqd.run(
        seed=cfg.random_seed,
        shots_objective=q.excited.vqd.shots_objective,
        shots_overlap=q.excited.vqd.shots_overlap,
        shots_weight=q.excited.vqd.shots_weight,
        pauli_grouping=q.pauli.grouping,
        ground_angles=angles,
        ground_energy=float(energy_pre),
    )
    bundle: VqdPipelineBundle = {
        "schema": EXCITED_VQD_BUNDLE_V1,
        "energies": vqd_res.energies,
        "meta": vqd_res.meta,
    }
    out["vqd"] = bundle
