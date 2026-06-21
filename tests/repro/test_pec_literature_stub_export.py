"""PEC literature stub parity / run_summary export."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from qchem_stack.config import load_experiment_config
from qchem_stack.config.mitigation_helpers import build_mitigation_pec_literature_stub_v1
from qchem_stack.contracts.schema_ids import MITIGATION_PEC_LITERATURE_STUB_V1
from tests.helpers.paths import configs_path, scripts_path

_ROOT = Path(__file__).resolve().parents[1]


def test_pec_stub_builder_schema() -> None:
    stub = build_mitigation_pec_literature_stub_v1()
    assert stub["schema"] == MITIGATION_PEC_LITERATURE_STUB_V1


def test_pec_config_loads_yaml_flag() -> None:
    cfg = load_experiment_config(configs_path("example_h2_pec_literature_stub.yaml"))
    assert cfg.mitigation.stubs.pec_literature is True


def test_pec_export_config_only_has_mitigation_in_parity_snapshot() -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    cfg = configs_path("example_h2_pec_literature_stub.yaml")
    proc = subprocess.run(
        [sys.executable, str(scripts_path("export_parity_criteria_table.py")), str(cfg)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    exp = json.loads(proc.stdout)
    stub = exp.get("mitigation_pec_literature_stub_v1")
    assert isinstance(stub, dict)
    assert stub.get("schema") == MITIGATION_PEC_LITERATURE_STUB_V1
