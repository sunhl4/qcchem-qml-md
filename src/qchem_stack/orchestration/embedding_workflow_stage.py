"""Post-variational embedding workflow audit stage (does not rebuild main qh)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from qchem_stack.config.embedding_enums import EmbeddingMode
from qchem_stack.orchestration.embedding_strategies import (
    DmetStrategy,
    EmbeddingStrategy,
    NoneStrategy,
    PluginStrategy,
    ProjectionStrategy,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer


_STRATEGIES: dict[EmbeddingMode, EmbeddingStrategy] = cast(
    "dict[EmbeddingMode, EmbeddingStrategy]",
    {
        EmbeddingMode.DMET: DmetStrategy(),
        EmbeddingMode.PROJECTION: ProjectionStrategy(),
        EmbeddingMode.PLUGIN: PluginStrategy(),
        EmbeddingMode.NONE: NoneStrategy(),
    },
)


def apply_embedding_workflow_stage(
    cfg: ExperimentConfig,
    *,
    out: dict[str, object],
    qh: QubitHamiltonian,
    exe: object,
    embedding_input_payload: dict[str, object] | None,
    schmidt_ctx: dict[str, object] | None,
    rhf: ClassicalMeanFieldReference,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> None:
    strategy = _STRATEGIES.get(cfg.embedding.mode, NoneStrategy())
    strategy.apply(
        cfg,
        out=out,
        qh=qh,
        exe=exe,
        embedding_input_payload=embedding_input_payload,
        schmidt_ctx=schmidt_ctx,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=emit,
    )
