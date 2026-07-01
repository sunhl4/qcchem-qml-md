"""
Thin workflow coordinator over :func:`run_pipeline_from_config`.

Adds a ``methods_sidecar`` blob with :func:`~qchem_stack.protocols.computable.computables_export_dict`
and ``hamiltonian_fingerprint`` when present in pipeline output.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_from_config
from qchem_stack.protocols.computable import computables_export_dict
from qchem_stack.protocols.workflow_preview import workflow_preview_payload

if TYPE_CHECKING:
    from qchem_stack.orchestration.pipeline_result import PipelineResultV1


class WorkflowCoordinator:
    """Load YAML once, run full pipeline, attach Methods-oriented side metadata."""

    def __init__(self, config_path: str | Path, *, job_db: Path | None = None) -> None:
        self.config_path = Path(config_path)
        self.job_db = job_db
        self._cfg = load_experiment_config(self.config_path)

    @property
    def config(self) -> ExperimentConfig:
        return self._cfg

    def run(self) -> PipelineResultV1:
        out = run_pipeline_from_config(self.config_path, job_db=self.job_db)
        pc = out.get("protocol_counts") if isinstance(out.get("protocol_counts"), dict) else None
        side: dict[str, object] = {
            "computable_abstract": computables_export_dict(self._cfg, protocol_counts=pc),
            "workflow_preview_v1": workflow_preview_payload(self._cfg),
            "hamiltonian_fingerprint": None,
        }
        hm = out.get("hamiltonian_meta")
        if isinstance(hm, dict) and hm.get("hamiltonian_fingerprint") is not None:
            side["hamiltonian_fingerprint"] = hm.get("hamiltonian_fingerprint")
        out["methods_sidecar"] = side
        return out
