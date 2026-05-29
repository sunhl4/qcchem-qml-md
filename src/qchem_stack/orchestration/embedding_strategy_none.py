"""No-op embedding workflow strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from qchem_stack.contracts.schema_ids import EMBEDDING_WORKFLOW_V1

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer


class NoneStrategy:
    """Strategy for no embedding workflow."""

    def apply(
        self,
        cfg: ExperimentConfig,
        *,
        out: dict[str, Any],
        qh: QubitHamiltonian,
        exe: Any,
        embedding_input_payload: dict[str, Any] | None,
        schmidt_ctx: dict[str, Any] | None,
        rhf: ClassicalMeanFieldReference,
        cfg_path: Path | None,
        profile: PipelineStageTimer,
        emit: Callable[[str], None],
    ) -> None:
        out["embedding_workflow"] = {
            "schema": EMBEDDING_WORKFLOW_V1,
            "mode": "none",
            "stage_timing": "post_variational",
            "note": "No DMET/projection embedding stage; variational Hamiltonian uses global active space.",
        }
        if embedding_input_payload is not None:
            cast("dict[str, Any]", out["embedding_workflow"])["embedding_input_system"] = (
                embedding_input_payload
            )
        profile.mark("embedding_none")
        emit("embedding_none")
