"""Embedding workflow strategy protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer


@runtime_checkable
class EmbeddingStrategy(Protocol):
    """Protocol for embedding workflow strategies."""

    def apply(
        self,
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
        """Apply the embedding workflow strategy."""
        ...
