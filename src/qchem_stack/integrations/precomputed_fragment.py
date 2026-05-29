"""MI-FNO / precomputed fragment input sidecar (P4-C2 / A-15 plugin hook)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_precomputed_fragment_sidecar(path: str | Path) -> dict[str, Any]:
    """Load JSON sidecar with incremental fragment energies / inputs."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("precomputed fragment sidecar must be a JSON object")
    data.setdefault("schema", "precomputed_fragment_input_v1")
    return data


def merge_precomputed_fragment_into_workflow(
    workflow: dict[str, Any],
    sidecar: dict[str, Any],
) -> dict[str, Any]:
    """Attach sidecar metadata to an embedding workflow dict."""
    out = dict(workflow)
    out["precomputed_fragment_sidecar_v1"] = sidecar
    out["mi_fno_plugin_status"] = sidecar.get("status", "input_only")
    return out
