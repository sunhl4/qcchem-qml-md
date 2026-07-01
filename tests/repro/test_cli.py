"""Tests for ``qchem-run`` and ``qchem-export-parity`` console scripts."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.no_pyscf
def test_qchem_run_precomputed_subprocess() -> None:
    cfg = ROOT / "configs" / "example_h2_precomputed_bundle.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "qchem_stack.cli",
            str(cfg),
            "--json-summary",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env={**__import__("os").environ, "PYTHONPATH": f"{ROOT / 'src'}:{ROOT}"},
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data.get("scf_energy") is not None


def test_qchem_export_parity_config_only() -> None:
    cfg = ROOT / "configs" / "example_h2.yaml"
    from qchem_stack.cli import main_export_parity

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main_export_parity([str(cfg)])
    assert rc == 0
    out = json.loads(buf.getvalue())
    assert out.get("parity_export_schema_version") == "3"
    assert out.get("experiment_id")


def test_qchem_run_list_scenarios() -> None:
    from qchem_stack.cli import main_run

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main_run(["--list-scenarios"])
    assert rc == 0
    text = buf.getvalue()
    assert "minimal_vqe" in text
    assert "configs/scenarios/minimal_vqe.yaml" in text


def test_qchem_run_scenario_resolves_config() -> None:
    from qchem_stack.config.scenarios import scenario_config_path

    path = scenario_config_path("minimal_vqe", configs_dir=ROOT / "configs")
    assert path.name == "minimal_vqe.yaml"
    assert path.is_file()


def test_qchem_run_unknown_scenario() -> None:
    from qchem_stack.cli import main_run

    rc = main_run(["--scenario", "not_a_real_scenario"])
    assert rc == 2
