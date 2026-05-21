"""SCEOM excited-state stage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import EXCITED_SCEOM_BUNDLE_V1

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.excited_stages_types import SceomPipelineBundle


def run_sceom_stage(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    angles: np.ndarray,
    out: dict[str, Any],
) -> None:
    from qchem_stack.quantum.algorithms.sceom import (
        resolve_sceom_s_generators,
        run_sceom_nested_commutator_from_hea,
    )

    q = cfg.quantum
    sceom_kw: dict[str, Any] = {}
    gens, _ = resolve_sceom_s_generators(
        strategy=q.excited.sceom.generator_strategy,
        hamiltonian=qh,
        subspace_dim=q.excited.sceom.subspace_dim,
    )
    if gens is not None:
        sceom_kw["s_generators"] = gens
    sceom_kw["generator_strategy_yaml"] = q.excited.sceom.generator_strategy
    sceom_res = run_sceom_nested_commutator_from_hea(
        qh,
        angles,
        q.vqe.depth,
        subspace_dim=q.excited.sceom.subspace_dim,
        shots_per_matrix_element=q.excited.sceom.shots_per_matrix_element,
        seed=cfg.random_seed,
        **sceom_kw,
    )
    bundle: SceomPipelineBundle = {
        "schema": EXCITED_SCEOM_BUNDLE_V1,
        "energies": sceom_res.energies,
        "meta": sceom_res.meta,
    }
    out["sceom"] = bundle
