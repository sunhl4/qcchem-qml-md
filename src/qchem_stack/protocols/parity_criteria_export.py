"""Config-only and run-merged parity / Methods export (stable integrator API)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.resource_estimation_preview import (
    build_resource_estimation_preview_v1,
)
from qchem_stack.protocols.parity_export_config import (
    register_parity_export_solvers,
    table_from_config,
)
from qchem_stack.protocols.parity_export_merge import (
    _merge_pipeline_results,
    _truncate_pauli_support_for_export,
)
from qchem_stack.protocols.parity_export_stable_keys import _assert_parity_export_v3_stable_keys
from qchem_stack.protocols.parity_export_types import ParityExportV3Document, as_parity_export_v3

__all__ = [
    "export_parity_criteria_table",
    "register_parity_export_solvers",
    "table_from_config",
]


def export_parity_criteria_table(
    config_path: str | Path,
    *,
    results_path: str | Path | None = None,
    max_pauli_export: int | None = None,
    register_solvers: bool = True,
) -> ParityExportV3Document:
    """Export Methods-style parity table (config-only or merged with pipeline JSON)."""
    if register_solvers:
        register_parity_export_solvers()
    path = Path(config_path)
    proto_pc: dict[str, Any] | None = None
    pipeline_data: dict[str, Any] | None = None
    if results_path is not None:
        results_file = Path(results_path)
        if results_file.is_file():
            raw = json.loads(results_file.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                pipeline_data = raw
                pc0 = raw.get("protocol_counts")
                if isinstance(pc0, dict):
                    proto_pc = pc0
    out = table_from_config(path, protocol_counts=proto_pc)
    if pipeline_data is not None:
        _merge_pipeline_results(out, config_path=path, data=pipeline_data)
    cfg_final = load_experiment_config(path)
    if cfg_final.parity_integrations.resource_estimation_preview:
        out["resource_estimation_preview_v1"] = build_resource_estimation_preview_v1(
            cfg=cfg_final, pipeline_row=pipeline_data
        )
    _truncate_pauli_support_for_export(out, max_pauli=max_pauli_export)
    _assert_parity_export_v3_stable_keys(out)
    return as_parity_export_v3(out)


_table_from_config = table_from_config
