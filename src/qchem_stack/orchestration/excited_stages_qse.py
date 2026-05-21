"""QSE excited-state stage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import EXCITED_QSE_BUNDLE_V1
from qchem_stack.quantum.algorithms.excited import QSE

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.excited_stages_types import QsePipelineBundle


def run_qse_stage(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    angles: np.ndarray,
    out: dict[str, Any],
) -> None:
    q = cfg.quantum
    qse = QSE(qh, subspace_dim=q.excited.qse.subspace_dim)
    kb = q.excited.qse.max_basis
    if q.excited.qse.shot_mode == "exact":
        qse_res = qse.run_from_vqe_hea_basis(angles, q.vqe.depth, max_basis=kb)
    elif q.excited.qse.shot_mode == "gaussian_h":
        qse_res = qse.run_from_vqe_hea_basis_shot_noise(
            angles,
            q.vqe.depth,
            max_basis=kb,
            shots_per_matrix_element=q.excited.qse.shots_per_matrix_element,
            seed=cfg.random_seed,
        )
    else:
        qse_res = qse.run_from_vqe_hea_basis_pauli_transitions(
            angles,
            q.vqe.depth,
            max_basis=kb,
            shots_per_ij_term=q.excited.qse.shots_per_ij_term,
            seed=cfg.random_seed,
        )
    qse_meta = dict(qse_res.meta)
    qse_meta["qse_shot_mode"] = q.excited.qse.shot_mode
    bundle: QsePipelineBundle = {
        "schema": EXCITED_QSE_BUNDLE_V1,
        "excitation_energies": qse_res.excitation_energies,
        "meta": qse_meta,
    }
    out["qse"] = bundle
