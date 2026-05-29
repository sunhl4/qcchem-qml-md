"""C-13: md_ml_repro_freeze_fields_v1 in parity export (config-only gate)."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.helpers.paths import repo_root, scripts_path

_ROOT = repo_root()


def _export(cfg_rel: str) -> dict:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    proc = subprocess.run(
        [
            sys.executable,
            str(scripts_path("export_parity_criteria_table.py")),
            str(_ROOT / cfg_rel),
        ],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def test_md_ml_repro_freeze_fields_on_resource_preview_config() -> None:
    exp = _export("configs/example_h2_qpe_track_parity_integrations.yaml")
    block = exp.get("md_ml_repro_freeze_fields_v1")
    assert isinstance(block, dict)
    assert block.get("schema") == "md_ml_repro_freeze_fields_v1"
    assert "qmframe_fields" in block
